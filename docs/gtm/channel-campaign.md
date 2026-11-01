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
| MCP directories | [Channel release receipts](../releases/0.2.0.md) | Correct existing suitable entries before sending new submissions. |

Composio Claude skills had 78,510 stars at this check. Repository stars indicate
collection visibility, not impressions delivered to Openhook.

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
