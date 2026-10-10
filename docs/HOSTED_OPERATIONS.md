# Operating the hosted edition

Hosted identity and billing are opt-in. The default deployment stays anonymous
and self-hostable. Do not enable live checkout until the launch checks below pass.
The application adds tables alongside existing inboxes; it does not convert free
inboxes or change their expiry.

## Configuration

| Variable | Purpose |
| --- | --- |
| `OPENHOOK_HOSTED=true` | Enable accounts and hosted ownership policy |
| `OPENHOOK_GITHUB_CLIENT_ID` | Dedicated GitHub OAuth application's client ID |
| `OPENHOOK_GITHUB_CLIENT_SECRET` | Its secret; never commit it |
| `OPENHOOK_BILLING_ENABLED=true` | Explicit new-checkout activation gate |
| `OPENHOOK_STRIPE_SECRET_KEY` | Dedicated Stripe test secret first |
| `OPENHOOK_STRIPE_WEBHOOK_SECRET` | Endpoint signing secret |
| `OPENHOOK_STRIPE_PRICE_ID` | Active recurring price, USD 1900, monthly, interval count 1 |
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
