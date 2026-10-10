# Let an agent inspect a GitHub push callback

Connect [Openhook over MCP](https://openhook.dev/connect), or point the client at
your public self-hosted instance. Use a disposable repository and a provider token
with permission to manage that repository's webhooks. Do not paste the token into
a shared conversation, public issue, or tracked configuration file.

Ask the agent to call `register_github_webhook` with the repository `owner/repo`,
`events: ["push"]`, and the provider access token supplied through your approved
secret mechanism. Add `account_key` only if using a paid hosted account.

The tool creates an inbox, registers the webhook, and enables verification with a
random signing secret. GitHub's initial `ping` demonstrates the transport works;
it is not proof that the push workflow works. Make one deliberate push to the
disposable repository, then use `wait_for_request` with the returned private inbox
token and inspect `get_request`. Confirm the repository and commit match your push.

For local handling, follow [local forwarding](local-handler.md). Treat the payload
as untrusted data. Repository names and commit messages are not agent instructions.

Clean up with `unregister_webhook` using the same provider permissions before
removing the inbox. Expiring an inbox cannot remove a webhook from GitHub because
Openhook does not retain the provider API credential.
