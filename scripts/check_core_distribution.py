"""Run with an isolated Python (-I) containing only the built core wheel.

This deliberately refuses hosted imports and operator credential reads, then
exercises HTTP capture, Stripe signature verification, and MCP tool discovery.
"""

import hashlib
import hmac
import importlib.abc
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
from zipfile import ZipFile


class NoHostedImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"openhook_hosted", "standardwebhooks"}:
            raise AssertionError(f"Core attempted a hosted import: {fullname}")


def main():
    for name in ("openhook_hosted", "standardwebhooks"):
        assert importlib.util.find_spec(name) is None, f"{name} must not be installed"
    sys.meta_path.insert(0, NoHostedImports())
    getenv = os.getenv

    def core_env(name, default=None):
        assert not name.startswith(("OPENHOOK_GITHUB_", "OPENHOOK_POLAR_", "OPENHOOK_STRIPE_", "OPENHOOK_BILLING_")), name
        assert name != "OPENCLAW_HOOKS_TOKEN", name
        return getenv(name, default)

    os.getenv = core_env
    with ZipFile(sys.argv[1]) as wheel:
        names = wheel.namelist()
        assert not any(name.startswith("openhook_hosted/") for name in names)
        assert not any(name in names for name in ("openhook/billing.py", "openhook/polar_billing.py", "openhook/hosted_web.py"))
        metadata = wheel.read(next(name for name in names if name.endswith(".dist-info/METADATA"))).decode()
        dependencies = [line.lower() for line in metadata.splitlines() if line.startswith("Requires-Dist:")]
        assert not any("standardwebhooks" in line or "openhook-hosted" in line for line in dependencies)

    from starlette.testclient import TestClient
    from openhook.settings import Settings
    from openhook.web import create_app
    from dataclasses import replace

    with tempfile.TemporaryDirectory() as directory:
        settings = replace(Settings.from_env(), database=str(Path(directory) / "core.db"), origin="http://testserver")
        with TestClient(create_app(settings)) as client:
            assert client.get("/health").status_code == 200
            assert client.get("/api/account").status_code == 404
            assert client.get("/auth/github").status_code == 404
            assert client.post("/billing/polar", content=b"untrusted").status_code == 404
            assert "Paid checkout is not available yet" in client.get("/pricing").text
            inbox = client.post("/api/v1/call", json={"action": "create"}).json()["data"]
            store = client.app.state.store
            store.configure(inbox["token"], {"signature_provider": "stripe", "verification_secret": "inbox-signing-secret"})
            body = b'{"event":"core-package-check"}'
            sent = str(int(time.time()))
            digest = hmac.new(b"inbox-signing-secret", sent.encode() + b"." + body, hashlib.sha256).hexdigest()
            path = "/h/" + inbox["inbox_id"]
            assert client.post(path, content=body, headers={"stripe-signature": f"t={sent},v1={digest}"}).status_code == 200
            assert client.post(path, content=body, headers={"stripe-signature": f"t={sent},v1=invalid"}).status_code == 401
            headers = {"Accept": "application/json, text/event-stream"}
            tools = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
            assert tools.status_code == 200, tools.text
            assert any(tool["name"] == "create_webhook" for tool in tools.json()["result"]["tools"])
            received = client.post("/mcp", headers=headers, json={"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "get_webhook_requests", "arguments": {"webhook_token": inbox["token"]}}})
            assert received.status_code == 200, received.text
            assert not received.json()["result"].get("isError"), received.text
            assert "core-package-check" in received.text, received.text
            owner = client.post('/api/v1/sessions', json={'action': 'create', 'name': 'Owner', 'title': 'Wheel check'}).json()['data']
            guest = client.post('/api/v1/sessions', json={'action': 'join', 'invite_code': owner['invite_url'], 'name': 'Guest'}).json()['data']
            assert client.post('/api/v1/sessions', json={'action': 'send', 'participant_token': guest['participant_token'], 'text': 'packaged conversation', 'message_id': 'wheel'}).status_code == 200
            history = client.post('/api/v1/sessions', json={'action': 'read', 'participant_token': owner['participant_token']})
            assert history.json()['data']['events'][-1]['text'] == 'packaged conversation'
            assert 'Work together, from your own AI.' in client.get('/sessions').text
            assert client.get('/assets/sessions.js').status_code == 200
            assert any(tool['name'] == 'create_agent_session' for tool in tools.json()['result']['tools'])
    print("Core wheel: no hosted imports or credential reads; signed capture and MCP read passed.")


if __name__ == "__main__":
    main()
