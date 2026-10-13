"""Paid limits are enforced atomically for all capture transports."""

import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest
from starlette.testclient import TestClient

from openhook import hosted_store
from openhook.accounts import Accounts
from openhook_hosted.settings import HostedSettings as Settings
from openhook.store import InboxError, Store


@pytest.fixture
def hosted(tmp_path):
    store=Store(Settings(database=str(tmp_path/'hosted.sqlite3'),hosted_enabled=True))
    service=Accounts(store)
    account,_=service.sign_in(1,'owner')
    with store.connection() as db:
        db.execute('INSERT INTO hosted_entitlements(account,paid_until,status,updated) VALUES(?,?,?,?)',
                   (account['id'],time.time()+86400*31,'active',time.time()))
    return store,service,account['id']


def test_paid_inboxes_have_ownership_and_recoverable_private_access(hosted):
    store,service,account=hosted
    inbox=store.create(account=account,name='Stable endpoint')
    assert inbox['hosted'] is True
    with store.connection() as db:
        assert db.execute('SELECT expires FROM inboxes WHERE id=?',(inbox['inbox_id'],)).fetchone()[0]>time.time()+86400*60
    assert service.inboxes(account)[0]['id']==inbox['inbox_id']
    other,_=service.sign_in(2,'other')
    assert service.inboxes(other['id'])==[]
    with pytest.raises(InboxError):service.inbox_access(other['id'],inbox['inbox_id'])
    access=service.inbox_access(account,inbox['inbox_id'])
    store.capture(inbox['inbox_id'],b'cross-device')
    assert store.request(access['token'])['request']['content']=='cross-device'
    rotated=store.rotate(inbox['token'])
    with pytest.raises(InboxError):store.info(access['token'])
    assert store.info(rotated['token'])['url']==inbox['url']


def test_free_account_cannot_create_paid_inbox_or_impersonate_owner(hosted):
    store,service,account=hosted
    free,_=service.sign_in(2,'free')
    with pytest.raises(InboxError) as exc:store.create(account=free['id'])
    assert exc.value.status==402
    assert store.create()['hosted'] is False
    key=service.create_key(account,'agent')
    from openhook_hosted.app import create_app
    with TestClient(create_app(store.settings),base_url=store.settings.origin) as client:
        created=client.post('/api/account/inboxes',headers={'Authorization':'Bearer '+key['key']},json={'name':'Agent inbox'})
        assert created.status_code==201
        assert created.json()['data']['hosted'] is True
        # Caller-supplied ownership is never accepted by the anonymous API.
        anonymous=client.post('/api/call',json={'action':'create','account':account})
        assert anonymous.json()['data']['hosted'] is False
        service.revoke_key(account,key['id'])
        assert client.get('/api/account/inboxes',headers={'Authorization':'Bearer '+key['key']}).status_code==401


def test_all_transports_share_atomic_monthly_quota_without_deletion_reset(hosted,monkeypatch):
    store,service,account=hosted
    monkeypatch.setattr(hosted_store,'PRO_MONTHLY_EVENTS',3)
    inbox=store.create(account=account)
    for kind in ('web','email','dns'):store.capture(inbox['inbox_id'],kind.encode(),kind=kind)
    assert service.usage(account)['events']==3
    store.delete_requests(inbox['token'])
    with pytest.raises(InboxError,match='monthly'):store.capture(inbox['inbox_id'],b'fourth')
    assert service.usage(account)['events']==3
    assert store.requests(inbox['token'])['total_requests']==0


def test_concurrent_receipts_cannot_overspend_quota(hosted,monkeypatch):
    store,service,account=hosted
    monkeypatch.setattr(hosted_store,'PRO_MONTHLY_EVENTS',1)
    inbox=store.create(account=account)
    def capture(number):
        try:store.capture(inbox['inbox_id'],str(number).encode());return 'accepted'
        except InboxError as exc:return exc.status
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(capture,(1,2)))
    assert results.count('accepted')==1 and results.count(429)==1
    assert service.usage(account)['events']==1


def test_duplicate_and_failed_audit_do_not_consume_extra_quota(hosted):
    store,service,account=hosted
    inbox=store.create(account=account)
    store.capture(inbox['inbox_id'],b'once',source_id='delivery')
    duplicate=store.capture(inbox['inbox_id'],b'once',source_id='delivery')
    assert duplicate['duplicate'] and service.usage(account)['events']==1
    with store.connection() as db:
        db.execute("CREATE TRIGGER fail_history BEFORE INSERT ON activity BEGIN SELECT RAISE(ABORT,'history failed'); END")
    with pytest.raises(sqlite3.IntegrityError):store.capture(inbox['inbox_id'],b'not accepted')
    assert service.usage(account)['events']==1


