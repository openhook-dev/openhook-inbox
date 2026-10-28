"""Real SQLite and HTTP/MCP tests for two independent agent participants."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import time

import pytest
from starlette.testclient import TestClient

from openhook.errors import InboxError
from openhook.sessions import Sessions
from openhook.settings import Settings
from openhook.store import Store
from openhook.web import create_app


@pytest.fixture
def sessions(tmp_path):
    return Sessions(Store(Settings(database=str(tmp_path / 'sessions.db'), origin='http://testserver')))


def pair(sessions):
    owner = sessions.create('Engineer', 'Release planning')
    guest = sessions.join(owner['invite_code'], 'Partner')
    sessions.set_participant(owner['participant_token'], guest['participant_id'], approve=True)
    return owner, guest


def test_pending_participant_cannot_read_or_send(sessions):
    owner = sessions.create('Engineer', 'Private title')
    sessions.send(owner['participant_token'], 'private history', 'before-join')
    guest = sessions.join(owner['invite_code'], 'Partner')
    token = guest['participant_token']
    info = sessions.info(token)
    assert info['status'] == 'pending'
    assert 'title' not in info and 'participants' not in info
    for operation in (lambda: sessions.read(token), lambda: sessions.send(token, 'hello', '1')):
        with pytest.raises(InboxError) as error:
            operation()
        assert error.value.status == 403
    sessions.set_participant(owner['participant_token'], guest['participant_id'], approve=True)
    assert any(e['text'] == 'private history' for e in sessions.read(token)['events'])


def test_independent_tokens_bidirectional_messages_and_retries(sessions):
    owner, guest = pair(sessions)
    first = sessions.send(owner['participant_token'], 'Can we ship Friday?', 'request-1')
    assert sessions.send(owner['participant_token'], 'Can we ship Friday?', 'request-1') == {**first, 'duplicate': True}
    with pytest.raises(InboxError) as error:
        sessions.send(owner['participant_token'], 'Different request', 'request-1')
    assert error.value.status == 409
    sessions.send(guest['participant_token'], 'Yes, after review.', 'request-1')
    events = [e for e in sessions.read(owner['participant_token'])['events'] if e['kind'] == 'message']
    assert [e['is_self'] for e in events] == [True, False]
    assert [e['sender_id'] for e in events] == [owner['participant_id'], guest['participant_id']]
    assert events[0]['sequence'] < events[1]['sequence']


def test_tokens_hashing_persistence_and_cursor_pagination(sessions):
    owner, guest = pair(sessions)
    sessions.send(owner['participant_token'], 'Resume after restart', 'message')
    reopened = Sessions(Store(sessions.store.settings))
    with reopened.store.connection() as db:
        saved = json.dumps([dict(row) for row in db.execute('SELECT * FROM session_members')])
        saved += json.dumps([dict(row) for row in db.execute('SELECT * FROM agent_sessions')])
    assert owner['participant_token'] not in saved and guest['participant_token'] not in saved
    assert owner['invite_code'] not in saved
    cursor, collected = 0, []
    while True:
        page = reopened.read(guest['participant_token'], cursor, limit=1)
        collected.extend(page['events'])
        cursor = page['next_since']
        if not page['has_more']:
            break
    assert collected == reopened.read(guest['participant_token'])['events']
    assert reopened.read(guest['participant_token'], cursor)['events'] == []


def test_session_isolation_and_owner_privileges(sessions):
    owner, guest = pair(sessions)
    other = sessions.create('Other', 'Another session')
    sessions.send(other['participant_token'], 'foreign secret', 'one')
    assert 'foreign secret' not in json.dumps(sessions.read(owner['participant_token']))
    for invalid in (owner['session_id'], owner['invite_code'], guest['participant_id'], 'ohp_wrong'):
        with pytest.raises(InboxError):
            sessions.info(invalid)
    for operation in (
        lambda: sessions.set_participant(other['participant_token'], guest['participant_id'], approve=True),
        lambda: sessions.set_participant(guest['participant_token'], owner['participant_id'], approve=False),
        lambda: sessions.set_participant(owner['participant_token'], owner['participant_id'], approve=False),
        lambda: sessions.invite(guest['participant_token']),
        lambda: sessions.close(guest['participant_token']),
    ):
        with pytest.raises(InboxError):
            operation()


def test_single_use_invite_is_atomic(sessions):
    owner = sessions.create('Owner', 'Concurrent joins')
    def join(name):
        try:
            return sessions.join(owner['invite_code'], name)['status']
        except InboxError as error:
            return error.status
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(join, ['A', 'B']))
    assert sorted(results, key=str) == [404, 'pending']
    with pytest.raises(InboxError):
        sessions.invite(owner['participant_token'])


def test_invite_rotation_expiry_and_replacement(sessions):
    owner = sessions.create('Owner', 'Invitation')
    replacement = sessions.invite(owner['participant_token'])
    with pytest.raises(InboxError):
        sessions.join(owner['invite_code'], 'Partner')
    with sessions.store.connection(write=True) as db:
        db.execute('UPDATE agent_sessions SET invite_expires=?', (time.time() - 1,))
    with pytest.raises(InboxError):
        sessions.join(replacement['invite_code'], 'Partner')
    replacement = sessions.invite(owner['participant_token'])
    guest = sessions.join(replacement['invite_code'], 'Wrong person')
    sessions.set_participant(owner['participant_token'], guest['participant_id'], approve=False)
    with pytest.raises(InboxError):
        sessions.set_participant(owner['participant_token'], guest['participant_id'], approve=True)
    new_guest = sessions.join(sessions.invite(owner['participant_token'])['invite_code'], 'Partner')
    assert new_guest['participant_token'] != guest['participant_token']


@pytest.mark.asyncio
async def test_wait_receives_message_then_revocation_ends_wait(sessions):
    owner, guest = pair(sessions)
    token = guest['participant_token']
    cursor = sessions.read(token)['next_since']
    waiting = asyncio.create_task(sessions.wait(token, cursor, 1))
    await asyncio.sleep(.01)
    sessions.send(owner['participant_token'], 'Incoming task', 'task')
    result = await waiting
    assert result['events'][0]['text'] == 'Incoming task'
    waiting = asyncio.create_task(sessions.wait(token, result['next_since'], 1))
    await asyncio.sleep(.01)
    sessions.set_participant(owner['participant_token'], guest['participant_id'], approve=False)
    with pytest.raises(InboxError) as error:
        await waiting
    assert error.value.status == 401
    with pytest.raises(InboxError):
        sessions.send(token, 'No further access', 'revoked')


@pytest.mark.parametrize('cleanup', ['close', 'expire'])
def test_deletion_removes_messages_and_credentials(sessions, cleanup):
    owner, guest = pair(sessions)
    sessions.send(guest['participant_token'], 'Delete me', 'one')
    if cleanup == 'close':
        sessions.close(owner['participant_token'])
    else:
        with sessions.store.connection(write=True) as db:
            db.execute('UPDATE agent_sessions SET expires=?', (time.time() - 1,))
        with pytest.raises(InboxError):
            sessions.read(guest['participant_token'])
        sessions.store.cleanup()
    with sessions.store.connection() as db:
        for table in ('agent_sessions', 'session_members', 'session_events'):
            assert db.execute(f'SELECT count(*) FROM {table}').fetchone()[0] == 0
    with pytest.raises(InboxError):
        sessions.info(owner['participant_token'])


def test_message_and_storage_limits(sessions):
    owner, guest = pair(sessions)
    token = owner['participant_token']
    with pytest.raises(InboxError):
        sessions.send(token, '💬' * 4097, 'too-large')
    for number in range(30):
        sessions.send(token, 'hello', str(number))
    with pytest.raises(InboxError) as error:
        sessions.send(token, 'rate limited', '31')
    assert error.value.status == 429
    # The peer has a separate sending allowance; retries do not consume it.
    sessions.send(guest['participant_token'], 'reply', 'reply')
    assert sessions.send(token, 'hello', '0')['duplicate']
    sessions.store.settings = replace(sessions.store.settings, storage_limit=1)
    with pytest.raises(InboxError) as error:
        sessions.send(guest['participant_token'], 'capacity', 'capacity')
    assert error.value.status == 507
    # Cleanup remains possible when storage is full.
    sessions.set_participant(token, guest['participant_id'], approve=False)
    with pytest.raises(InboxError):
        sessions.read(guest['participant_token'])
    sessions.close(token)


def test_session_and_history_caps(sessions, monkeypatch):
    owner, guest = pair(sessions)
    sessions.store.settings = replace(sessions.store.settings, inbox_limit=1)
    with pytest.raises(InboxError):
        sessions.create('Another', 'Full')
    monkeypatch.setattr('openhook.sessions.EVENT_LIMIT', 3)
    with pytest.raises(InboxError):
        sessions.send(owner['participant_token'], 'full history', 'full')


@pytest.mark.asyncio
@pytest.mark.parametrize('timeout', [float('inf'), float('nan'), -1, 31])
async def test_wait_limits(sessions, timeout):
    with pytest.raises(InboxError):
        await sessions.wait('ohp_invalid', timeout_seconds=timeout)


def test_http_and_mcp_agents_exchange_messages(sessions):
    with TestClient(create_app(sessions.store.settings)) as client:
        def http(action, **fields):
            result = client.post('/api/v1/sessions', json={'action': action, **fields})
            assert result.status_code == 200, result.text
            assert result.headers['cache-control'] == 'no-store'
            return result.json()['data']
        def mcp(tool_name, **arguments):
            response = client.post('/mcp', headers={'Accept': 'application/json, text/event-stream'},
                json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': tool_name, 'arguments': arguments}})
            result = response.json()['result']
            assert not result.get('isError'), result
            return json.loads(result['content'][0]['text'])
        owner = mcp('create_agent_session', name='Codex', title='Partner conversation')
        guest = http('join', invite_code=owner['invite_code'], name='HTTP agent')
        mcp('approve_agent_participant', participant_token=owner['participant_token'], participant_id=guest['participant_id'])
        mcp('send_agent_message', participant_token=owner['participant_token'], text='Please review the plan', message_id='one')
        read = http('read', participant_token=guest['participant_token'])
        assert read['events'][-1]['text'] == 'Please review the plan'
        http('send', participant_token=guest['participant_token'], text='Here is my feedback', message_id='two')
        read = mcp('read_agent_messages', participant_token=owner['participant_token'], since=read['next_since'])
        assert read['events'][0]['text'] == 'Here is my feedback'
        assert not read['events'][0]['is_self']
        assert 'untrusted' in read['trust_notice']
        mcp('close_agent_session', participant_token=owner['participant_token'])


def test_web_security_and_discovery(sessions):
    settings = replace(sessions.store.settings, umami_script_url='https://analytics.example.com/script.js',
                       umami_website_id='d9c5e0f4-99f5-469e-9a2c-65f65954cbe8')
    with TestClient(create_app(settings)) as client:
        page = client.get('/sessions')
        assert page.status_code == 200
        assert page.headers['cache-control'] == 'no-store'
        assert page.headers['x-robots-tag'] == 'noindex, nofollow'
        assert 'analytics.example.com' not in page.text
        assert '/sessions' not in client.get('/sitemap.xml').text
        assert 'Disallow: /sessions' in client.get('/robots.txt').text
        schema = client.get('/openapi.json').json()
        assert '/api/v1/sessions' in schema['paths']
        assert '/api/v1/v1/sessions' not in schema['paths']
        invalid = client.post('/api/v1/sessions', json={'action': 'send', 'participant_token': 'ohp_do_not_echo', 'extra': 'secret'})
        assert invalid.status_code == 400 and 'do_not_echo' not in invalid.text and 'secret' not in invalid.text
        cross_origin = client.post('/api/v1/sessions', headers={'Origin': 'https://evil.example'}, json={'action': 'create', 'name': 'X', 'title': 'X'})
        assert cross_origin.status_code == 403
        assert client.get('/api/v1/sessions?participant_token=ohp_test').status_code == 405
