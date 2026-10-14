# Releasing

Validate native tests, generated schemas, JavaScript syntax, and `uv build`.
Push to the Openhook inbox repository and wait for its Test workflow.
Deploy only the dedicated Openhook Compose service through Dokploy.

The manual package workflow builds downloadable artifacts. PyPI is not published
automatically. To update the official MCP Registry listing, update `server.json`
with a new version, then run **Build distribution** with `publish_registry` enabled.
The optional job checks the listing identity and live tool discovery, verifies the
pinned publisher checksum, and authenticates using GitHub OIDC. It needs no stored
publisher token. Confirm the version is active in the public Registry after the run.

Registry publication does not deploy the application. Verify the exact deployed revision,
public endpoints, real event receipt, and durable storage before announcing a
release. See [deployment notes](deployment.md) and [testing](testing.md).
