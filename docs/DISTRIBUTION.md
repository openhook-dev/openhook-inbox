# Openhook distribution tracker

Last checked: 2026-10-14 (Europe/Berlin). Submission does not mean curator acceptance or new users.

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
| ComposioHQ/awesome-claude-skills | [PR #2218](https://github.com/ComposioHQ/awesome-claude-skills/pull/2218) open in Development & Code Tools. Listing validation and Socket checks passed; repository automation applied `ready-to-merge`. 77,048 stars at the 2026-10-14 check. | Await maintainer merge; the label is not acceptance or publication. |
| yzfly/Awesome-MCP-ZH | [PR #733](https://github.com/yzfly/Awesome-MCP-ZH/pull/733) open in Development & Code Execution. Chinese description, license, runtime and authorization details included. 7,728 stars at the 2026-10-14 check. | Respond to review; verify the default-branch listing after merge. |
| rohitg00/awesome-devops-mcp-servers | [PR #365](https://github.com/rohitg00/awesome-devops-mcp-servers/pull/365) submitted under Testing & Chaos Engineering, with Python and hosted/self-hosted scope icons. Maintainer affiliation and AI assistance disclosed. CodeRabbit's check passed with no actionable changes, but its [comment](https://github.com/rohitg00/awesome-devops-mcp-servers/pull/365#issuecomment-6162889166) flags possible promotional spam. | Await human maintainer review; do not duplicate or auto-reply to the bot. |
| TensorBlock/awesome-mcp-servers | [PR #3674](https://github.com/TensorBlock/awesome-mcp-servers/pull/3674) submitted under Developer Productivity & Utilities. Includes structured metadata distinguishing unauthenticated MCP connection from private per-inbox authorization. Catalog build: 8,493 entries, zero errors; generated Openhook record verified. | Respond to review; verify the hosted catalog profile after merge/deployment. |
| agentskillexchange/skills | [PR #113](https://github.com/agentskillexchange/skills/pull/113) open. Skill metadata validator and 79-pattern security scan passed with no findings. Maintainer affiliation disclosed; verification level is `listed`. | Respond to curator feedback; verify after merge. |
| OpenAgentSkill | [Submission form](https://www.openagentskill.com/submit) confirmed saved for review; receipt `a9f8ce40`. Human review required for credential instructions and network execution. | Follow the existing receipt; submission is not publication or installation approval. |
| Skillboard | [Submission form](https://www.skillboard.lol/submit) confirmed “Thanks – submitted for review.” Canonical skill directory submitted. | Check for curator publication; do not resubmit while pending. |
| AgentNDX | [Submission form](https://agentndx.ai/submit/) confirmed “Submission received.” MCP server submitted with maintainer disclosure; optional contact email omitted. | Check after its stated 48-hour review window; publication is not yet verified. |
| MCP.Directory | [Submission form](https://mcp.directory/submit) confirmed “Server Submitted!” Repository and description submitted; optional email and unpublished package names omitted. | Check after its stated 24-hour review window; reconcile with any official Registry import. |
| heilcheng/awesome-agent-skills | [PR #586](https://github.com/heilcheng/awesome-agent-skills/pull/586) open under Community Skills / Development and Testing; local required website build passed. Vercel's preview check is blocked on authorization by the collection owner's team, per its [bot comment](https://github.com/heilcheng/awesome-agent-skills/pull/586#issuecomment-6151302619). | Maintainer must authorize their preview; respond to review and verify after merge. |
| junminhong/awesome-agent-skills | [PR #73](https://github.com/junminhong/awesome-agent-skills/pull/73) open; matching English/Chinese entries; GitHub-verified commit. | Respond to maintainer feedback; verify the listing after merge. |
| realadeel/awesome-webhooks | [PR #91](https://github.com/realadeel/awesome-webhooks/pull/91) open under Development Tools. | Respond to maintainer feedback; verify after merge. |
| punkpeye/awesome-mcp-servers | [PR #16343](https://github.com/punkpeye/awesome-mcp-servers/pull/16343) drafted. Its submission bot additionally requires Glama validation and a real badge. | Complete free Glama setup and server validation, add its actual badge, then mark ready. |
| mcpservers.org | Free MCP submission accepted by the [submission form](https://mcpservers.org/submit); success screen named Openhook. Review estimate: within two weeks. | Check hello@openhook.dev for review outcome; do not resubmit while pending. |
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

No new human maintainer feedback was present on the three earlier review-ready
collection PRs at the latest 2026-10-14 check. The Agent Skill Exchange PR also
had no feedback at submission. Check existing receipts and PRs before following up.

## Deferred destinations

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

The [posting plan](gtm/posting-plan.md) includes one complete callback tutorial,
short X and LinkedIn drafts, two follow-on article experiments, and current
platform rules. No article or social post has been published to an external
account. The tutorial's callback example passed again on 2026-10-14. HN requires
human-written posts; DEV's published AI-content policy restricts business promotion.
The selected publishing account is still pending.

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
