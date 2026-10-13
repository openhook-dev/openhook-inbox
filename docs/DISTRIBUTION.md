# Openhook distribution tracker

Last checked: 2026-10-13. Submission does not mean curator acceptance or new users.

## Published installation

The [agent skill](../skills/openhook/README.md) is public on main through
[PR #10](https://github.com/openhook-dev/openhook-inbox/pull/10).

```sh
npx skills add openhook-dev/openhook-inbox --skill openhook
```

Verified public discovery with `npx skills add openhook-dev/openhook-inbox --list`.
The project passed 97 Python tests and the generated-docs check. Both CI runs
passed before merge. The hosted first-callback example successfully sent and read
a matching payload, then cleaned up its disposable inbox on 2026-10-13.

## Submissions

| Destination | Status and evidence | Next step |
| --- | --- | --- |
| heilcheng/awesome-agent-skills | [PR #586](https://github.com/heilcheng/awesome-agent-skills/pull/586) open under Community Skills / Development and Testing; required website build passed. | Respond to maintainer feedback; verify after merge. |
| junminhong/awesome-agent-skills | [PR #73](https://github.com/junminhong/awesome-agent-skills/pull/73) open; matching English/Chinese entries; GitHub-verified commit. | Respond to maintainer feedback; verify the listing after merge. |
| realadeel/awesome-webhooks | [PR #91](https://github.com/realadeel/awesome-webhooks/pull/91) open under Development Tools. | Respond to maintainer feedback; verify after merge. |
| punkpeye/awesome-mcp-servers | [PR #16343](https://github.com/punkpeye/awesome-mcp-servers/pull/16343) drafted. Its submission bot additionally requires Glama validation and a real badge. | Complete free Glama setup and server validation, add its actual badge, then mark ready. |
| mcpservers.org | Free MCP submission accepted by the [submission form](https://mcpservers.org/submit); success screen named Openhook. Review estimate: within two weeks. | Check hello@openhook.dev for review outcome; do not resubmit while pending. |
| ClawHub openhook-cli | Existing listing is still 1.0.2. Corrected 2.0.0 package prepared, but publishing was rejected pending MIT-0 terms acceptance. No new version was published. | Obtain explicit approval for MIT-0 skill publication and the new read-only organization scope requested by browser login; complete setup and retry once. |

Glama authentication and any new account terms require approval before completing
that setup. No Glama listing, passing grade, or badge is claimed yet.

## Deferred destinations

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
