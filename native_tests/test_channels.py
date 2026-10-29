"""Authorization, migration, lifecycle and transport tests for shared channels."""
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from starlette.testclient import TestClient

from openhook.errors import InboxError
from openhook.sessions import Sessions, CHANNEL_DEFAULT_EXPIRY
from openhook.settings import Settings
from openhook.store import Store, token_hash
from openhook.web import create_app


@pytest.fixture
def service(tmp_path):
    return Sessions(Store(Settings(database=str(tmp_path / 'channels.db'), origin='http://testserver')))


def owner(service):
    return service.create('Owner', 'Launch channel', CHANNEL_DEFAULT_EXPIRY, channel=True, scope='Plan only. No publishing.')


def test_multiple_members_scoped_invites_and_unverified_identity(service):
    a = owner(service); at = a['participant_token']
    b = service.join(a['invite_url'], 'Business')
    invite = service.invite(at, 'read')
    c = service.join(invite['invite_url'], 'Observer')
    service.send(b['participant_token'], 'Here is a proposal', 'proposal')
    assert service.read(c['participant_token'])['events'][-1]['text'] == 'Here is a proposal'
    with pytest.raises(InboxError) as exc:
        service.send(c['participant_token'], 'Not allowed', 'forbidden')
    assert exc.value.status == 403
    assert c['permission'] == 'read' and c['scope'] == 'Plan only. No publishing.'
    info = service.info(at)
    assert len(info['participants']) == 3 and info['member_limit'] == 16
    assert info['identity_verified'] is False and info['channel'] is True
    assert service.info(c['participant_token'])['participants'][-1]['last_seen'] is not None
    assert at not in json.dumps(info)


@pytest.mark.parametrize('operation', ['invite', 'archive', 'renew', 'close', 'revoke'])
def test_guest_cannot_administer_channel(service, operation):
    a = owner(service); b = service.join(a['invite_code'], 'Guest')
    arguments = [b['participant_token']]
    if operation == 'revoke': arguments.append(a['participant_id'])
    with pytest.raises(InboxError) as exc:
        getattr(service, operation)(*arguments)
    assert exc.value.status == 403


def test_invites_single_use_rotation_and_capacity(service, monkeypatch):
    monkeypatch.setattr('openhook.sessions.CHANNEL_MEMBERS', 3)
    a = owner(service); at = a['participant_token']
    fresh = service.invite(at)
    with pytest.raises(InboxError): service.join(a['invite_url'], 'Old')
    b = service.join(fresh['invite_url'], 'B')
    invite = service.invite(at)
    def join(i):
        try: return service.join(invite['invite_code'], f'Guest-{i}')['status']
        except InboxError as exc: return exc.status
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(join, [1, 2]))
    assert sorted(map(str, results)) == ['404', 'active']
    with pytest.raises(InboxError): service.invite(at)
    service.revoke(at, b['participant_id'])
    service.join(service.invite(at)['invite_code'], 'Replacement')


def test_archive_revokes_unused_invite_but_keeps_history_and_restore(service):
    a = owner(service); at = a['participant_token']
    b = service.join(a['invite_code'], 'Guest'); bt = b['participant_token']
    service.send(bt, 'History', 'history')
    invite = service.invite(at)
    service.archive(at)
    assert service.read(bt)['archived'] is True
    assert any(e['text'] == 'History' for e in service.read(bt)['events'])
    for operation in (lambda: service.send(bt, 'Blocked', 'blocked'), lambda: service.invite(at)):
        with pytest.raises(InboxError) as exc: operation()
        assert exc.value.status == 409
    with pytest.raises(InboxError): service.join(invite['invite_url'], 'Late')
    service.archive(at, False)
    with pytest.raises(InboxError): service.join(invite['invite_url'], 'Still invalid')
    service.send(bt, 'Restored', 'restore')


def test_rotation_disconnects_old_key_without_changing_membership(service):
    a = owner(service); b = service.join(service.invite(a['participant_token'], 'read')['invite_code'], 'Reader')
    rotated = service.rotate(b['participant_token'])
    with pytest.raises(InboxError) as exc: service.info(b['participant_token'])
    assert exc.value.status == 401
    info = service.info(rotated['participant_token'])
    assert info['permission'] == 'read' and info['participant_id'] == b['participant_id']
    with pytest.raises(InboxError): service.send(rotated['participant_token'], 'Still read only', 'x')
    with service.store.connection() as db:
        assert rotated['participant_token'] not in json.dumps([dict(r) for r in db.execute('SELECT * FROM session_members')])
    assert service.leave(rotated['participant_token'])['left']
    with pytest.raises(InboxError): service.read(rotated['participant_token'])
    with pytest.raises(InboxError): service.leave(a['participant_token'])


def test_renew_is_idempotent_in_direction_and_existing_conversations_unchanged(service):
    a = owner(service); at = a['participant_token']
    initial = service.info(at)['expires_at']
    assert service.renew(at, 60)['expires_at'] == initial
    assert service.renew(at, 90 * 86400)['expires_at'] > initial
    with pytest.raises(InboxError): service.renew(at, 91 * 86400)
    old = service.create('Legacy', 'Two person')
    service.join(old['invite_code'], 'Legacy guest')
    with pytest.raises(InboxError): service.invite(old['participant_token'])
    with pytest.raises(InboxError): service.renew(old['participant_token'])


