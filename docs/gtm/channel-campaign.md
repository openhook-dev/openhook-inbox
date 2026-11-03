# Openhook channel campaign

Updated November 3, 2026 (Europe/Berlin). Targets are goals, not promised results.

## Outcome

Reach 20 earned GitHub stars and help three independent pairs of people exchange
messages through their own agents. Verify that at least one pair returns in a
later session. Stars, views and protocol demos are separate from adoption.

## Baseline

Live checks around 20:39 Berlin on November 1:

- Website: 14 tracked visitors / 16 pageviews today; 3 / 3 on October 31.
- Website, October 12–November 1: 82 tracked visitors / 119 pageviews.
- Today's pageviews: six from X and ten direct/unknown; none attributed to Reddit.
- GitHub: two stars and one fork. Latest traffic window October 18–31 UTC:
  25 unique visitors / 94 views. Today's traffic is delayed.
- Reddit repository post: 397 views, one reported comment, no shares.
- One historical external signup; no confirmed new external channel adoption.
- Zero recorded paid invoices/orders. Live provider reconciliation was not checked.

Analytics can include owner visits and internal QA. Public-page totals before the
measurement fix exclude the four channel use-case pages. Those missing visits
cannot be recovered. Local preview traffic must not use the production tracker;
exclude non-production hostnames when querying a website shared with old previews.

## Distribution

