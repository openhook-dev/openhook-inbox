# Operating the hosted edition

Hosted identity and billing are opt-in. The default deployment stays anonymous
and self-hostable. Do not enable live checkout until the launch checks below pass.
The application adds tables alongside existing inboxes; it does not convert free
inboxes or change their expiry.

## Install and upgrade

Login and payment adapters live in the separate `hosted/` package. The default
`uv sync`, `openhook --http`, `openhook` (stdio), and `Dockerfile` install/run only
the core. They do not load GitHub login, Stripe billing, or Polar credentials.

For a hosted deployment, keep the existing database, environment variables and
volume, and explicitly run the hosted entry point:

```sh
uv sync --package openhook-hosted
uv run --package openhook-hosted openhook-hosted --host 0.0.0.0 --port 8788
```

Containers must use `docker build --target hosted .`; `compose.dokploy.yaml`
selects this target.
For ASGI deployments replace `web_app:create_app` with
`openhook_hosted.app:create_app` (factory mode). Change the build/entry point in
the same release as this package split. Do not deploy the core-only image against
a hosted customer database: owned inboxes deliberately prevent core startup.
There is no schema migration or payment-provider change in this split.

`OPENHOOK_HOSTED=false` prevents loading operator login/payment credentials.
With hosted mode enabled, only `OPENHOOK_BILLING_PROVIDER`'s credentials are
loaded. Disabling new sales still keeps payment reconciliation and the portal
working for existing customers.

## Polar (openhook.dev)

Set `OPENHOOK_BILLING_PROVIDER=polar`. The default remains `stripe` for existing
self-hosted installations. Both adapters share the account policy, but billing
accounts and checkout attempts prevent changing provider or payment environment
on an existing database. Use a separate sandbox database.

| Variable | Purpose |
| --- | --- |
| `OPENHOOK_POLAR_ACCESS_TOKEN` | Dedicated Openhook organization token; never commit it |
| `OPENHOOK_POLAR_WEBHOOK_SECRET` | Standard Webhooks secret from a newly created endpoint |
| `OPENHOOK_POLAR_ORGANIZATION_ID` | Owning Polar organization |
| `OPENHOOK_POLAR_PRODUCT_ID` | One recurring monthly Pro product, no trial |
| `OPENHOOK_POLAR_PRICE_ID` | Its single active fixed USD 1900 price |
| `OPENHOOK_POLAR_SANDBOX=true` | Use sandbox API; set false only for the production organization |

The common hosted, GitHub and billing gate variables below also apply. Required
API scopes are organizations:read, products:read, customers:read,
subscriptions:read, orders:read, checkouts:read/write and customer_sessions:write.
Use a separate setup token for webhooks:read/write. Track token expiration and
rotate before expiry; an expired token blocks checkout and payment reconciliation.

Configure **exclusive** tax on the price or organization. Keep one price, no
trials, discounts, seats, usage billing or customer plan changes. The application
checks the product contract before creating checkout, and checks its returned
price/currency/tax behavior before exposing the URL. Polar must approve the
organization and payout setup before new sales can be enabled.

Create a raw webhook at `https://YOUR_HOST/billing/polar` with API version
**2026-10**, subscribing to `order.paid`, `order.refunded`, and
`subscription.revoked`. New endpoints use Standard Webhooks signature verification;
legacy secrets created before September 8, 2026 are not supported. Outbound API
requests also pin version 2026-10. Plan a tested API version upgrade before Polar
retires it. Never publish the webhook secret or a pre-authenticated portal URL.

Checkout binds the authenticated account UUID as `external_customer_id` and
`metadata.openhook_account`. Direct dashboard checkout links do not carry this
binding and must not be advertised. Keep the product private and send buyers
through `/account`. The customer portal provides invoices and cancellation.

Only the canonical paid order's positive, non-prorated configured-price line can
extend access. Its own `start_timestamp` and `end_timestamp` define the paid period;
a subscription's mutable current period never grants time. Failed payment,
trial, zero-value order, and checkout return cannot grant access. Ordinary
cancellation retains paid time. A full refund removes that order's entitlement;
a partial refund retains it. Explicit subscription revocation excludes all orders
for that subscription. Terminal ledger entries prevent late or concurrent paid
deliveries from restoring refunded/revoked access. Disputes still need operator
review. Existing payload retention continues after revocation.

