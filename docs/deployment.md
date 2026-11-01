# Deploy Openhook channels

Run one application replica using `compose.dokploy.yaml`, service `openhook`,
core image target. Set `OPENHOOK_ORIGIN=https://openhook.dev`; route that domain
through the trusted HTTPS reverse proxy to container port 8788. No SMTP or DNS
ports are exposed. Keep the persistent `openhook-data` volume mounted at `/data`.

Only trust the actual reverse proxy subnet in `FORWARDED_ALLOW_IPS`. Confirm
client IP handling so per-IP rate limits do not group all traffic under one proxy.
Keep body/token logging disabled in the application and proxy.

The database uses WAL and short write transactions. Use SQLite's backup API for
online backups; copying only the database file can omit WAL transactions. Keep
backups private. They contain server-readable channel messages. Restoring stale
backups may restore previously revoked keys.

Channels expire after their chosen lifetime (30 days by default); access stops
immediately and periodic cleanup removes expired channel rows. No cleanup touches
retired billing/account/inbox tables. Capacity is bounded and new writes fail
instead of evicting retained history. Revocation and deletion remain possible
when event capacity is exhausted.

See [channel-only rollout](CHANNEL_ONLY_RELEASE.md) before upgrading an existing
hosted service. Provider-side subscriptions require separate handling; this code
does not cancel them. Verify the exact deployed revision, TLS, health, seven-tool
catalog, an invite/join/send/read round trip and revocation before announcing.
