"""Hosted plan policy, enforced inside the capture store's write transaction.

No payment calls happen here. A billing adapter is responsible for recording
verified paid-through dates; a browser redirect can never grant access.
"""

from datetime import datetime, timezone

from openhook.errors import InboxError

PRO_INBOXES = 10
PRO_MONTHLY_EVENTS = 50_000
PRO_RETAINED_BYTES = 1_073_741_824
PRO_RETENTION_SECONDS = 30 * 86400


def initialize(db, *, stripe_live=False, billing_provider="stripe", polar_sandbox=True):
    db.executescript("""
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY, github_id INTEGER NOT NULL UNIQUE,
            login TEXT NOT NULL, created REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS account_sessions (
            key_hash TEXT PRIMARY KEY, account TEXT NOT NULL,
            created REAL NOT NULL, expires REAL NOT NULL,
            FOREIGN KEY (account) REFERENCES accounts(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS account_sessions_owner ON account_sessions(account, created);
        CREATE TABLE IF NOT EXISTS oauth_states (
            state_hash TEXT PRIMARY KEY, verifier TEXT NOT NULL, expires REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS account_keys (
            id TEXT PRIMARY KEY, account TEXT NOT NULL, name TEXT NOT NULL,
            key_hash TEXT NOT NULL UNIQUE, suffix TEXT NOT NULL,
            created REAL NOT NULL, revoked REAL,
            FOREIGN KEY (account) REFERENCES accounts(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS account_keys_owner ON account_keys(account, created);
        CREATE TABLE IF NOT EXISTS hosted_entitlements (
            account TEXT PRIMARY KEY, paid_until REAL NOT NULL DEFAULT 0,
            customer_id TEXT UNIQUE, subscription_id TEXT UNIQUE,
            status TEXT NOT NULL DEFAULT 'free', updated REAL NOT NULL,
            FOREIGN KEY (account) REFERENCES accounts(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS hosted_inboxes (
            inbox TEXT PRIMARY KEY, account TEXT NOT NULL,
            FOREIGN KEY (inbox) REFERENCES inboxes(id) ON DELETE CASCADE,
            FOREIGN KEY (account) REFERENCES accounts(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS hosted_inboxes_owner ON hosted_inboxes(account);
        CREATE TABLE IF NOT EXISTS account_usage (
            account TEXT NOT NULL, month TEXT NOT NULL, events INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (account,month),
            FOREIGN KEY (account) REFERENCES accounts(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS inbox_access (
            key_hash TEXT PRIMARY KEY, inbox TEXT NOT NULL, created REAL NOT NULL, expires REAL NOT NULL,
            FOREIGN KEY (inbox) REFERENCES inboxes(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS inbox_access_inbox ON inbox_access(inbox);
        CREATE TABLE IF NOT EXISTS billing_attempts (
            account TEXT PRIMARY KEY REFERENCES accounts(id) ON DELETE CASCADE,
            identifier TEXT NOT NULL UNIQUE, created INTEGER NOT NULL,
            session_id TEXT, url TEXT
        );
        CREATE TABLE IF NOT EXISTS billing_events (
            id TEXT PRIMARY KEY, kind TEXT NOT NULL, processed REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS paid_invoices (
            id TEXT PRIMARY KEY, account TEXT NOT NULL REFERENCES accounts(id),
            subscription_id TEXT NOT NULL, period_end REAL NOT NULL,
            amount_paid INTEGER NOT NULL, currency TEXT NOT NULL, created REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS polar_orders (
            id TEXT PRIMARY KEY, account TEXT NOT NULL REFERENCES accounts(id),
            subscription_id TEXT NOT NULL, period_end REAL NOT NULL,
            amount_paid INTEGER NOT NULL, refunded INTEGER NOT NULL DEFAULT 0,
            updated REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS polar_revocations (
            subscription_id TEXT PRIMARY KEY, account TEXT NOT NULL REFERENCES accounts(id)
        );
        CREATE TABLE IF NOT EXISTS billing_runtime (
            id INTEGER PRIMARY KEY CHECK(id=1), provider TEXT NOT NULL, sandbox INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS hosted_runtime (
            id INTEGER PRIMARY KEY CHECK(id=1), stripe_live INTEGER NOT NULL
        );
    """)
    if billing_provider not in {"stripe", "polar"}:
        raise InboxError("Unknown billing provider.", 503)
    sandbox = polar_sandbox if billing_provider == "polar" else not stripe_live
    previous = db.execute('SELECT provider,sandbox FROM billing_runtime WHERE id=1').fetchone()
    has_billing = db.execute("SELECT 1 FROM hosted_entitlements WHERE customer_id IS NOT NULL OR paid_until>0 LIMIT 1").fetchone()
    has_billing = has_billing or db.execute("SELECT 1 FROM billing_attempts LIMIT 1").fetchone()
    if has_billing and ((previous and (previous['provider'], bool(previous['sandbox'])) != (billing_provider, sandbox))
                        or (not previous and billing_provider != 'stripe')):
        raise InboxError("Billing provider or environment differs from existing accounts. Use a separate database.", 503)
    db.execute('INSERT INTO billing_runtime VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET provider=excluded.provider,sandbox=excluded.sandbox',
               (billing_provider, int(sandbox)))
    current = db.execute('SELECT stripe_live FROM hosted_runtime WHERE id=1').fetchone()
    if current and bool(current['stripe_live']) != stripe_live and db.execute('SELECT 1 FROM paid_invoices LIMIT 1').fetchone():
        raise InboxError('Payment mode differs from the invoice ledger. Use a separate database for Stripe sandbox tests.', 503)
    db.execute('INSERT INTO hosted_runtime VALUES(1,?) ON CONFLICT(id) DO UPDATE SET stripe_live=excluded.stripe_live', (int(stripe_live),))


