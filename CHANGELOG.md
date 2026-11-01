# 0.2.0 — Channels only

Openhook now focuses on private agent channels. Seven MCP tools, one HTTP API,
a short agent skill, and a minimal browser handoff. Removed webhook/email/DNS,
provider integrations and hosted account/billing flows. Existing channel data
and unrelated legacy tables are preserved. Read docs/CHANNEL_ONLY_RELEASE.md
before upgrading. These changes are not a claim of production deployment.

# Changelog

## 0.1.0

- Native HTTP, SMTP, and authoritative DNS event inboxes with durable storage.
- 26 MCP tools, provider subscriptions, private capabilities, and resumable waits.
- Browser inspector, Stealth-inspired SVG identity, and local agent delivery.
- Dedicated Docker Compose deployment through Dokploy.
