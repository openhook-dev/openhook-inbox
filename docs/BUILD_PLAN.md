# Openhook delivery

Openhook is an independent self-hosted event service with its own capture URLs,
storage, and delivery. The UI follows Stealth's restrained design principles.

- Native SQLite store and separate public/write versus private/read capabilities
- Native HTTP, SMTP, and authoritative UDP/TCP DNS receivers
- Streamable HTTP and stdio MCP over the same store
- Browser inspector, current schemas, setup, privacy, SVG identity
- Separate project on the existing personal Dokploy host
- Cloudflare DNS and public HTTPS
- Native tests and customer-visible event capture proof

Pending: public deployment verification, public SMTP/MX and delegated DNS proof.
Provider registration and local HTTPS delivery are implemented. Managed SSH provisioning remains outside this release.
