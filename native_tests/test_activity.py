"""Every accepted receipt and successful mutation has durable, private history."""

import hashlib
import json
import sqlite3
import time

import pytest
from starlette.testclient import TestClient

from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.web import create_app


def test_durable_receipts_mutations_pagination_and_secret_exclusion(tmp_path):
    settings = Settings(database=str(tmp_path / "history.sqlite3"))
    store = Store(settings)
    inbox = store.create()
    token = inbox["token"]
    events = [store.capture(inbox["inbox_id"], b"private payload", kind=kind) for kind in ("web", "email", "dns")]
    store.configure(token, {"verification_secret": "signing-secret", "cors": True})
    store.update_request(token, events[0]["uuid"], "private note")
    store.set_response(token, events[0]["uuid"], 202, "private response", "text/plain")
    store.attach_subscription(token, "github", "42", "owner/repo")
    store.detach_subscription(token)
    rotated = store.rotate(token)
    token = rotated["token"]
    store.delete_requests(token, events[1]["uuid"])
    records = Store(settings).activity(token)["activity"]
    actions = [row["action"] for row in records]
    assert actions == ["inbox.created", *(["event.received"] * 3), "inbox.configured", "event.note_updated",
                       "event.response_set", "subscription.registered", "subscription.removed", "inbox.token_rotated", "event.deleted"]
    assert [row["details"]["type"] for row in records if row["action"] == "event.received"] == ["web", "email", "dns"]
    for secret in (inbox["token"], token, "signing-secret", "private payload", "private note", "private response"):
        assert secret not in json.dumps(records)
    first = store.activity(token, limit=2)
    assert first["has_more"]
    assert store.activity(token, since=first["next_since"], limit=2)["activity"] == records[2:4]
    assert records[1]["details"]["sha256"] == hashlib.sha256(b"private payload").hexdigest()
    store.delete(token)
    with store.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0
        assert db.execute("SELECT action FROM activity ORDER BY sequence DESC LIMIT 1").fetchone()[0] == "inbox.deleted"
        assert db.execute("SELECT COUNT(*) FROM activity WHERE action='event.deleted'").fetchone()[0] == 3


def test_audit_failure_rolls_back_the_mutation(tmp_path):
    store = Store(Settings(database=str(tmp_path / "atomic.sqlite3")))
    inbox = store.create()
    with store.connection() as db:
        db.execute("CREATE TRIGGER fail_history BEFORE INSERT ON activity BEGIN SELECT RAISE(ABORT,'history failed'); END")
    with pytest.raises(sqlite3.IntegrityError, match="history failed"):
        store.configure(inbox["token"], {"cors": True})
    assert store.info(inbox["token"])["cors"] is False
    with pytest.raises(sqlite3.IntegrityError):
        store.capture(inbox["inbox_id"], b"not acknowledged")
    assert store.requests(inbox["token"])["total_requests"] == 0


def test_duplicate_receipts_capacity_and_expiry_history(tmp_path):
    settings = Settings(database=str(tmp_path / "expiry.sqlite3"), event_limit=1)
    store = Store(settings)
    inbox = store.create()
    first = store.capture(inbox["inbox_id"], b"keep this", source_id="same")
    duplicate = store.capture(inbox["inbox_id"], b"keep this", source_id="same")
    assert duplicate["duplicate"] and duplicate["uuid"] == first["uuid"]
    with pytest.raises(InboxError, match="capacity") as exc:
        store.capture(inbox["inbox_id"], b"would silently evict the first event")
    assert exc.value.status == 429
    assert store.request(inbox["token"])["request"]["content"] == "keep this"
    assert [row["action"] for row in store.activity(inbox["token"])["activity"]] == ["inbox.created", "event.received", "event.duplicate_received"]
    with store.connection() as db:
        db.execute("UPDATE inboxes SET expires=?", (time.time() - 1,))
    assert store.cleanup() == 1
    assert store.cleanup() == 0
    reopened = Store(settings)
    with reopened.connection() as db:
        assert [row[0] for row in db.execute("SELECT action FROM activity ORDER BY sequence")] == [
            "inbox.created", "event.received", "event.duplicate_received", "event.expired", "inbox.expired"]


def test_legacy_import_is_idempotent_and_history_is_private(tmp_path):
    settings = Settings(database=str(tmp_path / "legacy.sqlite3"), origin="http://testserver")
    store = Store(settings)
    inbox = store.create()
    event = store.capture(inbox["inbox_id"], b"existing")
    with store.connection() as db:
        db.execute("DROP TABLE activity")
    store = Store(settings)
    assert store.request(inbox["token"], event["uuid"])["request"]["content"] == "existing"
    assert [row["action"] for row in Store(settings).activity(inbox["token"])["activity"]] == ["inbox.imported", "event.imported"]
    with TestClient(create_app(settings)) as client:
        second = client.post("/api/call", json={"action": "create"}).json()["data"]
        history = client.post("/api/call", json={"action": "activity", "token": second["token"]}).json()["data"]["activity"]
        assert len(history) == 1 and history[0]["inbox_id"] == second["inbox_id"]
        for value in (inbox["url"], inbox["inbox_id"], "ohk_invalid"):
            assert client.post("/api/call", json={"action": "activity", "token": value}).status_code in (401, 404)
