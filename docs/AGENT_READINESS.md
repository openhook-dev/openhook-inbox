# Public agent contracts

Public pages render their content in HTML without JavaScript. The same canonical
URLs negotiate a Markdown representation for `Accept: text/markdown`, with
`Vary: Accept` on both representations. Markdown comes from the same page content,
so pricing and feature descriptions do not diverge. Private `/app` and `/account`
screens remain HTML and noindex.

Unknown public paths retain HTTP 404 and provide navigation guidance in HTML or
Markdown. API errors use RFC 9457 `application/problem+json`: type, title, status,
code, detail, resolution, and the compatible success/message fields. Unknown API
routes and wrong methods use this same contract. Error pages never echo private
URL parameters or arbitrary exception details.

Stable inbox operations are exposed under `/api/v1`; original `/api` paths remain
aliases with the same authentication, validation, storage and limits. Breaking
changes need a new major version; a removal requires at least 90 days of notice
with Deprecation/Sunset headers. No removal is scheduled. The public capture URL
does not change. It accepts caller-selected response types and defaults to plain
text, so its OpenAPI response is intentionally different from management JSON.

API/MCP/capture/auth responses advertise the existing per-IP rolling HTTP limit.
RateLimit-Policy and RateLimit use structured fields; the compatibility
RateLimit-Limit, RateLimit-Remaining and RateLimit-Reset fields remain available.
HTTP throttling returns Retry-After. Storage or entitlement exhaustion can require
cleanup or subscription management rather than time-based retries.

Discovery endpoints:

- `/server.json`: remote MCP registry manifest (publication is a separate action).
- `/.well-known/mcp/server-card.json` and `/mcp/server-card`: server identity,
  logo, transport and supported protocol version.
- `/.well-known/ai-catalog.json`: link to the MCP card.
- `/.well-known/api-catalog`: RFC 9727 API catalog linking OpenAPI and docs.
- `/.well-known/agent-skills/index.json`: skill with SHA-256 of its rendered bytes.
- `/.well-known/agent-skills/openhook/SKILL.md`: the same current skill as `/skill.md`.

MCP resources expose public guide, tool-reference and pricing documents. Inbox
events never appear in the resource listing. The tools retain their existing
private-token and hosted-account authorization boundaries.

The initial is-agentic.com scan on 2026-10-12 at 23:45 UTC scored 67/100. Its
essential gaps were Markdown negotiation, Markdown 404 recovery, JSON errors on
unknown API routes, and an advertised but empty MCP resource listing. Recommended
gaps included typed errors, response schemas, rate-limit headers, version policy,
trust pages and when-to-use guidance. Brand search and third-party indexing are
external observations; schema does not invent an operator address or profiles.

Recheck the deployed host and then request a fresh scan at
https://is-agentic.com/scan/openhook.dev. The public report API is
`https://is-agentic.com/api/v1/report?url=https%3A%2F%2Fopenhook.dev`.
A passing local check is not proof of a new external score; report timestamps
must postdate deployment.
