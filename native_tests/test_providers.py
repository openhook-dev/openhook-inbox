"""Provider credentials remain transient; every callback is verified natively."""

import hashlib
import hmac
import json
import time

import httpx
import pytest
import respx
from starlette.testclient import TestClient

from openhook.providers import register, remove
from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.web import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(database=str(tmp_path / "providers.sqlite3"), origin="https://inboxes.openhook.test")


@pytest.mark.asyncio
async def test_github_registration_verification_and_cleanup(settings):
    store = Store(settings)
    secret = None
    def created(request):
        nonlocal secret
        payload = json.loads(request.content)
        assert payload["config"]["url"].startswith(settings.origin + "/h/")
        assert payload["events"] == ["push"]
        secret = payload["config"]["secret"]
        return httpx.Response(201, json={"id": 42})
    with respx.mock:
        respx.post("https://api.github.com/repos/customer/repo/hooks").mock(side_effect=created)
        inbox = await register(store, "github", "provider-access-secret", ["push"], "customer/repo")
        assert inbox["subscription"]["external_id"] == "42"
        body = b'{"ref":"refs/heads/main"}'
        signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        with TestClient(create_app(settings)) as client:
            assert client.post(inbox["url"], content=body).status_code == 401
            assert client.post(inbox["url"], content=body, headers={"x-hub-signature-256": signature}).status_code == 200
        with store.connection() as db:
            assert "provider-access-secret" not in json.dumps([dict(row) for row in db.execute("SELECT * FROM inboxes")])
        respx.delete("https://api.github.com/repos/customer/repo/hooks/42").respond(204)
        await remove("github", "provider-access-secret", "42", "customer/repo")
        store.delete(inbox["token"])


@pytest.mark.asyncio
async def test_stripe_registration_signature_timestamp_and_idempotency(settings):
    store = Store(settings)
    with respx.mock:
        respx.post("https://api.stripe.com/v1/webhook_endpoints").respond(200, json={"id": "we_123", "secret": "whsec_test"})
        inbox = await register(store, "stripe", "sk_test_example", ["payment_intent.succeeded"])
    body = b'{"id":"evt_123","type":"payment_intent.succeeded"}'
    def signature(sent):
        value = hmac.new(b"whsec_test", str(sent).encode() + b"." + body, hashlib.sha256).hexdigest()
        return f"t={sent},v0=ignored,v1=wrong,v1={value}"
    with TestClient(create_app(settings)) as client:
        assert client.post(inbox["url"], content=body, headers={"stripe-signature": signature(int(time.time())-301)}).status_code == 401
        headers = {"stripe-signature": signature(int(time.time()))}
        assert client.post(inbox["url"], content=body, headers=headers).status_code == 200
        assert client.post(inbox["url"], content=body, headers=headers).status_code == 200
    assert store.requests(inbox["token"])["total_requests"] == 1


@pytest.mark.asyncio
async def test_linear_registration_uses_returned_secret_and_rejects_replays(settings):
    store = Store(settings)
    with respx.mock:
        respx.post("https://api.linear.app/graphql").respond(200, json={"data": {"webhookCreate": {"success": True, "webhook": {"id": "hook-123", "secret": "linear-secret"}}}})
        inbox = await register(store, "linear", "lin_api_example", ["Issue"], "team-123")
    with TestClient(create_app(settings)) as client:
        for age, status in [(0, 200), (61, 401)]:
            body = json.dumps({"type": "Issue", "webhookTimestamp": (time.time()-age)*1000}).encode()
            signature = hmac.new(b"linear-secret", body, hashlib.sha256).hexdigest()
            assert client.post(inbox["url"], content=body, headers={"linear-signature": signature}).status_code == status
    assert store.requests(inbox["token"])["total_requests"] == 1


@pytest.mark.asyncio
async def test_failed_registration_cleans_up_native_inbox(settings):
    store = Store(settings)
    with respx.mock:
        respx.post("https://api.github.com/repos/customer/repo/hooks").respond(403, json={"message": "forbidden"})
        with pytest.raises(InboxError, match="permissions"):
            await register(store, "github", "invalid-token", ["push"], "customer/repo")
    with store.connection() as db:
        assert db.execute("SELECT COUNT(*) FROM inboxes").fetchone()[0] == 0
