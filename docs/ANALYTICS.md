# Analytics and operations

Openhook uses two separate views. Umami measures public-page visits and button
clicks. Prometheus/Grafana measures server traffic and operational health,
including agents that never visit the website. Neither is an accounting ledger.

## Public website analytics

Set `OPENHOOK_UMAMI_SCRIPT_URL` to your self-hosted HTTPS `script.js` URL and
`OPENHOOK_UMAMI_WEBSITE_ID` to the website UUID. Both default to empty, so
self-hosted installations send no website analytics unless explicitly configured.

Only public HTML pages load the tracker. `/app`, `/account`, OAuth callbacks,
capture URLs, APIs and MCP do not. The before-send hook removes query strings,
fragments, referrer paths, arbitrary properties and identities. Consequently UTM
parameters are intentionally not collected. Referring domains, page paths,
browser/device statistics and approximate geography remain available. Do Not
Track and Global Privacy Control suppress collection. No session replay or
advertising integration is enabled.

Named events are `connect-click`, `pricing-click`, `try-inbox-click`, `pro-click`,
`account-click`, `source-click`, and `copy-setup-click`. These measure intent;
clicking Pro is not a signup or purchase, and a copy click is not proof that
clipboard access succeeded. Umami counts approximate visitors, not verified
people. Blockers and privacy preferences make browser analytics incomplete.

Production website: https://analytics.berkant.me/websites/d9c5e0f4-99f5-469e-9a2c-65f65954cbe8

## Operational metrics

Set a randomly generated `OPENHOOK_METRICS_TOKEN` of at least 32 characters.
`GET /metrics` requires `Authorization: Bearer <token>`. Without configuration
it returns 404; without the correct token it returns 401. Never put the token in
a URL or dashboard HTML. The endpoint is not an MCP tool.

- HTTP counts by bounded route group, method and status; duration histograms.
- Actual MCP tool success/error counts, independently of HTTP status.
- Committed captures by web/email/DNS and marked-test/unmarked traffic. Duplicate
  deliveries do not increment accepted-event counts.
- Inbox creation by free/Pro, current accounts and current paid entitlements.
- Retained inboxes/events, database capacity and free disk space.

Metrics never label payloads, IPs, user/account IDs, inbox IDs, tokens, arbitrary
paths or query parameters. Counters start when this version starts and reset on
process restart; Prometheus `rate`/`increase` handle observed resets. Events before
the first scrape or during collection outages cannot be reconstructed from these
counters. This deployment runs one application process; do not enable multiple
Uvicorn workers without configuring Prometheus multiprocess collection or separate
scrape targets. Stdio clients in separate processes are not counted by the HTTP
server's process metrics.

Unmarked events can still be bots, probes or unmarked tests: they are not evidence
of customer adoption. Successful OAuth callbacks include returning sign-ins.
Checkout counts include reused checkout links. Paid-account gauges are not MRR.
Use Polar's ledger and `scripts/business_report.py` for sales reconciliation.

## Monitoring deployment

`monitoring/compose.yaml` provides pinned Prometheus and Grafana releases,
persistent volumes, resource limits and a provisioned Openhook dashboard.
Prometheus keeps at most 30 days / 2 GB of time series. No service publishes a
host port. Grafana uses the existing Traefik/TLS route at
https://analytics.berkant.me/ops/ and requires login; anonymous access and public
signup are disabled. Prometheus is only accessible on Docker networks.

Deploy the directory outside the application checkout, create a private `.env`
with `GRAFANA_ADMIN_USER`, `GRAFANA_ADMIN_PASSWORD`, and `GRAFANA_SECRET_KEY`, and
create `metrics-token` containing the same token as Openhook. Never commit either
file. The token file must be readable by the Prometheus container user, while the
parent deployment directory should be restricted to the operator. Run:

```sh
docker compose run --rm --entrypoint promtool prometheus check config /etc/prometheus/prometheus.yml
docker compose up -d
```

Verify the authenticated metrics endpoint, Prometheus target `up == 1`, and
dashboard queries after every deployment. Preserve Grafana and Prometheus volumes
when upgrading; preserve the Grafana secret key. Credential recovery is through
the operator's protected files, never through the public app.

Alert rules cover failed scrapes, server errors, 429s, database/inbox capacity and
low disk space. They appear in the dashboard. **No outbound notification receiver
is configured.** Sending alerts to an email or chat channel requires choosing and
configuring a destination. Monitoring runs on the same host: a host-wide outage
needs an independent external uptime check for notification.

Validation: Python tests cover endpoint auth/redaction, duplicate capture counts,
public-only analytics and CSP. `node --test native_tests/analytics.test.mjs`
covers payload sanitization, private paths and browser privacy preferences.
