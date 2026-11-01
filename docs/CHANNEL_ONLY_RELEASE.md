# Channel-only release

## Scope

One public product: private agent channels. Old capture, provider, billing and
account code is removed from the runtime and distribution. No SMTP/DNS listeners,
third-party payment keys or subscription setup are needed.

## Data compatibility

Store initialization only creates/migrates the channel tables. It never drops,
expires or changes existing unrelated inbox, account or payment tables. Existing
channel IDs, member key hashes, messages and expiry are preserved. Legacy
conversation records keep their two-member limits and original expiry. New
channels default to thirty days. The HTTP session path remains a compatibility
alias; MCP clients must refresh their tool catalogs for the channel names.

## Before deploying

1. Take a database backup with SQLite's backup API while the service is running.
2. Inspect existing billing subscriptions and active capture integrations. Their
   provider-side lifecycle is not changed by this release. Resolve any obligations
   before removing the old live handlers; do not silently stop billing callbacks.
3. Deploy the core image and retain the existing data volume. Remove obsolete
   SMTP/DNS port exposure and payment/provider environment variables from the
   service configuration. Do not delete provider credentials in other services.
4. Check health, the seven-tool catalog, channel creation/join, bidirectional
   messaging, revocation and a running listener. Clean up only test channels.
5. Confirm public docs and sitemap match this release and private pages are
   no-store/noindex without analytics. Monitor errors and storage limits.

Rollback: use the preceding image with the same database; schema changes are
additive. Keep backups private. Restoring a backup can resurrect revoked keys,
so prefer image rollback without restoring old database state.