def test_storage_and_inbox_limits_preserve_accepted_events(hosted,monkeypatch):
    store,service,account=hosted
    monkeypatch.setattr(hosted_store,'PRO_INBOXES',1)
    inbox=store.create(account=account)
    with pytest.raises(InboxError,match='inbox limit'):store.create(account=account)
    event=store.capture(inbox['inbox_id'],b'keep this')
    monkeypatch.setattr(hosted_store,'PRO_RETAINED_BYTES',service.usage(account)['retained_bytes'])
    with pytest.raises(InboxError,match='storage'):store.capture(inbox['inbox_id'],b'over capacity')
    assert store.request(inbox['token'],event['uuid'])['request']['content']=='keep this'
    assert service.usage(account)['events']==1


def test_retention_records_expiry_without_deleting_persistent_endpoint(hosted):
    store,service,account=hosted
    inbox=store.create(account=account)
    event=store.capture(inbox['inbox_id'],b'old payload')
    with store.connection() as db:
        db.execute('UPDATE events SET created=? WHERE id=?',(time.time()-31*86400,event['uuid']))
    store.cleanup()
    assert store.info(inbox['token'])['requests_count']==0
    assert store.activity(inbox['token'])['activity'][-1]['action']=='event.expired'
    assert service.usage(account)['events']==1
    assert service.usage(account)['retained_bytes']==0


def test_expired_payment_blocks_capture_but_keeps_data_readable(hosted):
    store,service,account=hosted
    inbox=store.create(account=account)
    store.capture(inbox['inbox_id'],b'already paid for')
    with store.connection() as db:
        db.execute('UPDATE hosted_entitlements SET paid_until=?',(time.time()-1,))
    with pytest.raises(InboxError) as exc:store.capture(inbox['inbox_id'],b'unpaid')
    assert exc.value.status==402
    assert store.request(inbox['token'])['request']['content']=='already paid for'
    assert service.inbox_access(account,inbox['inbox_id'])['url']==inbox['url']
    assert service.usage(account)['plan']=='free'


def test_calendar_rollover_does_not_apply_a_second_per_inbox_quota(hosted,monkeypatch):
    store,service,account=hosted
    monkeypatch.setattr(hosted_store,'PRO_MONTHLY_EVENTS',1)
    inbox=store.create(account=account)
    monkeypatch.setattr(hosted_store,'month_at',lambda now:'2026-09')
    store.capture(inbox['inbox_id'],b'last month')
    monkeypatch.setattr(hosted_store,'month_at',lambda now:'2026-10')
    store.capture(inbox['inbox_id'],b'this month')
    assert store.requests(inbox['token'])['total_requests']==2
    assert service.usage(account)['events']==1


def test_notes_cannot_bypass_retained_storage_limit(hosted,monkeypatch):
    store,service,account=hosted
    inbox=store.create(account=account)
    event=store.capture(inbox['inbox_id'],b'keep')
    monkeypatch.setattr(hosted_store,'PRO_RETAINED_BYTES',service.usage(account)['retained_bytes'])
    with pytest.raises(InboxError,match='storage'):
        store.update_request(inbox['token'],event['uuid'],'extra data')
    assert store.request(inbox['token'],event['uuid'])['request']['note']==''


def test_hosted_mcp_uses_owned_inboxes_and_rejects_revoked_account_keys(hosted):
    store,service,account=hosted
    key=service.create_key(account,'MCP')
    from openhook_hosted.app import create_app
    with TestClient(create_app(store.settings),base_url=store.settings.origin) as client:
        def tool(name,arguments):
            response=client.post('/mcp',headers={'Accept':'application/json, text/event-stream'},json={
                'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':name,'arguments':arguments}})
            result=response.json()['result']
            return result if result.get('isError') else json.loads(result['content'][0]['text'])
        inbox=tool('create_webhook',{'account_key':key['key'],'name':'Owned from MCP'})
        assert inbox['hosted'] is True
        listed=tool('get_hosted_inboxes',{'account_key':key['key']})
        assert listed['inboxes'][0]['id']==inbox['inbox_id']
        access=tool('access_hosted_inbox',{'account_key':key['key'],'inbox_id':inbox['inbox_id']})
        assert store.info(access['token'])['url']==inbox['url']
        service.revoke_key(account,key['id'])
        assert tool('get_hosted_inboxes',{'account_key':key['key']})['isError'] is True


def test_owned_inboxes_cannot_silently_fall_back_to_anonymous_mode(hosted):
    store,service,account=hosted
    store.create(account=account)
    with pytest.raises(InboxError,match='Keep hosted mode enabled'):
        Store(replace(store.settings,hosted_enabled=False))