def month_at(now):
    return datetime.fromtimestamp(now, timezone.utc).strftime('%Y-%m')


def require_paid(db, account, now):
    row = db.execute('SELECT * FROM hosted_entitlements WHERE account=?', (account,)).fetchone()
    if not row or row['paid_until'] <= now:
        raise InboxError('A paid hosted plan is required. Open your account to manage billing.', 402)
    return row


def owner(db, inbox):
    row = db.execute('SELECT account FROM hosted_inboxes WHERE inbox=?', (inbox,)).fetchone()
    return row['account'] if row else None


def retained_bytes(db, account):
    return db.execute('SELECT COALESCE(SUM(length(CAST(e.payload AS BLOB))),0) FROM events e '
                      'JOIN hosted_inboxes h ON h.inbox=e.inbox WHERE h.account=?', (account,)).fetchone()[0]


def reserve_capture(db, account, payload_bytes, now):
    require_paid(db, account, now)
    month = month_at(now)
    db.execute('INSERT INTO account_usage(account,month) VALUES(?,?) ON CONFLICT DO NOTHING', (account, month))
    used = db.execute('SELECT events FROM account_usage WHERE account=? AND month=?', (account, month)).fetchone()[0]
    if used >= PRO_MONTHLY_EVENTS:
        raise InboxError('Hosted monthly event limit reached. No overage charge was made.', 429)
    if retained_bytes(db, account) + payload_bytes > PRO_RETAINED_BYTES:
        raise InboxError('Hosted storage limit reached. Export or delete events before sending more.', 429)
    db.execute('UPDATE account_usage SET events=events+1 WHERE account=? AND month=?', (account, month))


def expire_payloads(db, audit, now):
    rows = db.execute('SELECT e.id,e.inbox,e.kind FROM events e JOIN hosted_inboxes h ON h.inbox=e.inbox '
                      'WHERE e.created<=?', (now - PRO_RETENTION_SECONDS,)).fetchall()
    for row in rows:
        audit(db, row['inbox'], 'event.expired', row['id'], {'type': row['kind']}, actor='system')
        db.execute('DELETE FROM events WHERE id=?', (row['id'],))
    db.execute('DELETE FROM inbox_access WHERE expires<=?', (now,))
