# Openhook posting plan

Updated 2026-10-16. The Openhook-site guide is published; social and cross-post
copy remain drafts. Publication receipts are tracked in [DISTRIBUTION](../DISTRIBUTION.md).

## First article

Published on Openhook's site: [Prove a webhook arrived before your agent continues](https://openhook.dev/guides/callback-proof).
Use that verified live URL as the canonical URL for any later cross-post. The
[long-form draft](callback-proof-article.md) remains available for adapting to a
selected external account. The callback example and live guide were verified
on 2026-10-16.

The user has been asked which publishing account to use. No external publishing
account has been selected or authenticated for this article.

## Channels and current rules

| Channel | Suitable contribution | Current next step |
| --- | --- | --- |
| Openhook site | Callback-proof walkthrough published, linked from the guide index, tool docs and llms.txt. | Live URL and deployment verified on 2026-10-16; measure readers and first-callback outcomes. |
| Hashnode | One original technical article, reviewed by the maintainer, with affiliation and AI-assistance disclosure. | Select/sign in to the author's account, review the prepared article, then publish. [Code of conduct](https://hashnode.com/code-of-conduct) permits reviewed AI content but rejects bulk posting and primarily promotional use. |
| DEV Community | A human-owned technical contribution subject to its AI content rules. | Do not publish this GTM draft: [AI guidelines](https://dev.to/devteam/guidelines-for-ai-assisted-articles-on-dev-17n6) say AI-assisted articles should not promote a business. Its newer [disclosure tiers](https://dev.to/devteam/introducing-ai-disclosure-on-dev-tools-for-nuance-clarity-and-better-feeds-34mk/) do not remove that restriction. |
| Hacker News / Show HN | The working product with a personal explanation from its maker; direct demo access. | Author must write and submit their own text. [HN guidelines](https://news.ycombinator.com/newsguidelines.html) prohibit generated text and automated posting; [Show HN](https://news.ycombinator.com/showhn.html) excludes blog posts and signup-only pages. Do not paste the drafts here. |
| X or LinkedIn | A single founder post with a real callback example and a clear invitation to try it. | Select the intended account and review the corresponding copy below. No account-specific post has been submitted. |

## Short X draft

I maintain Openhook: an MIT-licensed webhook inbox for coding agents. Create a URL,
send a callback, and inspect it through MCP. Free temporary inboxes need no account.
Try the working example: https://github.com/openhook-dev/openhook-inbox

## LinkedIn draft

A coding agent can write a webhook handler without ever receiving a real callback.

I maintain Openhook, an open-source inbox that gives the agent a public callback
URL and private access to the captured events through MCP.

The quickstart creates a disposable inbox, sends a synthetic HTTP callback,
compares the original bytes, and cleans up. It needs Python and Git, with no
hosted account required.

The distinction that matters: a received callback proves capture. It does not
prove your application handled the event. The next test is forwarding a fresh
provider sandbox event to your local handler and checking the resulting state.

If you're building a webhook integration with a coding agent, try the example
on your current task. Feedback about where you get stuck would be useful.

https://github.com/openhook-dev/openhook-inbox

Draft prepared with AI assistance; technical example verified on 2026-10-14.

## Follow-on article ideas

- **Why a webhook's 200 response is not end-to-end delivery proof:** show an
  actual failed local handler, a retry, and deduplication. Run and record that
  experiment before writing a claim that it happened.
- **Resuming an agent's callback wait without losing events:** use the current
  cursor API to demonstrate an event arriving before a wait and resuming after
  timeout. Include cleanup and explain the stopped-session limitation.

## Measure the outcome

Record each published URL, date, canonical URL, and channel in the distribution
tracker. The current privacy filter strips URL queries and referrer paths before
sending analytics, so UTM query parameters alone do not establish campaign
attribution. Use available referring domains for now; direct visits can remain
unattributed. Any future campaign measurement needs explicit implementation and
verification without collecting tokens or personal identifiers. Compare referrals
with first real callback and return-use evidence. Exclude the maintainer's demo
runs from adoption counts.