def test_isolation_and_disconnect_when_history_full(service, monkeypatch):
    a = owner(service); b = service.join(a['invite_code'], 'Guest')
    other = owner(service)
    with pytest.raises(InboxError): service.revoke(other['participant_token'], b['participant_id'])
    with pytest.raises(InboxError): service.info(a['session_id'])
    monkeypatch.setattr('openhook.sessions.EVENT_LIMIT', 2)
    with pytest.raises(InboxError): service.invite(a['participant_token'])
    with pytest.raises(InboxError): service.send(a['participant_token'], 'full', 'full')
    service.revoke(a['participant_token'], b['participant_id'])
    service.archive(a['participant_token'])
    with service.store.connection() as db:
        assert db.execute('SELECT count(*) FROM session_events WHERE session=?', (a['session_id'],)).fetchone()[0] == 2
    service.close(a['participant_token'])
    with pytest.raises(InboxError): service.info(a['participant_token'])


def test_legacy_schema_migration_preserves_keys_messages_and_extended_expiry(tmp_path):
    path = tmp_path / 'old.db'; expires = time.time() + 31 * 86400
    with sqlite3.connect(path) as db:
        db.executescript('''
        CREATE TABLE agent_sessions(id TEXT PRIMARY KEY,title TEXT NOT NULL,created REAL NOT NULL,expires REAL NOT NULL,invite_hash TEXT,invite_expires REAL);
        CREATE TABLE session_members(id TEXT PRIMARY KEY,session TEXT NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,token_hash TEXT NOT NULL UNIQUE,name TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('owner','guest')),status TEXT NOT NULL CHECK(status IN ('active','revoked')));
        CREATE TABLE session_events(sequence INTEGER PRIMARY KEY AUTOINCREMENT,session TEXT NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,sender TEXT NOT NULL REFERENCES session_members(id),kind TEXT NOT NULL,body TEXT NOT NULL,created REAL NOT NULL,message_id TEXT,UNIQUE(session,sender,message_id));
        ''')
        db.execute('INSERT INTO agent_sessions VALUES(?,?,?,?,NULL,NULL)', ('old', 'Existing', time.time(), expires))
        db.execute('INSERT INTO session_members VALUES(?,?,?,?,?,?)', ('member', 'old', token_hash('ohp_existing'), 'Owner', 'owner', 'active'))
        db.execute('INSERT INTO session_events(session,sender,kind,body,created) VALUES(?,?,?,?,?)', ('old','member','message','Keep me',time.time()))
    settings = Settings(database=str(path), origin='http://testserver')
    for _ in range(2):
        service = Sessions(Store(settings))
        assert service.info('ohp_existing')['channel'] is False
        assert service.read('ohp_existing')['events'][0]['text'] == 'Keep me'
        with service.store.connection() as db:
            assert db.execute('SELECT expires FROM agent_sessions WHERE id=?', ('old',)).fetchone()[0] == expires


def test_channel_http_and_mcp_contract_and_private_page(service):
    with TestClient(create_app(service.store.settings)) as client:
        def http(action, **args):
            r = client.post('/api/v1/channels', json={'action': action, **args})
            assert r.status_code == 200, r.text
            assert r.headers['cache-control'] == 'no-store'
            return r.json()['data']
        def mcp(tool_name, **arguments):
            r = client.post('/mcp', headers={'Accept': 'application/json, text/event-stream'}, json={
                'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':tool_name,'arguments':arguments}}).json()['result']
            assert not r.get('isError')
            return json.loads(r['content'][0]['text'])
        a = http('create', name='Owner', title='API channel')
        b = mcp('join_agent_session', invite_code=a['invite_url'], name='Guest')
        invite = mcp('manage_agent_channel', participant_token=a['participant_token'], action='invite', permission='read')
        c = http('join', invite_code=invite['invite_code'], name='Reader')
        mcp('send_agent_message', participant_token=b['participant_token'], text='Hello reader', message_id='one')
        assert http('read', participant_token=c['participant_token'])['events'][-1]['text'] == 'Hello reader'
        assert client.post('/api/v1/channels', json={'action':'send','participant_token':c['participant_token'],'text':'forbidden','message_id':'no'}).status_code == 403
        page = client.get('/channels')
        assert page.status_code == 200 and page.headers['cache-control'] == 'no-store'
        assert 'noindex' in page.headers['x-robots-tag'] and '{{' not in page.text
        assert 'Channels' in client.get('/').text
        assert '/api/v1/channels' in client.get('/openapi.json').json()['paths']
        assert '/channels' not in client.get('/sitemap.xml').text
        assert client.post('/api/v1/channels', headers={'Origin':'https://evil.test'}, json={'action':'create','name':'X','title':'X'}).status_code == 403
        assert client.get('/api/v1/channels?participant_token=ohp_test').status_code == 405
