from openhook.accounts import Accounts
from openhook_hosted.settings import HostedSettings as Settings
from openhook.store import Store
from scripts.business_report import report


def test_polar_scorecard_counts_orders_and_labels_refunded_amounts(tmp_path):
    path = str(tmp_path / 'report.db')
    store = Store(Settings(database=path, hosted_enabled=True, billing_provider='polar'))
    account, _ = Accounts(store).sign_in(1, 'test-buyer')
    with store.connection() as db:
        db.execute('INSERT INTO polar_orders VALUES(?,?,?,?,?,?,?)', ('order1', account['id'], 'sub1', 100, 1900, 0, 0))
        db.execute('INSERT INTO polar_orders VALUES(?,?,?,?,?,?,?)', ('order2', account['id'], 'sub1', 200, 1900, 1, 0))
    result = report(path)
    assert result['billing_provider'] == 'polar' and result['sandbox'] is True
    assert result['accounts_ever_paid'] == 1
    assert result['verified_polar_orders'] == 2
    assert result['fully_refunded_polar_orders'] == 1
    assert result['recorded_polar_order_net_amount_usd_cents'] == 3800
    assert result['verified_paid_invoices'] == 0
    assert 'include subsequently refunded orders' in result['note']
