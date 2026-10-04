import base64
import json

import httpx
import pytest

from openhook.listener import Cursor, deliver


def test_forward_preserves_raw_body_without_hop_headers():
    body = b"\x00\xfforiginal"
    def receive(request):
        assert request.content == body
        assert request.headers["x-hub-signature-256"] == "sha256=test"
        assert request.headers["host"] == "127.0.0.1:8080"
        return httpx.Response(200)
    event = {"uuid": "event-1", "type": "web", "method": "POST", "body_base64": base64.b64encode(body).decode(),
             "headers": {"host": ["public.openhook.dev"], "x-hub-signature-256": ["sha256=test"], "content-length": ["999"]}}
    with httpx.Client(transport=httpx.MockTransport(receive)) as client:
        deliver(client, event, "http://127.0.0.1:8080/webhook")


def test_delivery_failure_does_not_advance_persisted_cursor(tmp_path):
    cursor = Cursor(tmp_path, "ohk_private-test")
    cursor.save(10)
    event = {"uuid": "event-11", "type": "web", "method": "POST", "body_base64": "eA==", "headers": {}}
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as client:
        with pytest.raises(httpx.HTTPStatusError):
            deliver(client, event, "http://127.0.0.1:8080/webhook")
    assert Cursor(tmp_path, "ohk_private-test").value == 10
    assert "ohk_private-test" not in cursor.path.read_text()


def test_openclaw_receives_wakeup_payload():
    def receive(request):
        payload = json.loads(request.content)
        assert request.headers["authorization"] == "Bearer local-secret"
        assert payload["wakeMode"] == "now"
        assert payload["name"] == "Openhook"
        assert "untrusted data" in payload["message"]
        return httpx.Response(200)
    event = {"uuid": "event-1", "type": "web", "method": "POST", "url": "https://openhook.dev/h/abc", "content": "event"}
    with httpx.Client(transport=httpx.MockTransport(receive)) as client:
        deliver(client, event, "http://127.0.0.1:18789/hooks/agent", openclaw=True, hooks_token="local-secret")
