# Openhook

An event inbox for AI agents. Create a public URL, wait for a callback, inspect
what arrived, and continue the task.

Openhook operates its own HTTP, SMTP, and authoritative DNS capture servers.
Events live in its SQLite database. No external webhook service is involved.

## Run it

```sh
uv sync
uv run openhook --http
```

Open http://127.0.0.1:8788/app. The website, capture API, and Streamable HTTP MCP
endpoint share one service and one durable store.

Connect an MCP client to `http://127.0.0.1:8788/mcp`, or use
`uv run openhook` for stdio. A local stdio process shares the same database
with a running HTTP process when both use the same `OPENHOOK_DATABASE`.
The HTTP process must be running to receive HTTP callbacks.

## Agent workflow

1. Call `create_webhook`. Save the private `ohk_` management token.
2. Give the returned public HTTP URL, email address, or DNS name to the sender.
3. Call `wait_for_request` with the management token.
4. Inspect the event and act. Reconnect using the returned `next_since` cursor.

Public capture addresses cannot read or delete events. Rotate a compromised
management token with `rotate_webhook_token`. Rotation preserves public addresses.

Inboxes expire within seven days. Each retains its latest 1000 events.
Individual events are limited to 1 MB. Email and DNS addresses are returned only
when their listeners are configured.

## Native tools

26 tools cover inbox creation, response configuration, token rotation,
event inspection, literal search, notes, JSON/CSV export, exact-byte download,
HTTP/email waits, test events, link/code extraction, callback checking,
delayed responses, provider subscriptions, and deletion. See [the generated tool reference](docs/TOOLS.md).

Set `verification_secret` through `configure_webhook` to require SHA256 HMAC
on raw HTTP bodies. Openhook accepts `X-Openhook-Signature: sha256=…` and
GitHub's `X-Hub-Signature-256`. Invalid signatures are rejected before capture.
`Idempotency-Key` and `X-GitHub-Delivery` deduplicate retries within an inbox.

Incoming URLs with `?openhook_wait=1` wait up to 20 seconds for an agent response.
Start `respond_to_next_request` before sending such a request.

## Configuration

| Environment variable | Purpose |
| --- | --- |
| `OPENHOOK_ORIGIN` | Public origin, default http://127.0.0.1:8788 |
| `OPENHOOK_DATABASE` | SQLite path, default data/openhook.sqlite3 |
| `OPENHOOK_EMAIL_DOMAIN` | Own inbound mail domain; unset disables SMTP |
| `OPENHOOK_SMTP_PORT` | SMTP listener, default 2525; map public port 25 |
| `OPENHOOK_DNS_DOMAIN` | Own delegated callback zone; unset disables DNS |
| `OPENHOOK_DNS_PORT` | UDP/TCP DNS listener, default 5353; map public port 53 |
| `OPENHOOK_DNS_ADDRESS` | IPv4 address returned for DNS A lookups |

SMTP rejects mail for unknown inboxes and never relays mail. DNS answers only
for the configured zone and does not provide recursion.

## Deploy

Use the Dockerfile and `compose.dokploy.yaml` in a separate Dokploy project.
Attach the Openhook domain to service `openhook`, port 8788. Its named data
volume survives releases. See [deployment notes](docs/deployment.md).

## Provider registration and local delivery

Call `register_github_webhook`, `register_stripe_webhook`, or
`register_linear_webhook` to create a native inbox and subscribe at the source.
Provider API credentials are used transiently and never saved. Raw signatures
are checked before capture; Stripe and Linear timestamps are checked for replay.
Call `unregister_webhook` before the inbox expires to remove the source subscription.

For local delivery, set `OPENHOOK_TOKEN` to your private inbox token, then run:

```sh
uv run openhook-listen --forward http://127.0.0.1:8080/webhook
# Or wake an already configured local OpenClaw:
uv run openhook-listen --openclaw
```

OpenClaw delivery also requires `OPENCLAW_HOOKS_TOKEN`. With no destination,
the listener prints events as JSON. It connects outward over HTTPS, saves a
cursor after successful delivery, and retries failed deliveries. Delivery is
at least once: recipients should deduplicate by event ID. Each destination has
its own cursor; run one listener per destination and token. Managed SSH tunnel
provisioning is not included.

## Verify

The website uses a centered text interface and the self-hosted Paper Mono
v1.000 variable font. Its webhook demo creates an inbox, sends a real callback,
and reads the captured event. Refresh asset versions after editing `web/`:

```sh
bun run build
```

```sh
uv run --extra dev pytest
node --check web/assets/app.js
```

Tests exercise native HTTP capture, private-token isolation, signature checks,
idempotency, persistence, expiry, MCP, and real local SMTP and UDP/TCP DNS.

MIT licensed. Required third-party notices are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