Checkout creation is claimed in SQLite before a provider POST. Concurrent requests
cannot create multiple sessions. Known open sessions are reused; expired sessions
can be replaced. An ambiguous provider failure deliberately stays pending. Inspect
Polar's checkout list for `metadata.openhook_attempt` matching `billing_attempts.identifier`.
After verifying account, product, status and URL, link the actual session ID and URL
to the pending row. Only remove a pending row once you have confirmed no checkout
was created, or the identified session has expired. Never blindly retry a POST or
re-run a charge to repair entitlement state.

Before enabling sales, complete a provider sandbox payment and verify the signed
webhook, account grant, persistent inbox capture, portal cancellation, renewal,
refund and revocation. The local tests mock provider HTTP; they are not a real
payment-flow test. Verify the actual GitHub callback and production account review.
Pause new sales with `OPENHOOK_BILLING_ENABLED=false`; webhooks and management
remain available. Leave `OPENHOOK_HOSTED=true` after onboarding customers.

## Stripe configuration (alternative provider)

| Variable | Purpose |
| --- | --- |
| `OPENHOOK_SUPPORT_EMAIL` | Monitored support address linked in the site footer |
| `OPENHOOK_HOSTED=true` | Enable accounts and hosted ownership policy |
| `OPENHOOK_GITHUB_CLIENT_ID` | Dedicated GitHub OAuth application's client ID |
| `OPENHOOK_GITHUB_CLIENT_SECRET` | Its secret; never commit it |
| `OPENHOOK_BILLING_ENABLED=true` | Explicit new-checkout activation gate |
| `OPENHOOK_STRIPE_SECRET_KEY` | Dedicated restricted Stripe key where possible; sandbox first |
| `OPENHOOK_STRIPE_WEBHOOK_SECRET` | Endpoint signing secret |
| `OPENHOOK_STRIPE_PRICE_ID` | Active USD 1900 monthly price, interval count 1, licensed usage, per-unit billing, exclusive tax, no quantity transformation |
| `OPENHOOK_STRIPE_LIVE=false` | Require test objects; change only for an approved live launch |
| `OPENHOOK_STORAGE_LIMIT` | Global SQLite used-page capacity in bytes; default 1 GiB |

Use an HTTPS `OPENHOOK_ORIGIN`. Register exactly
`https://YOUR_HOST/auth/github/callback` with GitHub. Sign-in asks for `read:user`,
uses browser-bound state and S256 PKCE, and discards the GitHub access token.
User identity is the immutable GitHub numeric ID, not a mutable login name.
Do not reuse OAuth or payment credentials from another product.

Configure a Stripe webhook at `https://YOUR_HOST/billing/stripe` for `invoice.paid`.
Use API version **2025-06-30.basil**, matching the pinned outbound API version.
Use a separate database for sandbox work. Once paid invoices exist, the store
refuses to start if the configured Stripe mode differs from its recorded mode;
sandbox grants must never become live entitlements.

The integration reads the canonical invoice, subscription, and invoice lines from
Stripe. It accepts one positive, non-prorated line for the configured price and
account-owned subscription. Zero-paid invoices, trial-only invoices, and other
prices do not activate access. Do not add coupons, credits, plan changes, trials,
or additional prices without extending and testing this policy.

Checkout requires Stripe Tax and collection of billing addresses and terms
acceptance. Configure the seller, tax registrations, public business details,
customer support, and terms/privacy links in the dedicated Stripe account first.
Verify Tax settings are active and that registrations match the seller's confirmed
obligations. `automatic_tax=true` alone does not collect tax where no active
registration applies. See [the Stripe review](STRIPE_REVIEW.md) for the initial
sandbox audit and remaining integration work.
Configure its customer portal for payment-method updates, invoices, and
cancellation **at the end of the paid period**. Disable plan changes and quantity
changes. No application route lets an agent key manage billing.

## Entitlement and failure behavior

Only a verified, canonical paid invoice grants a paid-through date. A browser
success URL, checkout completion, subscription status, or failed payment cannot
activate a plan. Duplicate events and duplicate invoice deliveries are recorded
atomically with grants; older invoices cannot shorten a newer paid period.
A renewal extends owned inbox expiry to its paid-through date plus 30 days.

