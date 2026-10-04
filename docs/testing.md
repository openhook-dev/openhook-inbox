# Testing Openhook

Run `uv run --extra dev pytest -q`, `uv run python scripts/generate_docs.py --check`,
and `node --check web/assets/app.js`.

The suite covers native persistence, capability isolation, raw-byte signatures,
expiry, idempotency, HTTP/MCP, and real local SMTP plus UDP/TCP DNS sockets.
Provider control-plane tests use fixtures based on official APIs; they do not
prove live provider access. Listener tests cover exact-byte forwarding and agent
wakeup payloads.

For a release, also prove public TLS, HTTP capture through MCP, public MX receipt,
delegated DNS capture, local forwarding, and persistence across an application
restart. Register and remove a real hook on a repository you control. Keep API
credentials and inbox management tokens out of logs and committed evidence.
