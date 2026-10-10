"""Exercise the native service across durable storage, HTTP, MCP, SMTP, and DNS."""

import asyncio
import base64
import hashlib
import hmac
import json
import smtplib
import socket
import struct
import time

import pytest
from dnslib import DNSRecord, RCODE
from starlette.testclient import TestClient

from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.web import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(database=str(tmp_path / "events.sqlite3"), origin="http://testserver")


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


def call(client, action, **values):
    response = client.post("/api/call", json={"action": action, **values})
    assert response.status_code == 200, response.text
    return response.json()["data"]


def test_own_urls_and_private_read_access(client):
    inbox = call(client, "create")
    assert inbox["url"].startswith("http://testserver/h/")
    assert inbox["token"].startswith("ohk_")
    assert inbox["inbox_id"] not in inbox["token"]
    assert inbox["email"] is None and inbox["dns"] is None
    response = client.post(inbox["url"], content=b'{"hello":"world"}', headers={"content-type": "application/json"})
    assert response.status_code == 200
    event = call(client, "get", token=inbox["token"])["request"]
    assert event["content"] == '{"hello":"world"}'
    assert base64.b64decode(event["body_base64"]) == b'{"hello":"world"}'
    for value in [inbox["url"], inbox["inbox_id"], "ohk_wrong"]:
        assert client.post("/api/call", json={"action": "list", "token": value}).status_code in (401, 404)


def test_persistence_and_key_hash_at_rest(settings):
    store = Store(settings)
    inbox = store.create()
    event = store.capture(inbox["inbox_id"], b"persistent")
    reopened = Store(settings)
    assert reopened.request(inbox["token"], event["uuid"])["request"]["content"] == "persistent"
    with reopened.connection() as db:
        row = dict(db.execute("SELECT * FROM inboxes").fetchone())
    assert inbox["token"] not in json.dumps(row)


def test_cross_inbox_isolation_rotation_and_delete(client):
    first, second = call(client, "create"), call(client, "create")
    client.post(first["url"], content=b"private")
    event = call(client, "list", token=first["token"])["requests"][0]
    assert client.post("/api/call", json={"action": "get", "token": second["token"], "request_id": event["uuid"]}).status_code == 404
    rotated = call(client, "rotate", token=first["token"])
    assert rotated["url"] == first["url"]
    assert client.post("/api/call", json={"action": "info", "token": first["token"]}).status_code == 404
    assert call(client, "list", token=rotated["token"])["total_requests"] == 1
    call(client, "delete", token=rotated["token"])
    assert client.post(first["url"]).status_code == 404


def test_custom_responses_and_partial_updates(client):
    inbox = call(client, "create")
    call(client, "configure", token=inbox["token"], config={"default_status": 201, "default_content": '{"ok":true}', "default_content_type": "application/json"})
    call(client, "configure", token=inbox["token"], config={"cors": True})
    response = client.put(inbox["url"] + "/callback?run=42", content=b"payload")
    assert response.status_code == 201
    assert response.json() == {"ok": True}
    assert response.headers["access-control-allow-origin"] == "*"
    event = call(client, "list", token=inbox["token"])["requests"][0]
    assert event["query"] == {"run": ["42"]}
    assert event["method"] == "PUT"
    for config in [{"default_status": 999}, {"default_content_type": "text/html\r\nInjected: header"}, {"wrong": 1}]:
        assert client.post("/api/call", json={"action": "configure", "token": inbox["token"], "config": config}).status_code == 400


def test_signature_verified_before_capture_and_idempotency(client):
    inbox = call(client, "create")
    call(client, "configure", token=inbox["token"], config={"verification_secret": "topsecret"})
    body = b"\xffbinary"
    assert client.post(inbox["url"], content=body).status_code == 401
    assert call(client, "list", token=inbox["token"])["total_requests"] == 0
    signature = "sha256=" + hmac.new(b"topsecret", body, hashlib.sha256).hexdigest()
    headers = {"x-hub-signature-256": signature, "x-github-delivery": "delivery-42"}
    one, two = client.post(inbox["url"], content=body, headers=headers), client.post(inbox["url"], content=body, headers=headers)
    assert one.status_code == two.status_code == 200
    assert one.headers["x-openhook-event"] == two.headers["x-openhook-event"]
    assert call(client, "list", token=inbox["token"])["total_requests"] == 1
    assert "topsecret" not in json.dumps(call(client, "info", token=inbox["token"]))


def test_streamed_export_preserves_exact_bytes_and_safe_preview(client):
    inbox = call(client, "create")
    body = b"z" * 5000
    client.post(inbox["url"], content=body)
    preview = call(client, "list", token=inbox["token"])["requests"][0]
    assert preview["preview_only"] and "body_base64" not in preview
    response = client.post("/api/export", json={"token": inbox["token"]})
    assert response.status_code == 200
    event = response.json()["requests"][0]
    assert base64.b64decode(event["body_base64"]) == body
    assert event["content"] == body.decode()


def test_size_bound_origin_and_headers(client, settings):
    inbox = call(client, "create")
    assert client.post(inbox["url"], content=b"x" * (settings.body_limit + 1)).status_code == 413
    assert client.post("/api/call", json={"action": "create"}, headers={"origin": "https://evil.example"}).status_code == 403
    assert client.get("/app").headers["cache-control"] == "no-store"
    assert "frame-ancestors 'none'" in client.get("/").headers["content-security-policy"]
    assert call(client, "list", token=inbox["token"])["total_requests"] == 0


