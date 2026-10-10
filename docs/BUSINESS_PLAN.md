# Openhook hosted business

Owner: Berkant. Implementation started 2026-10-10.

## Outcome

Earn recurring revenue from operating Openhook while keeping a useful MIT-licensed
self-hosted product. Shipping billing is not evidence of demand; paid customers,
repeat use, retention, and costs must be measured separately.

## First customer and offer

Start with individual developers using coding agents to build webhook integrations.
The first useful result is a real callback received, inspected by the agent, and
optionally forwarded to a local handler. Make that work before asking for payment.

Proposed hosted Pro: $19 USD/month, one developer, 10 persistent inboxes, 50,000
accepted events per calendar month, 30-day payload retention, and 1 GiB retained
payload storage. These are testable launch assumptions. The implementation is being validated;
the plan is not live and the price is not validated. No automatic overage charges. Stop accepting new events at
published capacity; preserve already accepted events within retention.

Anonymous hosted inboxes remain useful for one-off tests. Existing inboxes retain
their promised expiry. Self-hosted users can run the core without a hosted account,
paid license, payment provider, or Openhook-controlled infrastructure.

Charge for managed hosting, stable addresses, account recovery, and capacity.
Do not paywall MCP, the local listener, basic inspection, or security fixes.
Do not promise an uptime SLA or automatic waking of a stopped Codex session.

## Delivery sequence

1. Hosted identity: optional GitHub sign-in, secure sessions, scoped/revocable
   agent keys, and account isolation. Request no repository access for sign-in.
2. Paid product: account-owned persistent inboxes, all-transport usage enforcement,
   time-based payload retention, cross-device access, and usable limit messages.
3. Billing: server-owned prices, Checkout, customer portal, verified and idempotent
   webhooks, cancellation/dunning behavior, and recovery from out-of-order events.
   A browser success redirect must never grant a paid entitlement.
4. Onboarding: one real callback, visible agent setup, optional forwarding, clear
   free/hosted/self-hosted choice, and customer-visible billing/usage status.
5. Acquisition: outcome-focused README and landing page, copyable recipes,
   provider examples, contribution/security guidance, and an honest launch demo.
6. Validation: recruit 10 developers; seek 3-5 paid commitments; measure weekly
   return use and actual revenue. Do not count stars as willingness to pay.

## Launch dependencies

- Seller/legal entity, support contact, payment-provider account, currency/tax
  handling, and customer-facing terms must be resolved before live checkout.
- Dedicated GitHub OAuth app credentials and callback registration are required
  to enable hosted sign-in. No credentials from other products may be reused.
- Payment integration must pass test-mode lifecycle checks before live activation.
- External community posts and direct outreach require specific channel/recipient
  authorization; draft useful contributions and launch copy first.

## GTM experiments

Keep acquisition honest and useful. Publish working examples for receiving a real
payment-provider test callback, inspecting an inbound email, and forwarding an
external event to a local handler. Each example links to both hosted setup and
self-hosting. Provide a short agent skill; never require stars, follows, or payment
for the open-source workflow.

Track bounded, first-party conversion events: hosted account created, first owned
inbox, first real accepted callback, checkout started, paid entitlement activated,
and cancellation. Keep bodies, inbox tokens, provider secrets, and message content
out of acquisition data. Record only deliberate referral categories, not arbitrary
tracking query strings or browser fingerprints.

Initial weekly scorecard: activated developers, 7-day repeat use, checkout starts,
paying accounts, recognized recurring revenue, cancellations, retained bytes, and
support/hosting cost. Pricing and customer counts above are hypotheses, not results.

## Engineering boundaries

Use the existing Python/Starlette service and SQLite transactions. Hosted features
are opt-in configuration and must fail closed when credentials are missing. Keep
business policy separate from payment HTTP calls; avoid another service or frontend
framework. Preserve public/private inbox separation and atomic activity records.
The original release is ed7c6db; preserve its working HTTP, SMTP, DNS, MCP, and
listener behavior throughout this work.

## Current progress

- [x] Baseline released and live integration checks passed.
- [x] First offer, customer, success metrics, and launch dependencies documented.
- [x] Hosted identity and secure account API (local tests).
- [x] Paid inbox ownership and enforced limits (local tests).
- [x] Billing adapter with signed, mocked lifecycle tests.
- [ ] Real Stripe sandbox lifecycle and dedicated GitHub OAuth verification.
- [x] Hosted dashboard, onboarding, and conditional pricing implemented.
- [x] Open-source acquisition assets and local browser validation.
- [ ] Hosted foundation merged/deployed; remote release checks.
- [ ] Live merchant activation and launch.
- [ ] First paying customers and measured retention.
