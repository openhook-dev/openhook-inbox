# Openhook posting plan

Updated 2026-10-19. The Openhook-site guide and an X video thread are published;
external article and LinkedIn copy remain drafts. Publication receipts are tracked
in [DISTRIBUTION](../DISTRIBUTION.md).

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
| X | Founder video with implementation discussion and a reproducible callback example. | [Video published](https://x.com/berkant_thedev/status/2112272025305928045) October 19 in Build in Public; [setup reply](https://x.com/berkant_thedev/status/2112278190400163894) links the skill command and guide. Answer specific questions and measure referrals and external trials; respect the community's no-advertising rule. |
| LinkedIn | A single founder post with a real callback example. | Draft only; publishing account not selected. |

## Earlier X draft (superseded by the published video thread)

I maintain Openhook. Here's a small webhook test: create an inbox, send a callback, check that the original bytes match, then delete it.

Python standard library. No signup or paid plan.

https://openhook.dev/guides/callback-proof


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

## October 18 verification and measurement correction

The public walkthrough returned HTTP 200. Its Python example completed a real
HTTP capture, exact-byte comparison and inbox deletion on October 18. This was
maintainer QA, not customer adoption; exclude that run from external trial counts.

The live analytics script was still rejecting guide, about and contact page
visits despite those public pages loading the tracker. The accompanying fix
adds their exact published paths to the existing allowlist, preserving private
route rejection, query stripping and DNT/GPC. Deployment and receipt in Umami
must be verified separately. Historical guide visits cannot be recovered from
Umami, so previous website totals cover only the tracked public paths.

This fixes guide readership measurement only. A pageview or copy click does not
prove a completed callback or repeat usage. Anonymous activity still cannot
reliably distinguish outside developers from automated checks.

The short post above is ready; the publishing destination/account is awaiting
the user's selection. No external post has been published by this update.
