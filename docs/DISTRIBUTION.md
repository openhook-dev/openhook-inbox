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

On 2026-10-16, an actual skills CLI 1.7.2 installation on macOS exposed a
case-insensitive filename collision: the installer selected the website template
web/skill.md and left unresolved origin placeholders. [PR #36](https://github.com/openhook-dev/openhook-inbox/pull/36)
renamed that template while preserving public URLs. The regression test failed
before the fix and passed after it; all 105 Python tests passed, including the
SMTP/DNS test rerun with local socket access, and both CI runs passed. A fresh
public-main install selected skills/openhook/SKILL.md and matched its contents.
This proves installation and rendered instructions, not a model evaluation.

On 2026-10-16, [PR #50](https://github.com/openhook-dev/openhook-inbox/pull/50)
added human-readable titles to all 29 tools and marked every mutation with a
destructive hint so clients can request confirmation. Both CI runs and 105 local
tests passed. Production revision `55a9214` and its healthy container were
verified. Live discovery returned all titles and annotations; a disposable real
HTTP callback passed exact-body comparison and cleanup. This is protocol proof,
not the per-tool Inspector and Claude custom-connector testing required by the
separate official connector directory.

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
| marcelscruz/dev-resources | [PR #1383](https://github.com/marcelscruz/dev-resources/pull/1383) submitted on 2026-10-16 under API Building, Testing and Open Source. 1,354 stars at discovery; recent curator merges on October 15. One alphabetical resource in resources/o.ts, 133-character description, custom-domain homepage and no tracking parameters. Affiliation and Codex assistance disclosed. | Prettier, full TypeScript check and diff check passed; homepage returned HTTP 200. No duplicate resource, issue or PR found. Generated README/db untouched as required. Open with no checks, comments or reviews at initial verification. Await curator review, then verify generated catalog and devresourc.es publication separately. |
| Skillstore | **Processing complete; review PR open.** [Submission receipt](https://skillstore.io/submissions/80cee301-2911-4e3c-b5ad-d13ab78be481), ID `80cee301-2911-4e3c-b5ad-d13ab78be481`, accepted on 2026-10-16. [Processing run 38848200439](https://github.com/aiskillstore/marketplace/actions/runs/38848200439) succeeded for the canonical skills/openhook folder at revision 278a3723 and created [review PR #3793](https://github.com/aiskillstore/marketplace/pull/3793). The provider reports one skill processed, ready, with its automated risk label safe. | Publication provenance, action-pin policy and marketplace validation all passed. PR is open with no reviewer comments at verification; acceptance and public listing remain unverified. The automated risk label is not a security certification. Claude/Codex catalog and GitHub issue searches found no duplicate before submission; network/write operations, tokens, MIT license, paid-hosting option and Codex affiliation were disclosed. No account or notification authorization used. Follow the existing PR; do not resubmit. |
| AIAnytime/Awesome-MCP-Servers | [PR #229](https://github.com/AIAnytime/Awesome-MCP-Servers/pull/229) submitted on 2026-10-16 under developer-tools. 72 stars at discovery; recent curator merges on October 15. Added one JSON definition and regenerated the README. Source, hosted endpoint, official Registry identity, private inbox-token requirements, MIT self-hosting and optional paid hosting are explicit. Affiliation and Codex assistance disclosed. | Python 3.14 generation and lint passed for all 172 entries; ten existing entries warn about missing endpoints. Public source and real MCP initialize returned HTTP 200. No duplicate name/domain or prior PR found. Verified open; GitGuardian initially running. Await curator acceptance and separate publication on mcp.aianytime.net; connectivity is not model evaluation or adoption. |
| SkillForAgents | [Submission issue #18](https://github.com/A-K0DER/AiAgentCatalog/issues/18) opened on 2026-10-16 through the site's official structured GitHub intake. Runtime, conditional self-hosting configuration, private-token access, pricing and MIT license documented. Claude Code and OpenCode installation/connection evidence is explicitly distinguished from unrun model-driven evaluations. Affiliation and Codex assistance disclosed. | Existing catalog and issue search showed no Openhook duplicate. Tagline meets the template's 140-character limit. The template's submission label is absent upstream, so no replacement label was applied. Issue verified open with no comments; await curator review and website publication. Repository itself had zero stars; directory relevance, not measured audience reach, motivated this submission. |
| MCPizy | **Submission received** on 2026-10-16. [Receipt](https://mcpizy.com/submit/thanks?ref=web_mvaextrp_vy5cr3&tier=standard), reference `web_mvaextrp_vy5cr3`, explicitly says recorded in the review queue. Full published directory HTML contained no Openhook entry before submission. Submitted under Developer tools with canonical source, a hosted Claude Code connection command, local setup documentation, pricing limits and private-token requirements. Affiliation and Codex assistance disclosed. | Free standard listing. The provider states a 24-hour review/publication window; acceptance and publication remain unverified. The receipt says a transactional email is sent, but delivery was not independently checked. Await the review window; do not resubmit. |
| MyMCPTools | **Submission received** through the [free form](https://mymcptools.com/submit) on 2026-10-16. Directory search returned zero Openhook results before submission. Submitted under API & Web with Hosted / remote endpoint installation, canonical source and website links, hosted MCP endpoint and public business contact. Description explains callback inspection, private inbox tokens, MIT self-hosting and optional paid hosting; affiliation and Codex assistance disclosed. | Receipt says it is in the hand-review queue with no set date and an email if listed. No publication, email delivery or customer reach is claimed. No paid upgrade selected. Await review; do not resubmit. |
| ZoranPandovski/awesome-testing-tools | [PR #178](https://github.com/ZoranPandovski/awesome-testing-tools/pull/178) submitted on 2026-10-16 as one alphabetical entry under Automated Testing Tools. 376 stars at discovery; recent curator merges on October 7. Contribution guide and duplicate suggestions checked. Affiliation, Codex assistance and optional paid hosting disclosed. | Upstream site generator parsed 120 tools across eight categories and produced exactly one Openhook entry in the intended category; generated JSON excluded from the diff. Canonical source link returns HTTP 200 and diff check passes. Open with no checks, comments or reviews at initial verification. Existing Pages workflow watches master while default branch is main; noted in the PR without changing workflows. Await curator review, then verify README and website publication separately. |
| PostLaunchKit | **Submitted for review** on 2026-10-16 through the [free directory form](https://postlaunchkit.com/directory/submit/). Receipt reference: `19a15161-36ad-4c11-a5ea-4fd6d217cfe5`. Submitted as an authorized agent under Developer tools / Multiple platforms, using the official website and public business contact. Describes callback inspection, free MIT self-hosting, temporary hosted inbox limits and optional paid hosting. | Directory search found no existing Openhook entry before submission. The receipt explicitly says pending, not public, with no guaranteed review time. No paid placement, backlink commitment or notification opt-in. Await human review; do not resubmit. |
| Glama remote connector | **Published** [Openhook connector](https://glama.ai/mcp/connectors/io.github.openhook-dev/openhook-inbox), verified directly on 2026-10-16. Correct repository and public endpoint, 29 tools, and resolving SVG badge. The page's latest health check is dated 2026-10-15 09:36; its tool-definition grade is C (2.9/5), scored at 10:06 that day. | This unclaimed public connector is distinct from the source-server listing/ownership gate for punkpeye/awesome-mcp-servers. No owner sign-in, manual submission or independent security certification is claimed. It resolves the connector/badge prerequisite for the separate remote collection; star permission remains pending. |
| Socketlist | **Published** [Openhook detail page](https://socketlist.com/server/io-github-openhook-dev-openhook-inbox/), verified directly on 2026-10-16 and linked from its new-servers page. Shows the correct hosted Streamable HTTP endpoint, MIT license, source identity and description. | Discovered through public search; no new submission was needed. Its displayed score and metadata are directory signals, not a security audit or independent usage. |
| HagglyAI | **Published** in the [messaging comparison](https://hagglyai.com/compare/messaging), verified in live HTML on 2026-10-16 with Openhook's endpoint and callback-inbox description. The page reports four unpaid health checks. | Health checks and comparison inclusion do not establish paid usage or customers. No submission or purchase was made. |
| jqueryscript/awesome-claude-code | [PR #788](https://github.com/jqueryscript/awesome-claude-code/pull/788) submitted on 2026-10-16 as one entry under Claude Plugins. 531 stars at discovery. Uses the existing bold-name format and the current one-star project count. Public plugin manifests and canonical skill URL were verified. Affiliation and Codex assistance disclosed. | Existing Claude Code 2.1.288 installation/connection proof is linked and distinguished from the unrun model-driven workflow test. One-line diff check passed; await curator review and default-branch publication. |
| 0xNyk/awesome-agent-cortex | [PR #122](https://github.com/0xNyk/awesome-agent-cortex/pull/122) submitted on 2026-10-16 as one alphabetical entry under Agent Protocols and MCP Ecosystem. 224 stars at discovery. Required rubric included as a proposed self-assessment: 3.6/5 average, with production maturity explicitly scored 2/5 because internal checks do not establish broad independent use. Affiliation and AI assistance disclosed. | Alphabetical validator passed across 27 blocks; internal-link checker passed across 56 Markdown files. Canonical GitHub URL returns HTTP 200 without redirect. Open with no check results or comments at initial verification; await curator review. |
| michielhdoteth/awesome-ai-agent-tools | **Merged and present in the public JSON catalog**: [PR #117](https://github.com/michielhdoteth/awesome-ai-agent-tools/pull/117) merged on 2026-10-16 at 03:01 UTC as 671cecf6, verified directly on main under Developer Tools. 42 stars at discovery; the catalog provides connection/install commands. One JSON entry, current one-star project count, community provenance and verified=false. Affiliation and AI assistance disclosed. | All eight catalogs validated with zero errors or warnings. MCP and category totals updated; generated README untouched. The command connects Claude Code to hosted MCP rather than installing a local server, with private-token and optional hosted-plan limits explained in the PR. Upstream validator and triage passed. Public main contains the exact entry; generated README does not yet contain Openhook and no new Generate README run was observed. Reported the likely GITHUB_TOKEN trigger gap in a [technical publication note](https://github.com/michielhdoteth/awesome-ai-agent-tools/pull/117#issuecomment-6207172081); latest generator run was October 9. A maintainer can dispatch the existing generator. Acceptance is not independent adoption. |
| JSONbored/awesome-claude (HeyClaude) | [PR #5845](https://github.com/JSONbored/awesome-claude/pull/5845) submitted on 2026-10-16 as one source-backed MCP entry. 300 stars at discovery; also publishes a searchable website and registry. The entry documents the free MIT self-hosted server, local Claude Code setup, callback verification, token/data boundaries and optional paid hosting. Affiliation and Codex assistance disclosed. | Strict content validation passed for 1,389 files, with 24 existing warnings unrelated to Openhook; five source/documentation links return HTTP 200. No generated files or package artifacts included. Await the private maintainer gate and verify website publication separately; protocol tests are not a model-driven evaluation. |
| Ezeafk/awesome-agent-skills | [PR #65](https://github.com/Ezeafk/awesome-agent-skills/pull/65) submitted on 2026-10-16 under MCP and Tool Integration. 104 stars at discovery. One canonical-repository entry, six-column format, High risk for deletion/provider changes, private-token caveat and proposed 9/10 evaluation with evidence. Affiliation and AI assistance disclosed. | New link returns HTTP 200 and diff checks pass. Open with no checks at initial verification; full upstream link scan was not run locally. Await curator review. |
| Anthropic official plugin directory | Prepared a first-party Claude plugin and marketplace from the canonical skills/openhook folder on 2026-10-16. The official 39,194-star repository routes submissions to the [developer portal](https://claude.ai/directory/manage), which currently requires sign-in to a paid Claude account. No official listing or submission receipt exists. | Local strict plugin and marketplace validation, isolated installation, skill discovery and hosted MCP connection passed. Standard Skills CLI installation still selects the canonical skill. Complete portal login and validation before submission. The separate MCP connector route requires every-tool Inspector and Claude connector tests; current protocol discovery is not sufficient to check that requirement. |
| ZeroPointRepo/awesome-hermes-skills | [PR #131](https://github.com/ZeroPointRepo/awesome-hermes-skills/pull/131) submitted on 2026-10-16 under Community Skills / Dev & Skill Authoring, alphabetically with the beta tag. 625 stars at discovery. Linked the canonical skill directory; followed all five template items and the upstream format regex. Maintainer affiliation and AI assistance disclosed. | Current Hermes commit acc3cada installed the unchanged public skill with skills-guard-v10 SAFE / ALLOWED and no force; installed bytes match the source. Isolated MCP setup and saved-config test discovered 29 tools. Older local Hermes incorrectly blocked documentation links, so current upstream was tested separately without updating the user installation. Await curator review; scanner verdict and connection checks are not security endorsement or model evaluation. |
| ccplugins/awesome-claude-code-plugins | [PR #730](https://github.com/ccplugins/awesome-claude-code-plugins/pull/730) submitted on 2026-10-16 as one external entry under MCP Servers. 973 stars at discovery. The collection welcomes plugins and MCP servers; a comparable one-line MCP entry was merged in August. Public source, hosted endpoint and hosted/self-hosted scope included. Maintainer affiliation and AI assistance disclosed. | Duplicate search and one-line whitespace check passed. Claude Code 2.1.288 connection evidence is distinguished from model-driven evaluation. Open with no checks, comments or reviews at initial verification. Await curator review and verify default-branch publication after acceptance. |
| composio-community/awesome-claude-plugins | [PR #570](https://github.com/composio-community/awesome-claude-plugins/pull/570) submitted on 2026-10-16 under Code Quality & Testing. 1,945 stars at discovery. Includes a plugin manifest, hosted HTTP MCP configuration, unchanged canonical skill with pinned provenance, original MIT license, setup README and both marketplace entries. Maintainer affiliation and AI assistance disclosed. | Claude Code 2.1.288 passed strict plugin validation, isolated marketplace installation, skill/server inventory and live MCP connection health. Installed skill bytes match the source. Existing catalog entries remain unchanged; full marketplace validation has nine pre-existing missing-version warnings on other plugins. Await curator review; no model-driven workflow or marketplace publication claimed. |
| ai-for-developers/awesome-ai-coding-tools | [PR #982](https://github.com/ai-for-developers/awesome-ai-coding-tools/pull/982) submitted on 2026-10-16 as one entry at the end of MCP Servers and Directories. 2,167 stars at discovery. Followed contribution rules and the PR checklist; checked duplicates, public MIT source and the live hosted free tier. Maintainer affiliation and AI assistance disclosed. | One-line diff passed whitespace checks. Open with no checks, comments or reviews at initial verification. Await curator acceptance. Openhook is an MCP tool used by coding agents, not a model; no model evaluation or adoption claimed. |
| MCP Repository | [Submission form](https://mcprepository.com/submit) confirmed the public Openhook repository was queued for validation and processing on 2026-10-16. Directory search before submission returned no results. | Expected URL is https://mcprepository.com/openhook-dev/openhook-inbox; it still returned HTTP 404 at the post-submission check. Await indexing, then verify the actual entry. No account, payment or contact address required. |
| ProMCP | [Submission form](https://www.promcpservers.com/submit) confirmed “Submission received” on 2026-10-16 and said it was on its way to the reviewer. Search returned no existing Openhook entry. Included Development category, public source, tested Gemini extension install command, hosted endpoint, tool schemas, callback example and private-inbox token requirements. Maintainer affiliation and AI assistance disclosed. | Await the directory's human installation check and publication. The receipt does not independently prove email delivery, a completed client test by the curator or a live listing. Free submission; no account creation or paid placement. |
| Chat2AnyLLM skills catalog | **Published** in the [public skills catalog](https://github.com/Chat2AnyLLM/awesome-claude-skills#source-catalog), verified from the raw default-branch README on 2026-10-16 after its 01:54 UTC refresh. Openhook has one discoverable skill, branch main, path skills and status ok. [Source-config PR #244](https://github.com/Chat2AnyLLM/awesome-repo-configs/pull/244) merged after automatic review passed. The downstream collection had 152 stars at discovery. Maintainer affiliation and AI assistance disclosed. | All three required local checks passed, including 17 helper tests; strict JSON parsing and the actual skill-layout helper passed without warnings. Both source acceptance and downstream README publication are confirmed. The catalog's ok status means its metadata scan found the skill; it is not model evaluation, security certification or adoption. |
| SkillsMP | Added and verified the claude-skills GitHub topic on 2026-10-16 while preserving all existing Openhook topics. This follows the directory's [official discovery instructions](https://skillsmp.com/docs/faq): public SKILL.md with name/description frontmatter plus a discovery topic. | Await its stated daily sync, then verify an actual public listing. Search did not establish an existing Openhook page. No manual submission receipt, account, payment or endorsement claimed. |
| JayLZhou/Awesome-Agent-Skills | [PR #59](https://github.com/JayLZhou/Awesome-Agent-Skills/pull/59) submitted on 2026-10-16 as one Ecosystem Platforms and Resources row linking to the canonical callback-testing skill. 153 stars at discovery; a comparable resource was merged on 2026-10-13. Included the requested title, project type/year and category, plus maintainer affiliation and AI-assistance disclosure. | Public skill link, duplicate search and one-row diff verified; existing line endings preserved. Open with no CI checks at initial verification. Await curator acceptance; protocol and installation checks are not model evaluations or adoption. |
| MCP Market | [Free submission form](https://mcpmarket.com/submit) confirmed “Submitted! You're in the free queue” on 2026-10-16 for the public Openhook repository. Selected MCP Server, GitHub repo and the $0 Free Queue. | The receipt estimates 4–6 weeks and says notification will follow when live. Public listing and email delivery are not verified. No paid placement or badge purchased. |
| docker/mcp-registry | [PR #5746](https://github.com/docker/mcp-registry/pull/5746) submitted on 2026-10-16 through the official remote-server route. Includes server.yaml, empty tools.json and readme.md with the hosted endpoint, MIT source, private-inbox token boundaries and documentation. 572 stars at discovery; this is a Docker Toolkit distribution route, not just a link collection. Maintainer affiliation and AI assistance disclosed. | Official validator, remote build path, catalog generation and go test ./... passed. Docker's own RemoteTools client discovered 29 live tools when the empty tools file was temporarily set aside and then restored. Docker Desktop import/full Toolkit workflow was not tested because the MCP CLI plugin is absent. Upstream CI and Security Review Trigger runs require maintainer approval. Await Docker-team review. The PR flags the upstream generator's hardcoded Apache license/docker owner defaults for remote entries; Openhook is MIT and maintained by openhook-dev. No catalog publication claimed. |
| MCPfinder.org | [Free submission form](https://www.mcpfinder.org/submit) confirmed “Submitted successfully” on 2026-10-16 and redirected to /submit?submitted=1. Used the canonical README opening as the tagline under its permitted canonical-source policy, the public repository and Development category. Affiliation and AI assistance disclosed. | The page reports a confirmation email was sent; delivery and public listing are not independently verified. Await review. No paid placement or account creation. This is mcpfinder.org, separate from the mcpfinder.dev discovery tool. |
| spencerpauly/awesome-cursor-skills | [PR #111](https://github.com/spencerpauly/awesome-cursor-skills/pull/111) submitted on 2026-10-16 as one entry at the bottom of Testing. 853 stars at discovery. Links to the canonical skill; maintainer affiliation and AI assistance disclosed. | After fixing the template discovery collision in PR #36, skills CLI 1.7.2 installed public main for Cursor in an isolated project. Its lockfile selects skills/openhook/SKILL.md; installed content matches the rendered source byte for byte. Telemetry disabled. No Cursor model evaluation claimed. Await curator acceptance. |
| atinfo/awesome-test-automation | [PR #613](https://github.com/atinfo/awesome-test-automation/pull/613) submitted on 2026-10-16 as one API-testing entry in general-purpose-test-automation-tools.md. 7,176 stars at discovery. Contribution rules, existing entries and previous suggestions checked; maintainer affiliation and AI assistance disclosed. | Focused diff and public source/example links verified. Synthetic callback receipt and cleanup previously checked through MCP; application side effects and adoption are separate. Await curator acceptance. |
| awesome-opencode/awesome-opencode | [PR #875](https://github.com/awesome-opencode/awesome-opencode/pull/875) submitted on 2026-10-16 as one Project YAML entry. 10,606 stars at discovery. The tested OpenCode setup recipe is public on main through [PR #34](https://github.com/openhook-dev/openhook-inbox/pull/34). Maintainer affiliation and AI assistance disclosed. | All 230 collection YAML entries passed local validation. OpenCode 1.19.1 reported the hosted MCP server connected using an isolated temporary profile; no model-driven workflow or adoption claimed. Generated README left to upstream automation. Upstream YAML CI is waiting for curator approval ([action-required run](https://github.com/awesome-opencode/awesome-opencode/actions/runs/38834020777)); local validation does not clear that gate. Await curator acceptance. |
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
| agentskill.sh | Repository import attempted on 2026-10-16 after search found no Openhook entry. The form repeatedly returned “Too many submissions. Please try again in an hour.” The latest retry, after the requested interval at about 02:20 UTC, returned the same response. No success receipt or listing verified. | Pause retries for this round and recheck on a later day. No alternate identity, direct-URL workaround or account creation used to bypass the limit. |
| Agent-Skills.md | **Published** [Openhook skill](https://agent-skills.md/skills/openhook-dev/openhook-inbox/openhook) on 2026-10-16. Submitted the public `skills/` folder through its designated intake form after a search found no Openhook entry. Receipt: repository captured with one skill. Public search and detail page verified, including source, MIT license, complete skill text, install command and download link. | Measure referrals and independent installations separately. The importer currently assigns Uncategorized; listing is not a security certification. |
| kodustech/awesome-agent-skills | [PR #152](https://github.com/kodustech/awesome-agent-skills/pull/152) submitted as one Testing & QA row. 108 stars at the 2026-10-16 check. README welcomes contributions; its separate CONTRIBUTING.md link is absent, also confirmed by GitHub community metadata. Maintainer affiliation and AI assistance disclosed. | Await curator review. No duplicate entry or prior PR found; focused diff checked. |
| toolsdk-ai/toolsdk-mcp-registry | **Merged and published configuration verified**: [PR #876](https://github.com/toolsdk-ai/toolsdk-mcp-registry/pull/876) merged on 2026-10-16 at 03:18 UTC as 8e3b6cb5. The [publication notice](https://github.com/toolsdk-ai/toolsdk-mcp-registry/pull/876#issuecomment-6207493555) followed at 03:35 UTC. Registry identity is `@toolsdk-remote/openhook`; hosted Streamable HTTP endpoint, Python runtime and private inbox tokens as tool arguments. 197 stars at discovery. | The [published JSON](https://toolsdk-ai.github.io/toolsdk-mcp-registry/packages/developer-tools/openhook.json) returned HTTP 200 and matched the accepted main-branch JSON exactly, including https://openhook.dev/mcp. Local registry validation had zero errors and warnings; Schema and Biome CI passed. This proves acceptance and configuration publication, not end-user adoption. No requested promotional badge was added to Openhook's README. |
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

Glama source-server authentication and any new account terms require approval
before completing that setup. The separate public remote connector and its
badge are verified above; no source-server submission or security certification
is claimed.

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

- [jamesmurdza/awesome-ai-devtools](https://github.com/jamesmurdza/awesome-ai-devtools/blob/main/.github/PULL_REQUEST_TEMPLATE.md)
  (3,960 stars) requires the submitted tool itself to use AI. Openhook exposes
  callback capture through MCP and APIs; that is not evidence it uses AI itself.
  No submission made on 2026-10-16 merely because coding agents can call it.

- [stn1slv/awesome-integration](https://github.com/stn1slv/awesome-integration/blob/main/CONTRIBUTING.md)
  (566 stars, active October 11) explicitly prohibits self-promotion and mass
  submission campaigns. It also requires projects at least six months old and
  generally 250 stars. No submission made on 2026-10-16; do not disguise
  affiliation or seek an exception solely for another placement.

- [haoruilee/awesome-agent-native-services](https://github.com/haoruilee/awesome-agent-native-services/blob/main/CONTRIBUTING.md)
  (370 stars, active October 15) requires agent-specific primitives and distinct
  agent identity, delegated permissions and attributable audit trails. Openhook's
  callback inboxes and bearer-token access do not establish all those guarantees.
  No proposal was submitted merely because MCP is supported. New service PRs
  also require an explicitly approved proposal issue.
- [skillmatic-ai/awesome-agent-skills](https://github.com/skillmatic-ai/awesome-agent-skills)
  (684 stars) primarily catalogs learning resources, skill collections and tools
  for authoring skills. No suitable existing section for Openhook's individual
  callback skill was identified. The latest observed merged PR was February 16;
  newer submissions remain open. No entry was forced into Popular Collections
  or Developer Tools, which concern skill authoring and loading.

- [Claude Skills GitHub](https://claudeskillsgithub.com/blog/how-to-submit-repository)
  explicitly rejects submissions made primarily for backlinks or commercial
  promotion. This campaign's stated purpose is promotion, so no submission
  was made on 2026-10-16. Do not disguise the campaign's purpose to qualify.
- [Claude Skill Guide](https://www.claudeskillguide.com/submit.html) displays a
  free submission form, but its public HTML posts to the same page (`action="#"`)
  and the only application script inspected has no submission handler. Its
  referenced GitHub repository returns 404. Delivery remains unverified; this
  is not proof that a server-side handler cannot exist. No form was submitted,
  and no receipt or listing is claimed. Revisit if a working intake can be
  established.
- [GuildSkills](https://guildskills.com/) exposes a public bulk catalog. On
  2026-10-16 it contained no Openhook match. Its linked GitHub repository,
  `kinkyb/guildskills`, returned 404, and no direct submission form was found
  on the inspected homepage. No account, email, submission or listing created.
  Search UI is membership-gated; public catalog browsing does not require it.

- [ClaudSkills](https://claudskills.com/) asks submissions to include
  `allowed-tools` in skill frontmatter. Openhook's canonical skill currently has
  name, description and license fields, without that client-specific tool
  declaration. No submission made on 2026-10-16; do not add broad tool
  permissions merely to qualify for a directory. Search UI requires membership;
  its separate read-only public API is documented.
- [MCPSafe](https://mcpsafe.dev/) documents a public search API, but requests to
  `/api/v1/servers?q=openhook` returned HTTP 500 twice on 2026-10-16. Duplicate
  status and the claimed scan workflow could not be established. No submission
  or security grade claimed; revisit after the directory API is functional.

- [Few Servers](https://www.fewservers.com/mcp/submit/): public API search returned
  zero Openhook results and direct registry-name lookup returned 404 on
  2026-10-16. Filled and posted a missing-index correction, but the response
  explicitly said **not sent yet** and **nothing stored**: intake currently
  requires email to hello@fewservers.com. A [prepared email](gtm/fewservers-email.txt)
  is awaiting user authorization and sender selection. No submission receipt,
  email send or published listing is claimed. Two fresh Official Registry reads
  timed out; the earlier verified record is not treated as a fresh successful
  check or as evidence of removal.

- [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first/blob/main/CONTRIBUTING.md)
  (1,848 stars, recent curator merges on October 13) requires a significant
  milestone such as 1,000 GitHub stars, 1,000 followers, a Product Hunt award or
  SOC-2 compliance. None is established for Openhook; no submission made on
  2026-10-16. Revisit when an eligible milestone can be substantiated.

- [punkpeye/awesome-mcp-devtools](https://github.com/punkpeye/awesome-mcp-devtools)
  (488 stars at the 2026-10-16 check) focuses on tools for building, testing and
  operating MCP servers. Openhook provides callback inspection through MCP;
  it is not an MCP implementation-testing tool. No entry submitted solely to
  gain another placement; its server collections remain the closer fit.

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

- [kyrolabs/awesome-agents](https://github.com/kyrolabs/awesome-agents/blob/main/CONTRIBUTING.md)
  (2,928 stars at the 2026-10-16 check) explicitly excludes new projects without
  demonstrated traction. Openhook's internal tests and directory acceptances do
  not establish that traction; no submission was made.

- [philipbankier/awesome-agent-skills](https://github.com/philipbankier/awesome-agent-skills)
  (20 stars; also publishes awesomeagentskills.dev) requires at least ten stars
  or an official source. Openhook had one star at the 2026-10-16 check; no
  exception was inferred from being the project maintainer, and no PR was sent.
  Its Official MCP Registry sync may discover the existing published record;
  an Openhook website entry has not been verified.

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
- [Cursor Directory](https://cursor.directory/plugins/new): its current plugin
  submission route redirected to sign-in on 2026-10-16. No account or submission
  created. This is separate from the awesome-cursor-skills PR above.
- [Smithery](https://smithery.ai/new): the official URL-publishing route redirected
  to sign-in on 2026-10-16. Its [publishing guide](https://smithery.ai/docs/build/publish)
  accepts hosted Streamable HTTP servers and scans their metadata. No account,
  scan, server listing or skill listing was created. Resume after authentication.
- [MCPVault](https://mcpvault.io/submit): live search returned no Openhook entries
  on 2026-10-16. The submission page requires GitHub sign-in to associate and
  claim the listing. No account, submission, verification or purchase performed.
- [SkillMD.com](https://skillmd.com/publish) requires sign-in to publish. The
  separate [SkillMD.ai](https://skillmd.ai/submit/) form explicitly creates an
  account from the submitted email. Neither account nor submission was created
  during the 2026-10-16 check.
- [Skills AI by Strongly.AI](https://skills.strongly.ai/submit) shows Sign In
  Required. Its no-login claim applies to the evaluator, not publication. No
  account or submission was created during the 2026-10-16 check.
- [AIBase MCP](https://mcp.aibase.com/submit): the form redirected to sign-in
  when interaction began on 2026-10-16. No submission receipt, account creation
  or public listing verified; resume after authentication.
- [PulseMCP](https://www.pulsemcp.com/): homepage explicitly says new server
  submissions and listing changes are paused. Revisit when submissions reopen.
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills):
  requires established community usage. Revisit when independent usage can be
  demonstrated; do not represent internal testing as adoption.
- [punkpeye/awesome-remote-mcp-servers](https://github.com/punkpeye/awesome-remote-mcp-servers):
  (1,300 stars) now has a prepared Openhook entry: the public connector and SVG
  badge resolve, the endpoint answers unauthenticated MCP initialize with HTTP
  200, and format/order checks pass. Its current rules also require the submitting
  account to star the collection. The user account has not starred it; permission
  was requested. No star or PR has been submitted. This is separate from the
  draft submission to punkpeye/awesome-mcp-servers.
- appcypher/awesome-mcp-servers is archived; no submission.
- wong2/awesome-mcp-servers directs submissions to mcpservers.org and does not
  accept listing PRs. The website submission above follows that route.

- [cline/mcp-marketplace](https://github.com/cline/mcp-marketplace) is a separate, older intake route requiring an actual Cline setup test. No such test or submission was claimed. The newer [cline/marketplace contribution guide](https://github.com/cline/marketplace/blob/main/CONTRIBUTING.md) permits a metadata PR, submitted above with protocol-test evidence explicitly distinguished from Cline client testing.
- [LobeHub MCP Marketplace](https://lobehub.com/mcp) was inspected on 2026-10-16. Its current owner publication route uses the market CLI and requires browser login plus GitHub ownership connection; the older lobe-chat-plugins repository targets function-calling plugins, not this MCP intake. No LobeHub login, account creation or publication was performed. See the [official publication instructions](https://lobehub.com/publish-mcp/skill.md).

- [QASkills.sh](https://qaskills.sh/how-to-publish) is a relevant testing-skill directory. Its official publishing guide and repository contribution section direct new skills through authenticated dashboard/CLI publication; PRs are invited for improving existing skills. No account was created and no new-skill PR was sent through the wrong route.

- [Prat011/awesome-llm-skills](https://github.com/Prat011/awesome-llm-skills/blob/master/CONTRIBUTING.md)
  (1,801 stars at the 2026-10-16 check) requires verifying the skill across Claude
  Code, Codex and Gemini CLI. Current install/protocol evidence does not establish
  those model-driven workflows; no PR submitted.
- [Vibehackers skill import](https://vibehackers.io/claude-code/submit) accepted the
  public repository URL but stopped with “Sign in first — your listings are tied
  to your account.” No listing receipt, account creation or paid feature purchase.
- [SkillRouter](https://skillrouter.org/us/submit) requires signing in with its CLI
  before submitting, with optional repository ownership verification afterward.
  No login or submission performed.
- ichangyou/awesome-codex (5 stars) and ranbot-ai/awesome-skills (7 stars) were
  deprioritized for reach on 2026-10-16.

- [ToolHive catalog](https://github.com/stacklok/toolhive-catalog/blob/main/docs/server-criteria.md)
  requires pinned dependencies and GitHub Actions pinned to SHAs. Openhook's
  current test/release workflows still use action tags. Its shared criteria also
  weigh sustained organic adoption and warn against bulk listing campaigns.
  No submission made on 2026-10-16; revisit after supply-chain hardening and
  stronger independent usage evidence.

- [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills/blob/main/CONTRIBUTING.md)
  (53,153 stars at the 2026-10-16 check) requires an existing ClawHub listing,
  passing tests, clean security status and real community usage. The pending
  ClawHub correction and absent independent usage evidence remain gates; no PR
  submitted.

- [skills.sh](https://skills.sh/openhook-dev/openhook-inbox/openhook): the detail
  URL returned HTTP 200 with an explicit not-available/404 page on 2026-10-16,
  so a public listing is not established. Its [FAQ](https://skills.sh/docs/faq)
  describes install telemetry as the listing mechanism. Local QA installs used
  telemetry opt-out; do not manufacture install counts to obtain ranking.

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
No reminder comments were posted. That earlier PR search showed three
external merges; the refreshed audit below includes the later Chat2AnyLLM merge.

## Review audit — 2026-10-16

The latest GitHub search audit found 37 open external Openhook PRs and six
merged external PRs. The two other closed search matches predate this campaign;
they are not counted as newly accepted listings. This updates the earlier
33-open/four-merged snapshot after the subsequent submissions and catalog merges.
Direct GraphQL inspection at that earlier snapshot found no new maintainer
comments or formal review requests to address across those 33 open PRs. The
later technical publication note on the accepted JSON catalog is linked above;
it is not a reminder or a duplicate submission.

The failed Vercel contexts on heilcheng #586 and sickn33 #1943 explicitly require
a member of those owners' teams to authorize preview deployment. They are not
reported test regressions. Sickn33's Socket and Snyk contexts passed. Other
submissions remain in curator review or require owner approval to start checks.

The older [jezweb/claude-skills #50](https://github.com/jezweb/claude-skills/pull/50)
was closed after unresolved requested changes, with an invitation to resubmit.
Its [maintainer review](https://github.com/jezweb/claude-skills/pull/50#pullrequestreview-4025103371)
asked for safer installation, service stability/self-hosting, complete inline
instructions and an actual Claude Code end-to-end session test. The current
native skill no longer uses the old curl-pipe-shell installer or claims to
restart stopped sessions. However, installation and MCP discovery still do not
satisfy the requested model-driven workflow test. No replacement PR was opened;
revisit after that evidence is available. The repository had 1,065 stars and an
October 2026 update at this check.

The large punkpeye collection submission remains a draft pending Glama. The
[validator preparation](gtm/glama-validation.md) now records a successful local
non-root container build and network-disabled stdio discovery of 29 tools and
3 resources. Glama Add Server still requires account sign-in, requested from the
user; no source-server submission is claimed. The separate remote connector,
its dated tool-definition grade and its badge are verified in the table above.

Claude Code 2.1.288 CLI authentication was checked on 2026-10-16 and reported
signed out. A user sign-in request is pending so the actual Claude workflow test
can be run for the collections requiring it. No model call or successful
model-driven evaluation is claimed.
