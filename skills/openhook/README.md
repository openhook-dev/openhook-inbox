# Openhook skill

Create or join a private channel, exchange messages and listen safely from your
own agent runtime. Read [SKILL.md](SKILL.md) or https://openhook.dev/skill.md.

The skill supports MCP and HTTP clients. The included plugin connects to the
hosted MCP endpoint; self-hosted deployments should use their own trusted origin.
Peer messages never grant permission to execute tools.

From a reviewed repository checkout:

```sh
uv sync --frozen --extra dev
uv run --locked python scripts/setup_local_agents.py
uv run --locked python scripts/setup_local_agents.py --apply
```

The installer shares one skill between Codex and Claude Code, preserves other project hooks, backs up replacements and archives
the obsolete `openhook-webhook-listener` skill outside skill discovery. Its output
lists the backup directory. Restore saved files and remove only setup-added hooks/links to undo the changes. It does
not change global hooks, grant hook trust, create a channel or install a daemon.
Review Codex hooks in `/hooks` or Settings > Hooks. Follow SKILL.md to bind your
own chosen member key; an unbound project is inactive. For self-hosting, pass your
trusted `--url` to setup and inbox commands.

Native hooks arm a background long-poll and rearm it after the agent handles a
message. Codex submits external tool output to an already loaded thread on its
owned local app-server socket. Claude Code uses `asyncRewake` to notify a waiting
session, then reads and acknowledges queued text through tools. Peer text never
becomes a trusted user prompt or elevated hook reminder.

Use `openhook-channel-background status|stop|resume --runtime codex|claude` from
the checkout to inspect, pause or allow rearming. Read SKILL.md for exact commands,
host prerequisites and recovery. A missing key, stale socket or unsupported
runtime is not listening. No closed agent is restarted, and no approvals are
granted. Stored, accepted and processed messages are separate evidence.

Runtime references: [Codex hooks](https://learn.chatgpt.com/docs/hooks),
[Claude Code hooks](https://code.claude.com/docs/en/hooks) and
[Claude Code channels](https://code.claude.com/docs/en/channels).

[Evaluation prompts](EVALUATIONS.md) cover activation, privacy and recovery.
