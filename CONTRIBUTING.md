# Contributing to Openhook

Openhook is an MIT-licensed HTTP, email, and DNS inbox for developers and agents.
Hosted convenience funds the project; self-hosting and the useful core remain open.

Start with a reproducible integration problem. Open an issue with the expected
behavior, actual behavior, and a minimal example using fake payloads and credentials.
Never include private inbox tokens, signing secrets, customer data, or provider keys.
For suspected vulnerabilities, follow [SECURITY.md](SECURITY.md).

Keep changes small. Prefer the existing Python service, SQLite transactions, and
plain JavaScript. Follow DRY and KISS; clarity comes before abstraction. Changes to
capture must preserve raw bytes, private-token isolation, idempotency, and atomic
activity history. Do not introduce a hosted dependency into self-hosted core flows.

```sh
uv sync --extra dev
uv run pytest -q
uv run python scripts/generate_docs.py --check
bun run build
node --check web/assets/app.js
node --check web/assets/home.js
node --check web/assets/account.js
```

SMTP and DNS tests need localhost sockets. If tools change, regenerate
`docs/TOOLS.md` before running the doc check. Commit updated asset versions after
editing web files. Explain the user-visible problem, final behavior, and relevant
validation in the pull request. Test billing with mocks or a dedicated sandbox;
never charge a real customer to validate a patch.
