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

## Public release evidence

Verified on 2026-10-08 against release `9c8c678` at https://openhook.dev:

- Dokploy reports the release complete; the deployed `home.js` SHA256 matches
  the checkout. Normal HTTPS certificate validation succeeds.
- The landing relay creates an inbox, captures an HTTP webhook, and opens its
  body, headers, endpoint details, and expiry in the browser inspector.
- A Streamable HTTP MCP client initializes successfully, lists 26 tools, and
  calls `server_status` without an error.
- A disposable inbox stores public HTTP, SMTP, and DNS events. Mail is sent to
  `smtp.openhook.dev:25`, resolved from the `mail.openhook.dev` MX. DNS works over
  UDP and TCP port 53 and through the public 1.1.1.1 recursive resolver.
- Native GitHub registration on `openhook-dev/openhook-inbox` receives a signed
  ping. Native unregister removes the test provider subscription.
- The CLI forwards original binary bytes and headers to a local HTTP receiver.
  Restarting the listener resumes from its saved cursor without replaying the
  first event.
- A captured public event survives restarting the Openhook application
  container, with its original binary body unchanged.

Temporary test inboxes and the GitHub test subscription were removed. Provider
fixtures still cover Stripe and Linear; live registration on those accounts has
not been verified. These checks prove the tested paths, not sustained load or
delivery guarantees beyond the documented at-least-once behavior.

## Text interface

The 2026-10-09 interface uses the official Paper Mono v1.000 variable webfont.
The landing, inbox, setup, and documentation contain only text and native form
controls. Desktop and 375px phone checks confirm no horizontal overflow. Both
themes and keyboard-operated callback capture work. The captured event opens
in the inspector with endpoint details; response settings remain accessible.
