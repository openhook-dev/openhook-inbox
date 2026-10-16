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
| awesome-opencode/awesome-opencode | [PR #875](https://github.com/awesome-opencode/awesome-opencode/pull/875) submitted on 2026-10-16 as one Project YAML entry. 10,606 stars at discovery. The tested OpenCode setup recipe is public on main through [PR #34](https://github.com/openhook-dev/openhook-inbox/pull/34). Maintainer affiliation and AI assistance disclosed. | All 230 collection YAML entries passed local validation. OpenCode 1.19.1 reported the hosted MCP server connected using an isolated temporary profile; no model-driven workflow or adoption claimed. Generated README left to upstream automation. Await curator acceptance. |
| composio-community/awesome-codex-skills | [PR #346](https://github.com/composio-community/awesome-codex-skills/pull/346) submitted on 2026-10-16 with the Openhook callback-testing skill, pinned source attribution, preserved MIT license and four review prompts. 16,914 stars at discovery. Maintainer affiliation and AI assistance disclosed. | The collection's skill validator passes; the skill is 85 lines. A synthetic callback was verified through the MCP SDK with full-body comparison, timeout cursor preservation and test-inbox cleanup. This is not an automated Codex model evaluation. Await curator acceptance. |
| sickn33/agentic-awesome-skills | [PR #1943](https://github.com/sickn33/agentic-awesome-skills/pull/1943) submitted on 2026-10-16, adapting the Openhook skill with source attribution, preserved MIT notice, four evaluation prompts and explicit scope/cleanup limits. The repository was renamed from antigravity-awesome-skills and has 47,688 stars at discovery. No duplicate Openhook entry or PR found. Maintainer affiliation and AI assistance disclosed. | Validation chain, references, documentation security, 0/0 warning budget, source-credit check and all 149 local test groups passed. A real synthetic callback matched original bytes through MCP; timeout preserved its cursor and cleanup deleted the test inbox. Network integration suites and automated model evaluations were not run. Await upstream semantic review and curator acceptance. The Vercel preview requires approval from the collection owner’s team, per its PR bot comment; local checks do not resolve that gate. Generated catalogs and plugin mirrors are excluded from the source PR. |
| Piebald-AI/awesome-gemini-cli-extensions | [PR #76](https://github.com/Piebald-AI/awesome-gemini-cli-extensions/pull/76) submitted on 2026-10-16 as one Development entry, using the required bold-name format. Contribution rules and duplicate check verified. Gemini CLI 0.64.0 installed Openhook from public main, recognized the skill and connected to the hosted endpoint. Maintainer affiliation and AI assistance disclosed. | Await curator review; no model-driven workflow test, gallery publication or adoption claimed. This focused extension collection has 68 stars at discovery. |
| Piebald-AI/awesome-gemini-cli | Entry prepared locally under MCP Servers on 2026-10-16; no existing Openhook PR found. The repository has 514 stars. Its AGENTS.md explicitly requires asking the user whether to star the repository before opening a PR. | Await the user's answer to the star question. No star or PR submitted. If declined, leave the template's star checkbox unchecked; never invent that action. |
| Gemini CLI extension gallery | Added the root gemini-extension.json manifest and documented installation from main in [PR #31](https://github.com/openhook-dev/openhook-inbox/pull/31). The gemini-cli-extension repository topic was added and verified on 2026-10-16. Gemini CLI 0.64.0 installed the public PR branch in isolated settings, recognized the existing Openhook skill, and reported the hosted endpoint Connected. | Await the gallery's daily discovery and validation after merge, then verify the actual public listing. Public Git installation and client connection are proven; gallery publication and independent adoption are not. See the [official discovery requirements](https://github.com/google-gemini/gemini-cli/blob/main/docs/extensions/releasing.md#list-your-extension-in-the-gallery). |
| Kilo-Org/kilo-marketplace | [PR #407](https://github.com/Kilo-Org/kilo-marketplace/pull/407) submitted on 2026-10-16 with one Development MCP definition and its generated catalog entry. Uses the hosted Streamable HTTP endpoint; private inbox-token and persistent-account requirements are explicit. 194 stars at discovery; client distribution is the reason for submission. Maintainer affiliation and AI assistance disclosed. | Local generation passed for 129 MCPs; all 119 tooling tests and both type checks passed. Runtime JSON and live SDK discovery of 29 tools verified. This is not a Kilo client test. Await curator review, then verify marketplace publication separately. |
| tolkonepiu/best-of-mcp-servers | [PR #517](https://github.com/tolkonepiu/best-of-mcp-servers/pull/517) submitted on 2026-10-16 with one Developer Tools entry in projects.yaml. Current contribution rules, PR checklist and duplicate checks followed. 154 stars at discovery; minimum stars and project rank are zero. Maintainer affiliation and AI assistance disclosed. | Local YAML lint, focused diff and upstream yamllint CI passed. Await curator review and the separate generated-list update; no ranking, acceptance or adoption claimed. |
| MCP.tc | **Published** [Openhook listing](https://mcp.tc/i/openhook), verified 2026-10-16. Directory search initially showed zero matches; submitted the public endpoint through its no-account form with source, guide, token requirements, maintainer affiliation and AI-assistance disclosure. Receipt progressed from checking to listed. | Public page verified with correct Streamable HTTP endpoint, 29 tools, source attribution, private inbox-token explanation and client setup links. Listing is not independent adoption or a security certification. No account, contact email or payment was needed. |
| TrackMCP | **Submitted for review** on 2026-10-16 after the user approved the prepared free listing and required support contact. The form confirmed: “Your tool has been submitted. We'll review it and email you a confirmation.” Canonical GitHub repository submitted; paid placement was not selected. | Await review and verify the public directory entry separately. The earlier automatic approval gate is resolved; receipt is not publication or adoption. Do not submit again while pending. |
| denji/awesome-http-benchmark | [PR #79](https://github.com/denji/awesome-http-benchmark/pull/79) submitted on 2026-10-16 as one HTTP testing/debugging toolkit entry. 3,783 stars and a September upstream merge verified. Root contains README and MIT license; GitHub community metadata showed no separate contribution guide or PR template. No duplicate entry or PR found; maintainer affiliation and AI assistance disclosed. | Focused diff passed. Await curator review and verify the default-branch entry after any merge. Openhook is described as a callback inspection tool, not a load generator. |
| TheJambo/awesome-testing | [PR #303](https://github.com/TheJambo/awesome-testing/pull/303) submitted on 2026-10-16 as one API Testing entry beside existing webhook tools. 2,391 stars; recent upstream merges verified. Read contribution rules and code of conduct, searched previous suggestions, disclosed maintainer affiliation and AI assistance, and followed CC0 terms for the README contribution. | Open and awaiting curator review. Focused diff passed; the upstream dead-link checker passed on 2026-10-16. Source remains MIT licensed. |
| yosriady/awesome-api-devtools | [PR #227](https://github.com/yosriady/awesome-api-devtools/pull/227) submitted on 2026-10-16 as one API Debugging and Mocking / Hosted entry. 4,014 stars. README welcomes contributions; GitHub community metadata showed no separate contribution guide or PR template. No existing entry or PR found; maintainer affiliation and AI assistance disclosed. | Open with no checks or reviews at initial verification. This collection has an older activity date, so review timing is uncertain. Submission is not a published listing or measured reach. |
| cline/marketplace | [PR #248](https://github.com/cline/marketplace/pull/248) submitted on 2026-10-16 to Cline's CLI marketplace catalog with one MCP entry and the existing Openhook logo. Hosted Streamable HTTP install command, per-inbox token requirements, and callback-receipt boundary are explicit. Both verified and featured flags are false; maintainer affiliation and AI assistance disclosed. | Local validation and generation passed for all 204 entries. Open with no checks or reviews at the initial verification. Await Cline review, then separately verify the published catalog. This new catalog repository has 8 stars; client distribution, not repository star count, is the reason for submission. |
| agentskills.in | **Published** [Openhook skill](https://www.agentskills.in/marketplace/@openhook-dev/openhook), verified 2026-10-16 after submitting the public repository through its designated form. Search before submission showed no matches. The receipt said zero indexed skills, but the public detail page resolves with the correct source folder, branch, complete instructions and scoped install command. | Treat the verified public page as publication evidence. The page says Not scanned; no security endorsement or independent installation is claimed. The importer also exposes a separate `web` entry from the repository's web skill file. |
| agentskill.sh | Repository import attempted on 2026-10-16 after its search returned zero Openhook matches. The form returned “Too many submissions. Please try again in an hour.” No success receipt or listing was verified. | Wait for the directory's stated one-hour cooldown before checking again. Do not bypass the limit or resubmit through another identity. |
| Agent-Skills.md | **Published** [Openhook skill](https://agent-skills.md/skills/openhook-dev/openhook-inbox/openhook) on 2026-10-16. Submitted the public `skills/` folder through its designated intake form after a search found no Openhook entry. Receipt: repository captured with one skill. Public search and detail page verified, including source, MIT license, complete skill text, install command and download link. | Measure referrals and independent installations separately. The importer currently assigns Uncategorized; listing is not a security certification. |
| kodustech/awesome-agent-skills | [PR #152](https://github.com/kodustech/awesome-agent-skills/pull/152) submitted as one Testing & QA row. 108 stars at the 2026-10-16 check. README welcomes contributions; its separate CONTRIBUTING.md link is absent, also confirmed by GitHub community metadata. Maintainer affiliation and AI assistance disclosed. | Await curator review. No duplicate entry or prior PR found; focused diff checked. |
| toolsdk-ai/toolsdk-mcp-registry | [PR #876](https://github.com/toolsdk-ai/toolsdk-mcp-registry/pull/876) submitted with one developer-tools JSON file for the hosted Streamable HTTP endpoint. Registry identity is `@toolsdk-remote/openhook`; runtime Python, no OAuth or connection-header requirements claimed, private inbox tokens described as tool arguments. Local registry validation: one file, zero errors and warnings. 197 stars at the 2026-10-16 discovery check. | Schema and Biome CI checks passed. Await curator review; the registry requires a separate manual catalog publication after merge. Neither merge nor catalog publication is claimed yet. |
| devtoolsd/awesome-devtools | [PR #442](https://github.com/devtoolsd/awesome-devtools/pull/442) submitted as one Testing & Quality entry. 686 stars at the 2026-10-16 discovery check. Maintainer affiliation and AI assistance disclosed; duplicate search and focused diff verified. | Await curator review; no checks or comments at submission verification. |
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

- [aaif-goose/goose](https://github.com/aaif-goose/goose/blob/main/AGENTS.md)
  (55,324 stars at the 2026-10-16 check) has retired new third-party directory
  additions in favor of the official MCP Registry. No listing PR submitted.
  Openhook's official Registry record was reverified as active and latest,
  version 0.1.0 with the correct hosted endpoint. This does not establish that
  Goose's registry-backed client discovery has shipped or been tested.
- [marmelab/awesome-rest](https://github.com/marmelab/awesome-rest/blob/master/.github/pull_request_template.md)
  (3,920 stars at the 2026-10-16 check) has a relevant webhook testing category,
  but its PR template excludes young tools until they prove widely useful.
  No existing Openhook PR found; no submission made. Revisit with evidence of
  independent usage rather than treating internal tests as adoption.

- [skillsdir.dev](https://skillsdir.dev/add) directs submissions to
  `brunogalvao/claude-skills-directory` through an issue template. The linked
  repository and issue-template route returned 404 on 2026-10-16; no submission.

- [public-apis/public-apis](https://github.com/public-apis/public-apis/blob/master/CONTRIBUTING.md)
  (489,117 stars at the 2026-10-16 check) explicitly excludes marketing-driven
  submissions. Inspected its API and MCP formats but made no contribution as
  part of this promotion campaign.

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

- [cline/mcp-marketplace](https://github.com/cline/mcp-marketplace) is a separate, older intake route requiring an actual Cline setup test. No such test or submission was claimed. The newer [cline/marketplace contribution guide](https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md) permits a metadata PR, submitted above with protocol-test evidence explicitly distinguished from Cline client testing.
- [LobeHub MCP Marketplace](https://lobehub.com/mcp) was inspected on 2026-10-16. Its current owner publication route uses the market CLI and requires browser login plus GitHub ownership connection; the older lobe-chat-plugins repository targets function-calling plugins, not this MCP intake. No LobeHub login, account creation or publication was performed. See the [official publication instructions](https://lobehub.com/publish-mcp/skill.md).

- [QASkills.sh](https://qaskills.sh/how-to-publish) is a relevant testing-skill directory. Its official publishing guide and repository contribution section direct new skills through authenticated dashboard/CLI publication; PRs are invited for improving existing skills. No account was created and no new-skill PR was sent through the wrong route.

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

On 2026-10-16, the recent BehiSecc #952, libukai #198 and YuzeHao #646
submissions were checked directly: no review comments or checks were present.
No reminder comments were posted. The broader PR search still showed the three
previously confirmed external merges and the other submitted PRs awaiting review.

## Review audit — 2026-10-16

Direct inspection of all 19 currently open external PRs found no formal reviews
or requested code changes and no additional merges. Awesome Testing's dead-link
check passed; Composio, ToolSDK and Kodus checks remain successful. Heilcheng's
Vercel preview still requires its owner's authorization. A positive inspection
comment on that PR is from an account with association `NONE`, not a maintainer
approval. No reminder comments were posted.

The large punkpeye collection submission remains a draft pending Glama. The
[validator preparation](gtm/glama-validation.md) now records a successful local
non-root container build and network-disabled stdio discovery of 29 tools and
3 resources. Glama Add Server still requires account sign-in, requested from the
user; no Glama submission, passing platform grade or badge is claimed.
