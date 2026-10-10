"""Read-only aggregate launch scorecard; no customer identifiers or payloads."""

import argparse
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path


def report(path):
    connection = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    try:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if 'hosted_entitlements' not in tables:
            return {'hosted_configured': False}
        now = time.time()
        month = datetime.fromtimestamp(now, timezone.utc).strftime('%Y-%m')
        scalar = lambda query, args=(): connection.execute(query, args).fetchone()[0]
        return {
            'hosted_configured': True, 'as_of_utc': datetime.fromtimestamp(now, timezone.utc).isoformat(),
            'accounts': scalar('SELECT COUNT(*) FROM accounts'),
            'accounts_with_paid_time': scalar('SELECT COUNT(*) FROM hosted_entitlements WHERE paid_until>?', (now,)),
            'accounts_ever_paid': scalar('SELECT COUNT(DISTINCT account) FROM paid_invoices'),
            'inboxes': scalar('SELECT COUNT(*) FROM hosted_inboxes'),
            'calendar_month_utc': month,
            'accepted_events_this_month': scalar('SELECT COALESCE(SUM(events),0) FROM account_usage WHERE month=?', (month,)),
            'verified_paid_invoices': scalar('SELECT COUNT(*) FROM paid_invoices'),
            'recorded_invoice_amount_paid_usd_cents': scalar('SELECT COALESCE(SUM(amount_paid),0) FROM paid_invoices WHERE currency=\'usd\''),
            'retained_event_bytes': scalar('SELECT COALESCE(SUM(length(CAST(e.payload AS BLOB))),0) FROM events e JOIN hosted_inboxes h ON h.inbox=e.inbox'),
            'note': 'Invoice amounts are not net revenue or MRR. Reconcile live/test mode, refunds, taxes, fees and subscription status in Stripe.',
        }
    finally:
        connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', help='Existing SQLite database or consistent backup')
    print(json.dumps(report(parser.parse_args().database), indent=2))
