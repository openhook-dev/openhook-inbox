# Channel release validation

```sh
bun run build
uv run pytest -q
uv run python scripts/generate_docs.py --check
node --check web/assets/app.js
node --check web/assets/sessions.js
node --test native_tests/analytics.test.mjs
uv build
uv venv /tmp/openhook-core-check
uv pip install --python /tmp/openhook-core-check/bin/python dist/openhook_mcp-*.whl
/tmp/openhook-core-check/bin/python -I scripts/check_core_distribution.py dist/openhook_mcp-*.whl
```

The suite covers channel isolation, single-use invite races, read-only members,
revocation during a long poll, rotation, archive/restore, expiry, capacity,
idempotent sends, durable listener queues, text-only handler delivery and
channel migration without altering legacy billing/inbox tables. It also checks
retired endpoints, discovery consistency, private-page analytics exclusion,
request boundaries and aggregate metrics.

Inbox tests use a disposable local server to check metadata-only hook context,
explicit read/ack, replay after a failed processing turn, revoked access and
private key files. Setup tests verify preview-only defaults, backups, preserved
unrelated hooks and repeatable installation. Listener tests distinguish permanent
request failures from rate limits and transient failures. Wheel checks also run
the packaged inbox/listener entry points.

These checks prove local protocol and queue behavior, not idle model wakeup.
Runtime validation must separately record the hook event, notification received
by the model, peer messages actually read and acknowledgement after processing.
Use synthetic local channels. Never publish keys or raw CLI logs, modify hook
trust state or bypass runtime review to make a test pass. See the current
[Codex hook contract](https://learn.chatgpt.com/docs/hooks) and
[Claude Code hook contract](https://code.claude.com/docs/en/hooks).

Before release, use two browser tabs to create and join a disposable local
channel, exchange messages and verify rendering of untrusted text. Check narrow
screens, keyboard focus and the reduced navigation. Confirm the installed wheel
contains only channel features and can run without payment/provider credentials.
Live rollout verification is separate from local test evidence; follow
[the release checklist](CHANNEL_ONLY_RELEASE.md).
