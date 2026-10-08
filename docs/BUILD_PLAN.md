# Openhook delivery

Openhook is an independent self-hosted event service with its own capture URLs,
storage, and delivery. The website and app use a centered text interface with
Paper Mono v1.000. The webhook demo sends a real request to the native service.

- Native SQLite store and separate public/write versus private/read capabilities
- Native HTTP, SMTP, and authoritative UDP/TCP DNS receivers
- Streamable HTTP and stdio MCP over the same store
- Browser inspector, current schemas, setup, privacy, SVG identity
- Separate project on the existing personal Dokploy host
- Cloudflare DNS and public HTTPS
- Native tests and customer-visible event capture proof

The public service is deployed through Dokploy at https://openhook.dev.
HTTPS capture, the browser relay and inspector, the 26-tool MCP handshake,
SMTP through the public MX, authoritative UDP/TCP DNS and recursive DNS capture,
signed GitHub registration and removal, and local forwarding with cursor resume
have been verified against the deployment. See [release evidence](testing.md).

Stripe and Linear use mocked provider tests; live account registration remains
unverified. Managed SSH provisioning remains outside this release. Local delivery
uses an outbound HTTPS listener and does not require an exposed local port.
