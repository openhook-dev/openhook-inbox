# Contributing

Openhook is an MIT-licensed channel between people and their agents. Keep it small:
DRY, KISS, and clarity first. Use the shared channel use cases for HTTP and MCP.
Preserve key isolation, atomic invitation redemption, idempotent messages and
migration compatibility. Do not grant local tool permissions from peer content.

Run the checks in [docs/testing.md](docs/testing.md). Regenerate `docs/TOOLS.md`
and the installable skill with `uv run python scripts/generate_docs.py` after
changes. Run `bun run build` for asset versions. Use fake local data; never test
with real customer keys. Report sensitive issues using [SECURITY.md](SECURITY.md).
