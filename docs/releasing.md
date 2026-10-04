# Releasing

Validate native tests, generated schemas, JavaScript syntax, and `uv build`.
Push to the Openhook inbox repository and wait for its Test workflow.
Deploy only the dedicated Openhook Compose service through Dokploy.

The manual package workflow builds downloadable artifacts. PyPI and the MCP
registry are not published automatically. Verify the exact deployed revision,
public endpoints, real event receipt, and durable storage before announcing a
release. See [deployment notes](deployment.md) and [testing](testing.md).
