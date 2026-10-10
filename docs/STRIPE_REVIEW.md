# Stripe integration review

Reviewed 2026-10-11 against Stripe's implementation planner and the connected
Openhook sandbox. This is a sandbox readiness review, not a paid-launch report.

## Recommended integration

The planner selects hosted Checkout, a flat monthly subscription, a free core
without payment details, Customer Portal, and Stripe-managed payment recovery.
Pro is paid up front when a user upgrades: USD 19 per month plus applicable tax.
Its event allowance is an application limit, not metered Stripe billing.

Use one Openhook Pro product and one USD 1900 monthly price: licensed usage,
per-unit billing, exclusive tax, and no quantity transformation. Billing produces
the recurring invoices and collects payment through Checkout. Separate manual
invoice creation, Connect, Quotes, and a custom card form are unnecessary for this
offer. Keep the existing server-owned mapping from Openhook account to Customer.

The planner also returned an Accounts v2 portal blueprint. It is not a requirement
to migrate this existing Customer integration: Stripe's portal supports the
`customer` parameter already used here. Likewise, the generic suggestion to
provision on `checkout.session.completed` must not weaken the existing rule that
only a verified paid invoice grants access. Checkout completion can precede a
delayed payment's success.

## Initial sandbox audit

The official Stripe MCP connection succeeds and exposes the implementation
planner. Its sole authorized account is Openhook sandbox, in test mode, with
read access. The planner's selected configuration was accepted. The tax decision
was explicitly left unresolved pending the merchant's actual obligations.

Read-only API calls confirmed:

| Item | Observed result |
| --- | --- |
| Prices | Empty list, no further pages |
| Customer Portal configurations | Empty list, no further pages |
| Webhook endpoints | Empty list, no further pages |
| Tax registrations | Empty list, no further pages |
| Tax settings | `pending`, missing `head_office`; no default tax code or behavior |

The user-supplied API keys were not saved, printed, or used. MCP OAuth supplied
the account access for this review. No Stripe objects or production settings were
changed. A hosted payment has not been completed.

## Code review

The existing implementation in `openhook/billing.py` already covers the essential
payment boundary: raw-body signature verification, canonical Stripe invoice and
subscription reads, account ownership and mode checks, durable Checkout
idempotency, atomic invoice/event deduplication, and monotonic paid-through dates.
The browser cannot supply a price or Customer ID. Agent keys cannot manage billing.
Pausing sales preserves renewals and Customer Portal access.

This review fixes a price-validation gap. A one-time price with `recurring: null`
previously raised an unhandled exception. A monthly price with metered usage,
inclusive tax, or quantity transformation could pass the incomplete offer check.
Checkout now rejects incompatible prices before creating a Customer. Six
regression cases cover these errors. This patch is local and has not been deployed.

Remaining improvements, in priority order:

1. **Complete sandbox configuration and prove the payment path.** Create the
   product/price and portal, configure the actual seller details and terms URL,
   and deliver `invoice.paid` to a separate sandbox Openhook deployment/database.
   Tax settings are incomplete today. `automatic_tax=true` does not establish tax
   obligations or collect tax where no active registration applies. Have the seller
   confirm tax treatment, registrations, and the product tax category before
   configuring them; do not infer a legal registration from the account country.
2. **Configure recovery and make its outcome visible.** Enable Stripe's Smart
   Retries and appropriate customer payment-failure emails. The application
   intentionally ignores `invoice.payment_failed` and cancellation events when
   calculating paid time. Keep that entitlement rule, but add account-facing
   payment status if customers need an explanation and a recovery link. Recovery
   settings and emails have not been verified or enabled in this review.
3. **Validate a deliberate API-version upgrade.** The application and runbook pin
   `2025-06-30.basil`; the planner recommends flexible billing. This pin defaults
   to classic mode unless flexible is explicitly requested. Test the current
   stable API and flexible mode against real invoices before upgrading both the
   outbound version and webhook endpoint. Do not use the MCP search tool's
   preview OpenAPI version as a production version recommendation. Preserve exact
   request parameters for unresolved Checkout retries across any migration.
4. **Use a dedicated restricted runtime key.** Scope it to Customers, Checkout
   Sessions and Portal Sessions as required, with read access to Prices,
   Subscriptions, Invoices and their lines. Verify the exact permissions in the
   sandbox. Keep runtime credentials in the deployment's secret storage; the
   browser only receives hosted Stripe URLs. Hosted Checkout does not require
   the provided publishable key in the frontend.

