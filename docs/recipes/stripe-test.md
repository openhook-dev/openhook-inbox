# Inspect a Stripe test callback

This recipe tests **your integration**, separately from Openhook's own hosted
billing. Use a dedicated Stripe sandbox/test-mode credential; do not run a real
payment for this example.

Connect [the hosted MCP endpoint](https://openhook.dev/connect), or connect to your
public self-hosted Openhook server. Call `register_stripe_webhook` with a provider
credential that can create webhook endpoints and `events: ["payment_intent.succeeded"]`.
The result includes a public endpoint and private inbox token. Registration stores
the endpoint signing secret; it does not store your provider API credential.

Produce a `payment_intent.succeeded` event in that same sandbox using Stripe's test
workflow. Use `wait_for_request` followed by `get_request` to confirm the event type,
object identifier, and `livemode: false`. The registered inbox checks Stripe's raw
body signature and timestamp before accepting it. Re-delivery of the same retained
event is deduplicated by the Stripe event ID.

Forward accepted events to your local handler using [the listener](local-handler.md).
Verify the handler's own result separately. Delivery is at least once, so its
business operation still needs idempotency.

Finish with `unregister_webhook` and remove disposable inbox data. Keep the API
credential and endpoint signing secret out of screenshots and example code.