def test_retention_pagination_search_and_expiry(tmp_path):
    settings = Settings(database=str(tmp_path / "retention.sqlite3"), event_limit=3)
    store = Store(settings)
    inbox = store.create(expiry=60)
    for index in range(3):
        store.capture(inbox["inbox_id"], f"event-{index}".encode())
    with pytest.raises(InboxError, match="capacity"):
        store.capture(inbox["inbox_id"], b"must not evict an accepted event")
    assert store.requests(inbox["token"])["total_requests"] == 3
    first = store.requests(inbox["token"], limit=2)
    assert not first["pagination"]["is_last_page"]
    assert len(store.requests(inbox["token"], limit=2, page=2)["requests"]) == 1
    assert store.requests(inbox["token"], query="event-0")["total_requests"] == 1
    with store.connection(write=True) as db:
        db.execute("UPDATE inboxes SET expires=0")
    with pytest.raises(InboxError, match="expired"):
        store.info(inbox["token"])
    assert store.cleanup() == 1
    with store.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0


@pytest.mark.asyncio
async def test_wait_and_resume_cursor(settings):
    store = Store(settings)
    inbox = store.create()
    first = store.capture(inbox["inbox_id"], b"before")
    waiter = asyncio.create_task(store.wait(inbox["token"], timeout_seconds=2))
    await asyncio.sleep(0.05)
    second = Store(settings).capture(inbox["inbox_id"], b"during")
    result = await waiter
    assert result["request"]["uuid"] == second["uuid"]
    resumed = await store.wait(inbox["token"], timeout_seconds=0.02, since=first["sorting"])
    assert resumed["request"]["uuid"] == second["uuid"]
    timeout = await store.wait(inbox["token"], timeout_seconds=0.02, since=second["sorting"])
    assert timeout["timeout"] and timeout["request"] is None


def test_native_mcp_uses_same_storage(client):
    headers = {"Accept": "application/json, text/event-stream", "Content-Type": "application/json"}
    initialized = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "customer-test", "version": "1"}}})
    assert initialized.status_code == 200, initialized.text
    assert initialized.json()["result"]["serverInfo"]["name"] == "openhook"
    response = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "create_webhook", "arguments": {"name": "MCP customer"}}})
    assert response.status_code == 200, response.text
    result = response.json()["result"]
    assert not result.get("isError"), result
    inbox = json.loads(result["content"][0]["text"])
    configured = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "configure_webhook", "arguments": {"webhook_token": inbox["token"], "default_content": {"ok": True}}}})
    assert not configured.json()["result"].get("isError"), configured.text
    client.post(inbox["url"], json={"from": "mcp"})
    assert call(client, "list", token=inbox["token"])["total_requests"] == 1
    history = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "get_webhook_activity", "arguments": {"webhook_token": inbox["token"], "since": 0}}})
    result = history.json()["result"]
    assert not result.get("isError"), result
    records = json.loads(result["content"][0]["text"])["activity"]
    assert [record["action"] for record in records] == ["inbox.created", "inbox.configured", "event.received"]
    tools = client.get("/api/tools").json()["tools"]
    assert len(tools) == 27
    assert not any("webhook.site" in json.dumps(tool) for tool in tools)


def test_listener_wait_endpoint_returns_original_bytes_and_cursor(client):
    inbox = call(client, "create")
    client.post(inbox["url"], content=b"\x00\xfflocal-forward")
    result = client.post("/api/wait", json={"token": inbox["token"], "since": 0, "timeout_seconds": .01}).json()["data"]
    assert base64.b64decode(result["request"]["body_base64"]) == b"\x00\xfflocal-forward"
    resumed = client.post("/api/wait", json={"token": inbox["token"], "since": result["next_since"], "timeout_seconds": .01}).json()["data"]
    assert resumed["timeout"] and resumed["request"] is None


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def test_real_smtp_dns_udp_and_tcp(tmp_path):
    smtp_port, dns_port = free_port(), free_port()
    settings = Settings(database=str(tmp_path / "transports.sqlite3"), origin="http://testserver",
        email_domain="mail.openhook.test", dns_domain="dns.openhook.test", smtp_port=smtp_port, dns_port=dns_port)
    with TestClient(create_app(settings)) as client:
        inbox = call(client, "create")
        with smtplib.SMTP("127.0.0.1", smtp_port, timeout=3) as smtp:
            smtp.sendmail("sender@example.com", inbox["email"],
                          "From: sender@example.com\r\nSubject: Native email\r\n\r\nCode 123456 https://example.com/confirm")
            with pytest.raises(smtplib.SMTPRecipientsRefused):
                smtp.sendmail("sender@example.com", "stranger@elsewhere.test", "No relay")
        query = DNSRecord.question("callback." + inbox["dns"])
        udp_reply = DNSRecord.parse(query.send("127.0.0.1", dns_port, timeout=3))
        assert udp_reply.header.rcode == RCODE.NOERROR
        tcp_reply = DNSRecord.parse(query.send("127.0.0.1", dns_port, tcp=True, timeout=3))
        assert tcp_reply.header.rcode == RCODE.NOERROR
        refused = DNSRecord.parse(DNSRecord.question("example.com").send("127.0.0.1", dns_port, timeout=3))
        assert refused.header.rcode == RCODE.REFUSED and not refused.header.ra
        events = call(client, "list", token=inbox["token"])["requests"]
        assert sorted(event["type"] for event in events) == ["dns", "dns", "email"]
        history = call(client, "activity", token=inbox["token"])["activity"]
        assert sorted(item["details"]["type"] for item in history if item["action"] == "event.received") == ["dns", "dns", "email"]
        email = next(event for event in events if event["type"] == "email")
        assert email["subject"] == "Native email"
        links = call(client, "links", token=inbox["token"], request_id=email["uuid"])
        assert links["verification_codes"] == ["123456"]
        assert links["links"] == ["https://example.com/confirm"]
