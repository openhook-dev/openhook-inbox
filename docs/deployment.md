# Deploy Openhook with Dokploy

Create a dedicated Openhook project and Docker Compose service. Select this
repository, compose.dokploy.yaml, and service openhook. Configure
OPENHOOK_ORIGIN=https://openhook.dev and OPENHOOK_BIND_ADDRESS to the host IPv4.
Bind SMTP/DNS to that public IP so the host resolver can retain loopback port 53. Add openhook.dev through Dokploy Domains:
service openhook, container port 8788, HTTPS and Let's Encrypt enabled.

The named openhook-data volume holds the SQLite database. Run one application
replica. Do not mount the repository directory as the data directory.

## Mail

Set OPENHOOK_EMAIL_DOMAIN=mail.openhook.dev. Point the domain's MX record to
smtp.openhook.dev. Point smtp.openhook.dev directly to the host's IPv4 address
with Cloudflare proxying disabled. Public TCP port 25 maps to container 2525.
Confirm the host permits incoming port 25. The service receives mail only;
there is no mail relay or outbound mail sender.

## DNS

Set OPENHOOK_DNS_DOMAIN=dns.openhook.dev and OPENHOOK_DNS_ADDRESS to the host's
IPv4 address. Delegate dns.openhook.dev to ns.dns.openhook.dev. Create an
unproxied A record for that nameserver, including glue where required by the
parent. Public UDP and TCP port 53 map to container 5353. Disable DNSSEC on the
delegated child zone until signing is implemented.

Do not enable either transport until DNS and inbound ports are configured.
Health reports configured listeners, not independent proof of public reachability.

## Storage and backups

Events are committed before an HTTP success response. WAL permits concurrent
SMTP, HTTP, and MCP access. Inboxes expire within seven days; cleanup runs every
minute, and every creation also removes expired inboxes. Each inbox accepts up to
1000 retained events. At capacity, new captures fail instead of evicting earlier
accepted events. Receipts and mutations write durable activity records in the
same transaction. Minimal history remains after payload deletion and expiry;
it excludes bodies, notes, and secrets.

Use SQLite's backup API for a consistent database copy. Copying only the live
.sqlite3 file can miss transactions in its WAL. Keep backups private; they
contain captured events and signing secrets. Dokploy named-volume backups can
preserve an entire stopped volume; for online backups use SQLite's backup API.

## Release verification

Verify /health, HTTPS, the deployed Git SHA, container readiness, and a real
create → HTTP callback → MCP read/wait loop. For mail, deliver through the public
MX. For DNS, use a public recursive resolver and inspect the recorded lookup.
Also verify that a public capture UUID cannot read the inbox through /api/call.

Trust only the verified Dokploy proxy subnet with FORWARDED_ALLOW_IPS. If using
Cloudflare proxying, also add its published IP ranges. Confirm actual sender IPs
in captured events so rate limits do not group all visitors under the proxy IP.
