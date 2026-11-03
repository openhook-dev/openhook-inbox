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

## Storage encryption

This encrypts event bodies with server-held keys. It is **not end-to-end
encryption**: the running service can decrypt, and titles, scope, names,
timestamps and membership metadata remain visible. Local listener queues and
pre-existing backups are separate copies and are not encrypted by this setting.

Generate a new key ring without printing its contents:

```sh
uv run python scripts/storage_key.py /private/operator/path/openhook-storage-keys.json
```

Keep the file outside the source checkout and database backups. It must be an
owned regular file with no group/other permissions (0600 or 0400); never commit
it. For the container, assign ownership to UID 10001 on the Linux host. Back up
keys privately and separately: losing every decryption key loses the messages.
Do not use a password as a key or put key contents in command arguments.

Set `OPENHOOK_STORAGE_KEY_FILE` to the file path for every HTTP and stdio process
that opens this database. A separate read-only Compose secret mount is supplied:

```sh
export OPENHOOK_STORAGE_KEY_HOST_FILE=/private/operator/path/openhook-storage-keys.json
docker compose -f compose.yaml -f compose.encrypted.yaml up --build -d
```

For hosted Compose, use `compose.dokploy.yaml` as the base instead. A fresh
self-hosted database without the setting remains plaintext. Once protection is
enabled, removing the setting is an error, including after all channels are
removed. Never run an older application image against the protected database.

For existing data, stop **all** writers first, including stdio agents. Make a
consistent private backup using SQLite's backup API. Start the new version with
the key file configured: startup validates retained ciphertext and encrypts
previous plaintext bodies in one transaction, preserving member keys, event IDs
and channel expiry. No traffic is accepted if verification fails. Allow space
for ciphertext expansion; make sure a staging backup round trip passes first.

A row rewrite does not erase prior plaintext from filesystem history. During
the maintenance window, with other writers stopped, use SQLite `VACUUM` and
`PRAGMA wal_checkpoint(TRUNCATE)` to compact the current database/WAL after the
migration. Check the checkpoint result: a busy result means other connections
still exist. Separately manage pre-migration backups and filesystem snapshots;
never claim secure erasure of those copies or delete the only recovery backup.

For rotation, stop every writer, securely prepend a newly generated Fernet key
to the JSON list (maximum eight keys), then start this version. It validates and
rewrites retained bodies under the first key atomically; older keys remain
available for decryption. After verifying the migrated database, remove old keys
from the live ring and restart. Keep keys needed for retained backups separately.
Never run old-key writers concurrently with rotation. Missing/wrong keys,
modified ciphertext and plaintext writes into protected storage fail closed.

### Hosted secret-volume bootstrap

`compose.dokploy.yaml` requires `/run/openhook-secrets/storage-keys.json` and
mounts the separate `openhook-secrets` volume read-only in the application.
Before the first encrypted hosted rollout, initialize that volume with a private
JSON key ring, owned by UID 10001 and mode 0600. The mount directory should be
owned by UID 10001 and mode 0700. Keep the volume outside database-only backups.
The app refuses startup if the key is absent, unreadable, public or invalid.
Do not roll an older release back onto the encrypted database: restore a tested
matching database/key backup or deploy a compatible fixed version instead.
