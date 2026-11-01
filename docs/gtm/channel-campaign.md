# Openhook channel campaign

Updated November 1, 2026 (Europe/Berlin). Targets are goals, not promised results.

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
| Composio Codex skills | [Existing PR #346](https://github.com/composio-community/awesome-codex-skills/pull/346), copied skill and evaluation prompts refreshed for channels | Await curator review. Structural validator passed; no model-driven evaluation claimed. |
| Agentic Awesome Skills | [Draft PR #2232](https://github.com/sickn33/agentic-awesome-skills/pull/2232), replaces the published retired callback instructions | Maintainer provenance review required for the updated source pin. This correction is not accepted yet. |
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

The external skill correction passed the catalog's full 2,910-skill validator,
reference checks, documentation security checks and 27 changed-skill evidence
tests. The complete preflight stopped at its source-pin provenance gate; that is
documented in the draft PR rather than represented as a pass or bypassed.

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
