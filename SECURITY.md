# Security

Never post inbox management tokens, captured customer events, provider credentials,
or signing secrets in public issues.

Report vulnerabilities through [GitHub's private reporting form](https://github.com/openhook-dev/openhook-inbox/security/advisories/new).
Private reporting is enabled for this repository. Maintainers must monitor reports
and establish a response process before accepting paid customers. Do not include
vulnerability details or sensitive data in a public issue.

Reports should describe the affected version, impact, and minimal reproduction
using disposable test data. Do not access another person's inbox or account,
exfiltrate production data, or perform destructive tests.

Public inbox addresses are write-only capabilities; private `ohk_` tokens can
read, configure, rotate, and delete their inbox. Treat `oha_` hosted agent keys
as account-level secrets for owned inbox management. Keep all credentials out of
shared prompts and source control. Use optional signature verification when the
identity of a sender matters.

Self-hosted operators are responsible for TLS, database/backup permissions,
network exposure, updates, and their own retention and access policies.

## MCP and hosted credentials

The `openhook-mcp` wheel excludes the optional `openhook-hosted` package. Basic
inbox/MCP use requires no Stripe, Polar or GitHub OAuth operator credentials.
Those environment variables are read only by the explicitly installed and
started hosted service, and only for its selected billing provider.

Provider-registration tools still require the caller's authorized provider token;
webhook verification requires the inbox's signing secret. The local listener
reads `OPENCLAW_HOOKS_TOKEN` only when `--openclaw` is selected. These are real,
optional capabilities, not billing requirements for connecting an MCP client.

The hosted source remains public in `hosted/`. A repository-wide scan can still
report its operator credentials. Assess the core and hosted artifacts separately;
this separation is not a claim that every tool is credential-free or read-only.
