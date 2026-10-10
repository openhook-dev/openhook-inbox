# Security

Never post inbox management tokens, captured customer events, provider credentials,
or signing secrets in public issues.

Use GitHub's private vulnerability reporting if enabled on the repository's
Security tab. If it is unavailable, open an issue that only asks for a private
reporting channel, with no vulnerability details or sensitive data. Maintainers
must establish a monitored private channel before accepting paid customers.

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