Portal configuration should allow invoices, payment-method updates, and
cancellation at period end; disable subscription plan/quantity changes and
promotion codes until the entitlement policy supports them. Refunds and disputes
remain an explicit operator workflow. No automated refund/revocation claim is made.

## Validation and next execution

The focused suite passes: **27 tests**, including the six new price checks:

```sh
.venv/bin/python -m pytest native_tests/test_billing.py native_tests/test_hosted.py -q
```

These tests mock Stripe HTTP. They cover grants, renewal, duplicate and older
invoices, signatures, wrong mode/owner/price, rollback, retry stability, browser
authorization, and hosted policy. They do not prove Stripe Checkout, real webhook
delivery, Tax, email recovery, or Customer Portal works with this new account.

For the sandbox run, record the Checkout, Customer, subscription and invoice IDs
without secrets, then verify the stored paid-through date against the canonical
invoice line period. Exercise renewal, failed renewal, duplicate delivery,
cancellation at period end, Portal payment-method updates, interrupted checkout,
and a second account's isolation. Keep all test grants in a separate database.
Do not enable live checkout until these checks and the launch gates in
[HOSTED_OPERATIONS.md](HOSTED_OPERATIONS.md) pass.

## Sandbox setup and payment verification

Later on 2026-10-11, the user authorized sandbox write access. The official MCP
successfully created the following objects in Openhook sandbox only:

| Object | Identifier / result |
| --- | --- |
| Product | `prod_VPyZCseM62hQAB`, Openhook Pro |
| Price | `price_1UP8ciANdB6UPhKpISq4U9Sk`, USD 1900/month, exclusive tax, licensed usage |
| Price lookup key | `openhook_pro_monthly_usd_v1` |
| Default Portal configuration | `bpc_1UP8cpANdB6UPhKpbhO2RhfG` |
| Test clock | `clock_1UP8dbANdB6UPhKp8YISp0Ev` |
| Synthetic Customer | `cus_VPyaKL4HBWHHLx`, no email or personal details |
| Test subscription | `sub_1UP8dvANdB6UPhKpmpezF8vs` |
| First invoice | `in_1UP8dvANdB6UPhKpuXEUv63p`, paid, USD 1900 |
| Paid event | `evt_1UP8dxANdB6UPhKp7zyPItta` |

Portal invoice history and payment-method updates are enabled; cancellation is at
period end. Subscription changes and the public portal login page are disabled.
A Portal session was successfully created using the default configuration and
returned a valid Stripe billing URL. Portal browser interactions are not yet tested.

The subscription was created directly through Stripe's API with `pm_card_visa`
and explicit classic billing mode to match the application's current default.
Automatic tax was omitted for this isolated payment/entitlement test because the
seller's Tax setup is pending. This does not change application Checkout, which
still requires automatic tax and terms acceptance. No real card or money was used.
The test subscription is scheduled to cancel at its first period end
(`1794349258`) so it will not renew if its test clock advances beyond that point.

The real invoice, subscription, line items, and paid event were retrieved through
MCP. Replaying those recorded objects through `Billing.receive` against a separate
temporary SQLite database verified a single grant, duplicate rejection, the exact
paid-through date, and successful creation of an owned Pro inbox. This replay used
mocked HTTP and a local signature: it validates actual Stripe object compatibility,
not delivery of a Stripe-signed webhook to the application or the pinned API's
network responses. No runtime secret key was stored or used.

Still pending: seller identity/head-office details, confirmed tax treatment and
product tax category, terms/support configuration, a separate reachable sandbox
application endpoint, actual hosted Checkout and signed webhook delivery, renewal
and failed-renewal tests, and end-to-end Portal interactions. The MCP API search
did not expose a test-clock advance operation during this run. Production and live
billing remain unchanged. Sandbox IDs must not be used with live credentials.

## Stripe references

- [Hosted subscription Checkout](https://docs.stripe.com/billing/subscriptions/build-subscriptions?payment-ui=checkout&ui=stripe-hosted)
- [Customer Portal](https://docs.stripe.com/customer-management/integrate-customer-portal)
- [Flexible billing mode and API-version defaults](https://docs.stripe.com/billing/subscriptions/billing-mode)
- [Stripe Tax setup](https://docs.stripe.com/tax/set-up)
- [Tax registrations](https://docs.stripe.com/api/tax/registrations)
- [Revenue recovery](https://docs.stripe.com/billing/revenue-recovery)
- [Restricted API keys](https://docs.stripe.com/keys/restricted-api-keys)
