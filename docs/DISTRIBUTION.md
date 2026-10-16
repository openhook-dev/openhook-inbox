# Openhook distribution tracker

Last checked: 2026-10-16 (Europe/Berlin). Submission does not mean curator acceptance or new users.

## Published installation

The [agent skill](../skills/openhook/README.md) is public on main through
[PR #10](https://github.com/openhook-dev/openhook-inbox/pull/10).

```sh
npx skills add openhook-dev/openhook-inbox --skill openhook
```

Verified public discovery with `npx skills add openhook-dev/openhook-inbox --list`.
The project passed 97 Python tests and the generated-docs check. Both CI runs
passed before merge. The hosted first-callback example successfully sent and read
a matching payload, then cleaned up its disposable inbox again on 2026-10-14.

## Official MCP Registry

Published version `0.1.0` of `io.github.openhook-dev/openhook-inbox` and verified
its [public registry record](https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.openhook-dev/openhook-inbox)
is `active` and latest. It points to `https://openhook.dev/mcp`, this repository,
and the Openhook website. Publication completed in
[workflow run 38479763582](https://github.com/openhook-dev/openhook-inbox/actions/runs/38479763582)
using GitHub workload identity. Registry presence is not a security certification
or evidence of customer adoption. See [releasing](releasing.md) for updates.

## Submissions

| Destination | Status and evidence | Next step |
| --- | --- | --- |
| BehiSecc/awesome-claude-skills | [PR #952](https://github.com/BehiSecc/awesome-claude-skills/pull/952) submitted as one Development & Code Tools entry linking directly to the skill. 10,255 stars at the 2026-10-16 check. Maintainer affiliation and AI assistance disclosed. | Await curator review; submission is not publication. |
| ripienaar/free-for-dev | [PR #5001](https://github.com/ripienaar/free-for-dev/pull/5001) submitted under Testing at the user's explicit request after explaining the repository's ban on AI-written submissions. Template AI checkbox checked and AI assistance disclosed. Public free limits, pricing, contact and privacy pages verified; one README addition. 139,603 stars at the 2026-10-16 check. | Open at verification; acceptance is unlikely under its stated policy. Do not conceal authorship, resubmit after rejection, or argue with maintainers. |
| libukai/awesome-agent-skills | [PR #198](https://github.com/libukai/awesome-agent-skills/pull/198) submitted under Programming & Development with matching Chinese, English and Japanese entries pointing to the canonical skill. 5,173 stars at the 2026-10-16 check. Maintainer and AI assistance disclosed. | Await curator review; three focused additions and duplicate check verified. |
| YuzeHao2023/Awesome-MCP-Servers | [PR #646](https://github.com/YuzeHao2023/Awesome-MCP-Servers/pull/646) submitted as one Development Tools entry. 1,074 stars at the 2026-10-16 check. Hosted/self-hosted operation and per-inbox authorization explained in the PR. | Await maintainer review and verify default-branch publication. |
| MCP.so | [Submission comment](https://github.com/chatmcp/mcpso/issues/1#issuecomment-6204523280) posted in its designated public submission thread on 2026-10-16. Source, docs, endpoint, feature scope and authorization boundaries included. Existing-issue search found no Openhook submission. | Await directory publication; the comment is a receipt, not a live mcp.so listing. |
| mcpHQ/awesome-mcp-servers | [PR #278](https://github.com/mcpHQ/awesome-mcp-servers/pull/278) submitted under Developer Tools and Code Intelligence, with hosted endpoint metadata and generated README/LLM catalogs. Local validation and generated-file checks passed: 327 entries across 13 categories. | Await maintainer review; submission is not publication on mcphq.org. |
| MobinX/awesome-mcp-list | [PR #793](https://github.com/MobinX/awesome-mcp-list/pull/793) submitted as one README bullet under Developer Tools. Exact required format, public source, duplicate check and focused diff verified. 892 stars at the 2026-10-16 check. | Await maintainer review and verify default-branch publication. |
| ComposioHQ/awesome-claude-skills | [PR #2218](https://github.com/ComposioHQ/awesome-claude-skills/pull/2218) open in Development & Code Tools. Listing validation and Socket checks passed; repository automation applied `ready-to-merge`. 77,048 stars at the 2026-10-14 check. | Await maintainer merge; the label is not acceptance or publication. |
| yzfly/Awesome-MCP-ZH | [PR #733](https://github.com/yzfly/Awesome-MCP-ZH/pull/733) **merged 2026-10-15**. Openhook entry verified on the default-branch README on 2026-10-16. 7,731 stars at this check. | Published repository listing; measure referral and product activity separately. |
| rohitg00/awesome-devops-mcp-servers | [PR #365](https://github.com/rohitg00/awesome-devops-mcp-servers/pull/365) submitted under Testing & Chaos Engineering, with Python and hosted/self-hosted scope icons. Maintainer affiliation and AI assistance disclosed. CodeRabbit's check passed with no actionable changes, but its [comment](https://github.com/rohitg00/awesome-devops-mcp-servers/pull/365#issuecomment-6162889166) flags possible promotional spam. | Await human maintainer review; do not duplicate or auto-reply to the bot. |
| TensorBlock/awesome-mcp-servers | [PR #3674](https://github.com/TensorBlock/awesome-mcp-servers/pull/3674) **merged 2026-10-14**. Openhook metadata verified on the upstream default branch on 2026-10-16. Catalog validation before submission built 8,493 entries with zero errors. | Verify hosted catalog deployment separately; upstream merge is confirmed. |
| agentskillexchange/skills | [PR #113](https://github.com/agentskillexchange/skills/pull/113) open. Skill metadata validator and 79-pattern security scan passed with no findings. Maintainer affiliation disclosed; verification level is `listed`. | Respond to curator feedback; verify after merge. |
| OpenAgentSkill | [Submission form](https://www.openagentskill.com/submit) confirmed saved for review; receipt `a9f8ce40`. Human review required for credential instructions and network execution. | Follow the existing receipt; submission is not publication or installation approval. |
| Skillboard | [Submission form](https://www.skillboard.lol/submit) confirmed “Thanks – submitted for review.” Canonical skill directory submitted. | Check for curator publication; do not resubmit while pending. |
| AgentNDX | [Submission form](https://agentndx.ai/submit/) confirmed “Submission received.” MCP server submitted with maintainer disclosure; optional contact email omitted. | Check after its stated 48-hour review window; publication is not yet verified. |
| MCP.Directory | [Submission form](https://mcp.directory/submit) confirmed “Server Submitted!” Repository and description submitted; optional email and unpublished package names omitted. | Check after its stated 24-hour review window; reconcile with any official Registry import. |
| heilcheng/awesome-agent-skills | [PR #586](https://github.com/heilcheng/awesome-agent-skills/pull/586) open under Community Skills / Development and Testing; local required website build passed. Vercel's preview check is blocked on authorization by the collection owner's team, per its [bot comment](https://github.com/heilcheng/awesome-agent-skills/pull/586#issuecomment-6151302619). | Maintainer must authorize their preview; respond to review and verify after merge. |
| junminhong/awesome-agent-skills | [PR #73](https://github.com/junminhong/awesome-agent-skills/pull/73) **merged 2026-10-15**. English Openhook skill entry verified on the default branch on 2026-10-16. | Published repository listing; measure independent installation and usage separately. |
| realadeel/awesome-webhooks | [PR #91](https://github.com/realadeel/awesome-webhooks/pull/91) open under Development Tools. | Respond to maintainer feedback; verify after merge. |
| punkpeye/awesome-mcp-servers | [PR #16343](https://github.com/punkpeye/awesome-mcp-servers/pull/16343) drafted. Its submission bot additionally requires Glama validation and a real badge. | Complete free Glama setup and server validation, add its actual badge, then mark ready. |
| mcpservers.org | **Published** [Openhook listing](https://mcpservers.org/servers/openhook-dev/openhook-inbox), verified publicly on 2026-10-16. Includes the hosted endpoint, skill installation and source link. | Measure referral traffic and independent usage separately; no resubmission needed. |
| ClawHub openhook-cli | Existing listing is still 1.0.2. Corrected 2.0.0 package prepared, but publishing was rejected pending MIT-0 terms acceptance. No new version was published. | Obtain explicit approval for MIT-0 skill publication and the new read-only organization scope requested by browser login; complete setup and retry once. |

Glama authentication and any new account terms require approval before completing
that setup. No Glama listing, passing grade, or badge is claimed yet.

## Existing third-party discovery

The [M8ven Trust Index listing](https://m8ven.ai/mcp/openhook-dev/openhook-inbox)
was verified publicly on 2026-10-13. M8ven found the repository through GitHub
search; this was not a submission from this campaign. The listing remains
unclaimed and live monitoring is not connected.

It displays 74/100 (grade C) for commit `f6ac7c7`, scanned on 2026-10-11.
M8ven reports no concerning findings and says new projects are capped at C
until they earn adoption. This is their static assessment of an older commit,
not a current-release security guarantee or evidence of independent users.

On 2026-10-16, GitHub confirmed merges for Awesome-MCP-ZH, TensorBlock and
junminhong. Composio, heilcheng, realadeel, DevOps MCP and Agent Skill Exchange
still appeared in the open-PR search. Composio was additionally checked directly:
validation and Socket checks passed, with no human comments or reviews. Check
individual reviews before following up.

## Deferred destinations

- [awesome-selfhosted/awesome-selfhosted-data](https://github.com/awesome-selfhosted/awesome-selfhosted-data/blob/master/CONTRIBUTING.md)
  requires a first release older than four months. Openhook does not yet qualify;
  no submission on 2026-10-16.
- [karanb192/awesome-claude-skills](https://github.com/karanb192/awesome-claude-skills/blob/main/CONTRIBUTING.md)
  requires testing the skill with Claude. Protocol-level MCP checks do not satisfy
  that attestation; no submission on 2026-10-16.

- [jaw9c/awesome-remote-mcp-servers](https://github.com/jaw9c/awesome-remote-mcp-servers)
  (1,145 stars at the 2026-10-16 check): contribution rules require MCP OAuth
  and evidence of production use and an active community. Openhook uses private
  per-inbox tokens rather than MCP OAuth; no submission or compatibility claim.
- Christian-Sidak/awesome-mcp-tools (0 stars) and Sagargupta16/awesome-mcp-servers
  (7 stars) were inspected on 2026-10-16 and deprioritized for audience reach.

- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code/blob/main/CONTRIBUTING.md)
  (55,642 stars): recommendations must be made by a human through its web issue
  form. Also requires 14 days of default-branch history plus subsequent development,
  or 100 stars. Openhook currently has zero stars and its repository was created
  on 2026-10-03. No automated submission; confirm first-commit age before a future
  human recommendation.
- [github/awesome-copilot](https://github.com/github/awesome-copilot/blob/main/CONTRIBUTING.md)
  (39,998 stars): a relevant skill contribution is possible, but its checklist
  requires actual testing with GitHub Copilot. Current protocol-level validation
  is not a Copilot test; no submission or checked testing attestation.
- [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills/blob/main/CONTRIBUTING.md)
  (15,396 stars): requires at least 10 stars and prohibits AI-assisted submissions.
  No automated contribution; do not disguise authorship or buy stars.
- dipakkr/awesome-ai-engineering (22,380 stars): inspected default-branch content
  is primarily a broad student/developer resource list. No strong matching MCP
  category was found; deprioritized despite its star count.
- block/agent-skills is archived as checked on 2026-10-14; no submission.
- JackyST0/awesome-agent-skills requires 64 GitHub stars by default; defer until
  eligibility is established rather than requesting an exception for promotion.
- [Launch MCP](https://launchmcp.co/submit): duplicate check found no listing or
  pending submission. Free submission is prepared but was blocked by automatic
  approval review because it requires sending the support email to a new third
  party. Await specific approval; no submission occurred.
- [Skills Directory](https://www.skillsdirectory.com/): submission redirects to
  sign-in/account creation. No account or listing was created.
- [PulseMCP](https://www.pulsemcp.com/): homepage explicitly says new server
  submissions and listing changes are paused. Revisit when submissions reopen.
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills):
  requires established community usage. Revisit when independent usage can be
  demonstrated; do not represent internal testing as adoption.
- [punkpeye/awesome-remote-mcp-servers](https://github.com/punkpeye/awesome-remote-mcp-servers):
  requires a Glama connector listing and resolving badge. Revisit after validation.
- appcypher/awesome-mcp-servers is archived; no submission.
- wong2/awesome-mcp-servers directs submissions to mcpservers.org and does not
  accept listing PRs. The website submission above follows that route.

## Submission conventions

Read each destination's current contribution rules and search for existing
entries and PRs before submitting. Use factual descriptions, disclose maintainer
affiliation, and keep one relevant project per contribution. No paid placement
or fabricated usage claims. Track approvals separately from submissions.

Canonical source: https://github.com/openhook-dev/openhook-inbox

Hosted MCP endpoint: https://openhook.dev/mcp

Suggested description: Open-source webhook inbox with an MCP interface for AI
agents to capture callbacks, inspect payloads, and forward events to local handlers.

For acquisition measurement, compare referral traffic in Umami with new account
and product-usage evidence. Page views, internal QA, and anonymous test inboxes
are not proof of independent users or paid customers.

## Articles and social posts

The [callback-proof guide](https://openhook.dev/guides/callback-proof) is live
on Openhook's site as of 2026-10-16, merged in [PR #19](https://github.com/openhook-dev/openhook-inbox/pull/19)
and deployed as `13e723e`. HTML, canonical metadata, article schema, sitemap,
Markdown response and the real MCP callback loop were verified. Google Search
Console accepted an indexing request for the guide and resubmission of the updated
14-URL sitemap on 2026-10-16; acceptance is not confirmed indexing. The [posting
plan](gtm/posting-plan.md) includes X and LinkedIn drafts and two follow-on article
experiments. No social post or cross-post has been published to an external
account; the intended account is still pending. HN requires human-written posts;
DEV's published AI-content policy restricts business promotion.

## High-visibility campaign

Prioritize audience fit and a valid contribution path alongside star count.
Stars are a reach proxy, not measured impressions or users. Existing larger
channels include punkpeye/awesome-mcp-servers (96,311 stars; Glama gate),
VoltAgent/awesome-agent-skills (35,675 stars; proven-usage gate), and
heilcheng/awesome-agent-skills (6,273 stars; existing PR awaiting review).
Counts are a dated snapshot from 2026-10-14.

Before the new high-visibility submissions, a direct MCP SDK check successfully
initialized the hosted connection, discovered tools, created a disposable inbox,
sent a real synthetic HTTP callback, waited with `since: 0`, verified exact body
bytes, and deleted the inbox. Tokens were not printed. This establishes protocol
behavior, not a Claude or Copilot UI test or independent adoption.

External maintainers control their merges. Address actionable review feedback
and verify default-branch publication; do not request collaborator privileges,
bypass branch protection, or merge a fork and call it upstream acceptance.
