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