Cancellation stops future billing through Stripe. Already-paid time remains
usable. If renewal fails, capture stops when paid time ends; existing data stays
readable subject to its 30-day age limit. Inbox addresses expire 30 days after
paid time ends. A late renewal cannot resurrect an already-deleted inbox.

Refunds and disputes currently require operator review. Issuing a refund in Stripe
does not automatically revoke an existing paid period. Do not advertise automatic
refund or dispute handling. Reconcile the ledger and customer outcome manually.

Checkout retries reuse a persisted idempotency key and exact parameters. Existing
active, incomplete, or delinquent subscriptions block another purchase. An open
Checkout Session is reused. A stale unresolved customer/checkout creation stops
with a support error instead of risking a second charge after Stripe's idempotency
window. Resolve it by inspecting Stripe and linking the actual customer/session;
never blindly delete the pending row or grant time manually to hide a failure.

Provider timeouts return a retryable error without consuming an invoice/event.
The original signed Stripe delivery can be retried. Investigate repeatedly failing
400 responses: wrong mode, price, metadata, API schema, or unsupported invoice shape.
Never replay a customer payment to repair application state.

Keep `OPENHOOK_HOSTED=true` after onboarding customers. The store refuses to start
with hosted mode disabled while owned inboxes exist. Do not roll back to a release
that predates hosted policy against an active customer database. Turning it off is not a
billing kill switch: hosted policy needs the ownership tables to remain enabled.
Pause new sales with `OPENHOOK_BILLING_ENABLED=false`. Configured payment webhooks
and the customer portal continue working so renewals and cancellation remain
available to existing subscribers. Remove credentials only for full maintenance.

## Capacity and retention

One account gets 10 inboxes, 50,000 accepted events per UTC calendar month,
30-day payload retention, and 1 GiB serialized event data. HTTP, SMTP, and DNS share
the allowance. Duplicate retained source deliveries do not increment usage;
deleting payloads does not refund event usage. Stored bytes include encoded body,
headers, and notes. Activity records and delayed responses are separate operational
storage, covered by the global capacity limit. Activity metadata persists.

The default **global** 1 GiB limit is insufficient for multiple full Pro accounts.
Set capacity deliberately, monitor disk and SQLite size, and budget for activity,
backups, and free users. A reserve below 500 MiB free disk rejects new captures.
The service currently applies 120 HTTP/API requests per minute per source IP;
Pro is not a promise of high throughput or an uptime SLA. SMTP/DNS have their own
transport admission behavior. Test the intended load before making capacity claims.

## Test and launch checks

1. Back up SQLite consistently with its backup API; preserve volume permissions.
2. Run the full tests, asset build, generated-doc check, and browser flow. Local
   payment tests mock Stripe HTTP and **do not replace** the next step.
3. In a dedicated Stripe sandbox, complete real Checkout with test payment data;
   confirm invoice delivery, access, renewal, duplicate delivery, cancellation,
   failed renewal, portal, and interrupted/retried checkout. Check a second account
   cannot access the first account's customer or inboxes.
4. Verify GitHub sign-in with the dedicated app and the actual callback domain.
5. Approve the seller/support/terms/privacy/tax configuration, backup recovery,
   monitoring, storage allocation, and exact $19/month offer.
6. Enable live credentials and mode only after approval. A real charge requires
   explicit authorization. Confirm the first authorized paid invoice end to end.
7. Track demand, paid conversion, retention, hosting costs, and support burden.
   Working checkout alone is not a successful business.

## Hosted API and MCP

Browser sessions are HTTP-only cookies; mutations require the exact Origin.
Agent keys use `Authorization: Bearer oha_...` on:

- `GET /api/account/inboxes`: own inbox metadata and usage.
- `POST /api/account/inboxes` with `{"name":"Example"}`: a paid owned inbox.
- `POST /api/account/inboxes/{id}/access`: issue a private inbox capability.

MCP supports `account_key` on `create_webhook` and all provider registration tools;
`get_hosted_inboxes` and `access_hosted_inbox` recover existing inboxes. Ordinary
inbox tools still take `ohk_...`. Never pass an account key in a URL.

Keys can be revoked in `/account`. This prevents issuing new capabilities but does
not revoke previously issued inbox tokens. Rotate an inbox token to revoke all its
older capabilities without changing the capture address. Recovery capabilities
expire after at most 30 days; the primary token lasts until rotation or inbox expiry.
