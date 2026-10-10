# Open-source launch and first paid customers

Status: preparation, not a claim of launch or customer demand.

## Positioning

“An inbox your coding agent can use to finish webhook integrations.”

Show a useful loop: create a URL → send a real provider test event → inspect it
through MCP → forward it to a local handler. Keep the demo under two minutes.
The hosted upgrade preserves addresses and account access across working sessions.

Avoid “first”, “only”, “guaranteed”, and automatic Codex wake-up claims. Existing
webhook tools already support agents. Openhook's offer is a small MIT-licensed
service combining native HTTP/email/DNS capture, MCP, and local forwarding.

## Distribution sequence

1. Repository: clear quickstart, three recipes, contribution and security guidance,
   MIT license, and an honest hosted link. A stranger should receive one callback
   without reading implementation code or creating an account.
2. Demo: record one actual callback and local handler invocation using disposable
   payloads. Hide tokens and credentials; show both hosted and self-hosted setup.
3. Founder channels: publish the working demo and ask developers building webhook
   integrations to try it. Obtain approval for the exact account/channel and copy.
4. Relevant communities: tailor a useful technical walkthrough to community rules;
   disclose authorship and do not automate unsolicited mass posting or replies.
5. Ten qualified developer sessions: observe a real integration, the second use,
   and whether persistent endpoints solve a problem they would pay $19/month for.
6. After live billing validation, seek 3–5 actual paid customers. Record feedback,
   recurring use, cancellations, support time, and contribution margin.

Do not buy ads before activation and repeat usage work. Do not require a star or
email signup to access the open-source product. Do not call free accounts paying
customers or turn compliments into revenue forecasts.

## Founder post draft — free core available, Pro not launched

I built Openhook because my coding agent could write a webhook handler, but still
needed a public place to receive the callback while I worked locally.

Openhook gives it an inbox through MCP: create a URL, inspect the actual payload,
then forward it to a local handler. It also receives email and DNS callbacks.
The Python service and local listener are MIT-licensed and self-hostable.

Try it without an account: https://openhook.dev/
Source: https://github.com/openhook-dev/openhook-inbox

I'm preparing an optional hosted plan for persistent inboxes and saved account
access. If you're building a webhook integration with a coding agent, I'd like to
watch where the workflow helps or gets in your way.

## Launch post draft — use only after live billing and operator checks

Openhook is an open-source webhook inbox for coding agents. Give your agent a
public URL, inspect callbacks through MCP, and forward them to your local app.
HTTP, email, and DNS capture run in the same self-hostable Python service.

The core is MIT-licensed. Free temporary hosted inboxes need no account.
Hosted Pro is $19 USD/month plus applicable tax: 10 persistent inboxes, 50,000
events per calendar month, 30-day retention, and up to 1 GiB of stored event data.

Demo and plans: https://openhook.dev/pricing
Source: https://github.com/openhook-dev/openhook-inbox

## Developer session script

- What integration are you building, and how do you receive its callbacks today?
- Try the free workflow on your own task without guidance. Record where you stall.
- Return after a few days. Does losing the endpoint or finding the private token
  interrupt real work? How often does that happen?
- Show the exact hosted offer. Ask whether they want to purchase it when available.
  A stated intention is a lead; only a real payment is paid conversion.
- If they decline, ask why once. Improve or narrow the offer rather than discounting
  immediately. Stop contacting anyone who declines further contact.

## Weekly scorecard

Keep a dated local/customer-approved record with counts and denominators:
qualified sessions, developers receiving a first real callback, 7-day return use,
checkout attempts, successful first paid invoices, retained paying customers,
cancellations, cash collected, refunds, hosting costs, and support hours.

The read-only `scripts/business_report.py` provides the current database's account,
usage, and invoice aggregates. Paid-through access is not MRR: a canceled customer
can retain paid time. Reconcile recurring subscription status, refunds, processor
fees, and taxes in Stripe before reporting revenue or contribution margin.

Decision gate after the first ten sessions: if fewer than three developers want
to pay and repeated use is weak, revisit the target workflow and offer before
building teams, SSO, integrations, or higher plans. These are experiment thresholds,
not evidence that the market will convert.
