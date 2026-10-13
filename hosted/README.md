# Openhook hosted service

Optional, separately installed login and billing application. This package is
not part of the `openhook-mcp` wheel or its runtime dependencies.

From the repository root:

```sh
uv sync --package openhook-hosted
uv run --package openhook-hosted openhook-hosted --host 0.0.0.0 --port 8788
```

Set `OPENHOOK_HOSTED=true` and configure the operator credentials described in
[hosted operations](../docs/HOSTED_OPERATIONS.md). Disabled hosted mode does not
read login or payment credentials. Enabled mode reads only the selected payment
provider's configuration. Existing payment webhook and portal handling remains
available when new sales are disabled.

Basic inboxes, MCP connections, webhook signature verification, and local
forwarding do not need this package or its operator credentials.

The hosted source remains public and MIT-licensed. Repository-wide scanners may
report its credentials; package scanners should assess the core and hosted
artifacts separately. This split does not conceal legitimate provider access.