| Destination | Evidence | Next action |
| --- | --- | --- |
| r/coolgithubprojects | [Published repository post](https://www.reddit.com/r/coolgithubprojects/comments/1xl5d6q/openhook_selfhostable_channels_for_ai_agents/), no removal notice at the check | Read genuine questions; help people complete setup without unsolicited messages. |
| r/mcp | [Showcase submission](https://www.reddit.com/r/mcp/comments/1xl4kth/openhook_a_shared_channel_for_your_agent_and/) removed by Reddit's filters | Moderator review is needed; do not repost to evade the filter. |
| r/SideProject | [Use-case submission](https://www.reddit.com/r/SideProject/comments/1xl5e8f/i_want_my_agent_to_ask_my_partners_agent_without/) removed by Reddit's filters | Same moderation gate; no bulk reposting. |
| Composio Claude skills | [Existing PR #2218](https://github.com/ComposioHQ/awesome-claude-skills/pull/2218), channel description corrected | Await curator review; submission is not acceptance. |
| Composio Codex skills | [Existing PR #346](https://github.com/composio-community/awesome-codex-skills/pull/346), copied skill synchronized with native background delivery and WebMCP on November 3 | Open, awaiting curator review. Structural validation and exact source comparison passed; maintainer-run runtime results are linked, separately from catalog acceptance. |
| Agentic Awesome Skills | [PR #2232](https://github.com/sickn33/agentic-awesome-skills/pull/2232) merged November 2; channel instructions verified on main November 3 | Accepted correction to an existing listing, not a new destination or adoption. Its reviewed source pin predates the November 3 native-listener update. |
| TensorBlock MCP Index | [PR #5130](https://github.com/TensorBlock/awesome-mcp-servers/pull/5130) merged November 2; seven-tool metadata verified on main November 3 | Accepted correction to an existing listing. Separate hosted-profile deployment was not verified. |
| MCP directories | [Channel release receipts](../releases/0.2.0.md) | Correct existing suitable entries before sending new submissions. |

Composio Claude skills had 78,510 stars, Composio Codex skills 17,158, and Agentic
Awesome Skills 48,980 at this check. These are collection visibility signals,
not impressions delivered to Openhook or new accepted destinations.

## Shipped measurement fixes

[Openhook PR #74](https://github.com/openhook-dev/openhook-inbox/pull/74) merged
and deployed at `c6e1fa6ae9876990731c178204fe8312dd596137`. Both CI runs passed.
Local validation passed 56 Python tests, five analytics tests, frontend
typecheck/build and generated-docs checks. Browser verification confirmed prompt
copying and the intended GitHub destination.

The healthy running container's page renderer, tracker and homepage bundle hashes
match the tested files. Live HTML supplies all 11 canonical public paths and the
setup/star click annotations; private channel pages remain no-store/noindex with
no analytics. The seven-tool channel catalog remains available. A pre-deployment
container image is retained for rollback.

Before review, the external skill correction passed the catalog's full 2,910-skill validator,
reference checks, documentation security checks and 27 changed-skill evidence
tests. The complete preflight stopped at its source-pin provenance gate; that is
documented in the draft PR rather than represented as a pass or bypassed. The
maintainer subsequently merged that correction on November 2; the dated preflight
result above is not a current pending gate.

## Engineering funnel

1. A public page explains a concrete exchange between independently controlled agents.
2. The visitor can inspect the source or copy the setup prompt without an account.
3. A real peer joins with their own key and a real message reaches each agent.
4. The pair returns; useful users can choose to star or recommend the project.

Measure public routes from the server's canonical route catalog rather than a
separate manually maintained analytics list. Record only approved click names:
`connect-click`, `copy-setup-click`, `channels-click`, `source-click`, `star-click`.
A copy click is an attempt, not proof of successful copying, channel creation or
agent delivery. A star-link click is intent, not a verified GitHub star. Read
actual stars from GitHub and report its UTC traffic window and reporting delay.

Use the [first-channel feedback form](https://github.com/openhook-dev/openhook-inbox/issues/new?template=first-channel.yml)
to collect voluntarily shared client, hosting, listening and first-exchange
outcomes. Keep internal demos separate. A self-reported outcome is useful
feedback, not independently verified adoption; never solicit private transcripts
or capability keys as proof.

Keep private channels free of analytics. Strip query strings, fragments and
referrer paths; honor DNT/GPC. Never collect keys, invitations, message text or
member identities to attribute a campaign. Unknown/direct traffic stays unknown.

## Contribution bar

Use the current channel product and actual evidence. Disclose maintainer and AI
assistance where relevant. No purchased stars, star exchanges, installation-count
inflation or pretending to be a customer. Respect collection age, star and usage
requirements. Do not submit generated text to destinations that prohibit it.

Prioritize a reproducible first exchange and useful contributions over the number
of directory submissions. An accepted old callback listing must be corrected or
withdrawn if it no longer fits; it must not promote removed functionality.

## Captured CLI exchange — November 1

The [Claude Code ↔ Codex walkthrough](https://openhook.dev/guides/claude-code-codex)
contains a real model-driven question, reply, peer reads and final human-facing
summary. Claude Code 2.1.316 and Codex CLI 0.160.0 ran in separate folders on one
machine using the owner's existing subscriptions and synthetic briefs. Both used
the live remote MCP endpoint; the harness created and deleted the disposable
channel over HTTP. The successful run lasted 20:42:32–20:42:50 UTC.

The first attempt read the question but Codex's send was blocked by CLI approval
policy. It was not successful delivery. A second attempt explicitly preapproved
only the send tool for this synthetic test and completed. Both disposable
channels were deleted. No global permissions or listeners were installed.

The public JSON receipt allowlists message fields, tool names/statuses, peer
sequences read and final responses. It excludes member keys, invitations, member
IDs, raw arguments, private logs and reasoning. Publication checks reject
capability-shaped strings and require both peer reads and successful MCP sends;
a stored message or exit code zero is insufficient. Human review confirmed the
actual reply and summary. Raw run files remain private locally.

The branded video is a 74-second readable replay from those captured events,
with explicit internal-QA and synthetic-context labels. It is not a raw screen
recording. The guide includes reusable prompts, the CLI runner, foreground
listening limits and the lack of end-to-end encryption. It is linked from the
README, messaging use case, llms.txt and the automatically generated sitemap.
This is interoperability evidence, not independent adoption or idle wakeup proof.

### Publication receipts

- [Openhook PR #76](https://github.com/openhook-dev/openhook-inbox/pull/76) merged
  with both CI runs passing; deployed revision
  `0e78b84998e785949e85d787a4b25d55200cf568`. Container healthy; running renderer,
  guide and video hashes matched the tested files. Guide, JSON evidence, Markdown
  representation and sitemap returned 200; video range streaming returned 206.
  The seven-tool catalog and private-page no-store/noindex/no-analytics boundary
  remain intact. Local validation passed 58 Python tests, five analytics tests,
  frontend typecheck/build and generated-document checks.
- [X post with the replay attached](https://x.com/berkant_thedev/status/2116996785554010299)
  published from the owner's personal profile at 21:52 Berlin. X showed the media
  ready before publication and the embedded video on the public post afterward.
  No impression or conversion outcome is claimed from publication. Build in
  Public's visible rules prohibit product advertising, so this promotional post
  was not sent to that community.
- [RoggeOhta/awesome-codex-cli PR #537](https://github.com/RoggeOhta/awesome-codex-cli/pull/537)
  submitted as one README entry under Cross-Agent Tools. The collection had 562
  stars at discovery. Its rules require Codex relevance, maintenance, a clear
  unique value and a star badge; no minimum submitted-repository star count is
  stated. Checked for duplicates, disclosed affiliation/AI assistance and linked
  the real-client evidence. Open, no checks or curator acceptance at verification.
- The existing [Claude skills submission received the new evidence](https://github.com/ComposioHQ/awesome-claude-skills/pull/2218#issuecomment-6563731710),
  as did the existing [Codex skills submission](https://github.com/composio-community/awesome-codex-skills/pull/346#issuecomment-6563731935).
  Both remain open. These are substantive test updates, not new submissions,
  merges or published listings. No new external collection acceptance was verified.

Next: respond to real setup questions and help an independent pair complete this
walkthrough. Do not count these owner-run demo channels, CLI calls, post checks
or site QA visits as customer adoption. Larger star/usage-gated collections stay
deferred until their actual requirements are met.


## November 3 — targeted WebMCP distribution

Openhook's native WebMCP integration is merged and deployed through
[PR #83](https://github.com/openhook-dev/openhook-inbox/pull/83). It was verified
in native Chrome 156 against localhost and the live HTTPS channel page, using
synthetic channels that were deleted. These checks are internal QA, not adoption.

### Published Reddit contributions

- [r/ClaudeCode weekly showcase](https://www.reddit.com/r/ClaudeCode/comments/1xlurut/comment/19s33rvtdkurn/):
  shared the cross-person agent channel use case, the actual Claude Code/Codex
  workflow and its running-listener limitation. Links point to the repository
  and the walkthrough. The current pinned thread explicitly permits project
  sharing and simple self-promotion. No earlier Openhook mention was present.
- [r/WebMCP_Developers benchmark discussion](https://www.reddit.com/r/WebMCP_Developers/comments/1wino2z/comment/19s33ibzm84io/):
  contributed permission/refusal, revocation and duplicate-write evaluation
  cases, referencing the implementation notes. No model speedup or token-savings
  claim. Maintainer affiliation and AI assistance were disclosed in both comments.

Both comments were visibly present at their direct permalinks in the signed-in
browser, without a removal notice at verification. Anonymous visibility was not
established: the alternate browser also carried an authenticated session, the
public web fetch returned a cache miss, and a genuine incognito visit hit Reddit's
"Prove your humanity" gate. No challenge was completed or bypassed. This is
publication evidence in the owner session, not curator
endorsement, search indexing, new visitors, stars or confirmed product use.

### Submitted listings — pending curator review

- [webmachinelearning/awesome-webmcp #75](https://github.com/webmachinelearning/awesome-webmcp/pull/75):
  README-only Websites entry, following CONTRIBUTING.md. The collection had 61
  stars at discovery. Open, mergeable, no checks or acceptance at verification.
- [webfuse-com/awesome-webmcp #44](https://github.com/webfuse-com/awesome-webmcp/pull/44):
  one Community Demos entry. The collection had 174 stars at discovery. Open,
  mergeable, no checks or acceptance at verification.

Both submissions link the deployed implementation and explain native browser
verification, optional support and security limits. Affiliation and AI assistance
are disclosed. They are proposals, not merged listings or endorsed backlinks.

A WebMCP.com scan/listing request was also started for
`https://openhook.dev/channels`, using the public business support address. The
UI remained at "Starting scan" / "Reaching your site" after more than five
minutes, with zero pages scanned. Completion and directory acceptance have not
been verified. Its listing policy requires automated checks and human review.
Do not count it as a published listing or repeatedly submit the same request.

### Qualified conversations held back

- [r/AI_Agents: Multi-Agent Communication](https://www.reddit.com/r/AI_Agents/comments/1xgr8ol/multiagent_communication/)
  and [Cross-harness agents messaging](https://www.reddit.com/r/AI_Agents/comments/1x3ef9d/crossharness_agents_messaging/):
  close product fit, but the community limits self-promotion to approximately
  one in ten contributions and the account is already promotion-heavy. No link
  was posted. Do not manufacture filler comments to satisfy a quota.
- [r/codex: Best way to get Codex and Claude Code working together?](https://www.reddit.com/r/codex/comments/1x805d9/best_way_to_get_codex_and_claude_code_working/):
  relevant, but the community explicitly says not to use bots. No automated
  comment was submitted.
- r/OpenSourceProjects is restricted and its visible posts are years old; no
  posting-access request was sent.

The existing [r/coolgithubprojects post](https://www.reddit.com/r/coolgithubprojects/comments/1xl5d6q/openhook_selfhostable_channels_for_ai_agents/)
showed 553 views, zero displayed upvotes, one comment and no shares in its owner
insights. These are dated exposure figures, not website visitors or adoption.

Next: answer genuine replies to the showcase, help an independent pair complete
its first exchange, and handle curator feedback on the two new PRs. Do not
repost removed submissions, repeat the same promotion, buy stars or count
internal tests as outside use.

## November 3 — additional channel and skill distribution

Three further README-only proposals were submitted after reading each available
contribution guide and checking the list and existing PRs for duplicates:

| Collection | Submission | Stars at check | Verified state |
| --- | --- | --- | --- |
| karanb192/awesome-claude-skills | [PR #643](https://github.com/karanb192/awesome-claude-skills/pull/643) | 583 | Open, mergeable, no checks or review yet. |
| commune-dev/awesome-agent-protocols | [PR #10](https://github.com/commune-dev/awesome-agent-protocols/pull/10) | 3 | Open, mergeable, no checks or review yet. |
| masstensor/awesome-agent-collaborate-tools | [PR #6](https://github.com/masstensor/awesome-agent-collaborate-tools/pull/6) | 2 | Open, mergeable, no checks or review yet. |

The Claude entry links the canonical skill folder, sits alphabetically under
Collaboration & Workflow and has a 99-character task description. Its previous
Claude-testing eligibility gap is now covered by maintainer-run runtime evidence
in docs/testing.md and the captured walkthrough. The broad no-vulnerabilities
checkbox is deliberately left unchecked with an explanation; passing tests do
not establish an absence of all vulnerabilities. The other entries describe
messaging, not a new protocol standard or orchestration framework. The two tiny
collections are exact subject matches, not major reach claims. All three disclose
maintainer affiliation, AI assistance, server-readable messages and QA limits.
The masstensor README links a CONTRIBUTING.md absent from its default branch;
its inline maintenance, relevance and open-source/free-tier criteria were used.
One-line diffs, formatting and public documentation links were checked.

### Existing larger submission improved

[Composio Codex skills #346](https://github.com/composio-community/awesome-codex-skills/pull/346)
was updated in place at `47b03e89ff6e4f368ae595da4e03eba31bdd0cbd`.
The submitted SKILL.md now matches the canonical Openhook skill byte for byte;
its existing evaluation cases were retained and native-host, notification-trust,
uncertain-delivery and WebMCP scenarios added. Standard skill validation and
`git diff --check` passed. The collection had 17,180 stars at verification.
The [reviewer update](https://github.com/composio-community/awesome-codex-skills/pull/346#issuecomment-6609503899)
explains the substantive changes and actual runtime evidence; this is not a new
submission or acceptance. The PR remains open.

### Prior corrections now accepted

- [Agentic Awesome Skills #2232](https://github.com/sickn33/agentic-awesome-skills/pull/2232)
  merged on November 2 at 07:58 UTC, commit `4b9b4974f8d537d4b0f7fc5f55df733a4dd4949c`.
  Verified the channel-oriented skill and reviewed source pin on main. The
  collection had 49,088 stars. Its catalog-assigned risk label is not a security
  certification, and its source pin does not yet contain the newest native
  background receiver. Do not bypass the catalog's provenance review for a refresh.
- [TensorBlock #5130](https://github.com/TensorBlock/awesome-mcp-servers/pull/5130)
  merged on November 2 at 09:12 UTC, commit `45db3ec196b506b081249eaff6767156b9d89e5e`.
  Verified main-branch metadata lists the seven channel tools, invitation/member
  authentication and no-E2EE boundary. The collection had 1,025 stars. Its bot
  supplied a hosted-profile URL, but that separate site's deployment could not be
  verified by the web fetch; do not claim it is live based only on the bot comment.

These are accepted updates to destinations that already listed Openhook. They
were discovered in this audit, not newly merged by this outreach batch. Collection
stars measure potential audience, not delivered impressions or earned Openhook
stars. No new independent customer or product-use claim follows from this work.

### Further eligibility checks

EvoMap/awesome-agent-swarm requires 50 project stars, with curator exceptions for
novel projects. No exception was assumed and no submission was made. The Claude
Code mods collection specifically accepts JavaScript/TypeScript function-hook
mods; Openhook's shell/native receiver is not represented as such a mod.

The older jezweb #50 review was reread. Its model-test gap is now covered, but the
repository has since moved to a different plugin/skill shape. No duplicate or
unadapted resubmission was sent. The 57,167-star hesreallyhim collection still
requires a human web-form recommendation; no automated submission was made.

The current r/mcp rules explicitly warn against AI-generated promotion disguised
as security discussion. No product pitch was inserted into its fresh security
thread. r/opensource also prominently announces a no-AI policy; no automated
post was sent. The existing Claude Code showcase remained visible, with no new
direct reply visible at this check; it was not reposted or bumped.
