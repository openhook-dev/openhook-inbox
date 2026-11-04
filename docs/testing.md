# Channel release validation

Temporary attachment checks in `native_tests/test_channel_files.py` cover
membership isolation, read-only access, revocation during upload, expiry,
duplicate and concurrent retries, storage limits, encrypted migration/rotation,
tampering, binary HTTP security headers, MCP metadata and private CLI downloads.
They use disposable local storage and synthetic content, not customer files.

```sh
bun run build
uv run pytest -q
uv run python scripts/generate_docs.py --check
node --check web/assets/app.js
node --check web/assets/sessions.js
node --test native_tests/*.test.mjs
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

WebMCP unit checks cover optional native registration, membership-scoped tool
visibility, bounded secret-free schemas, cancellation, safe errors and browser
page lifecycle. For native validation, enable WebMCP in a compatible browser and
use two disposable local tabs: create, join from the invitation, exchange/read
messages, retry a send with the same ID, and verify both UI and tool results.
Check read-only membership, revocation and that results omit member keys. Registry
doubles alone do not establish native browser support or agent-client support.

Inbox tests use a disposable local server to check metadata-only hook context,
explicit read/ack, replay after a failed processing turn, revoked access and
private key files. Setup tests verify preview-only defaults, backups, preserved
unrelated hooks and repeatable installation. Listener tests distinguish permanent
request failures from rate limits and transient failures. Wheel checks also run
the packaged inbox/listener entry points.

Native background tests cover Codex tool-output delivery without user input or
permission overrides, Claude metadata-only notifications, explicit read/ack,
rearming, cancellation, runtime-parent shutdown, revocation, wrong-chat rejection
and uncertain-send retention. Unix socket tests need local IPC access.

Actual runtime validation on 2026-11-03 used Codex CLI 0.160.0 and Claude Code
2.1.316 with disposable local channels. After one initial human prompt, each
waiting model processed two separately arriving synthetic messages without a
follow-up human prompt. Codex history contained native function-call outputs;
Claude read and acknowledged through the inbox tool, with no peer text in hook
context. Claude's headless streaming test explicitly stopped its background hook
before closing stdin. These are internal QA results, not customer adoption or a
guarantee for every desktop/hosted client.

For runtime checks, record the initial prompt, peer send time, native delivery,
model processing, second-message receipt and cleanup. Keep logs private and
publish only sanitized receipts. Never publish keys, alter hook trust state or
bypass runtime review. The current contracts are
[Codex standalone tool output](https://learn.chatgpt.com/docs/app-server#turns)
and [Claude background hooks](https://code.claude.com/docs/en/hooks#run-hooks-in-the-background).

Before release, use two browser tabs to create and join a disposable local
channel, exchange messages and verify rendering of untrusted text. Check narrow
screens, keyboard focus and the reduced navigation. Confirm the installed wheel
contains only channel features and can run without payment/provider credentials.
Live rollout verification is separate from local test evidence; follow
[the release checklist](CHANNEL_ONLY_RELEASE.md).

Request-security tests exercise slow/dripping uploads, valid long-poll behavior,
ambiguous framing and JSON, error-header enforcement, and private queue cleanup
without discarding pending work. CI also audits the exact locked production
dependencies; do not suppress advisory findings without a documented resolution.
