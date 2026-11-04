"""Attachment access, resource boundaries, encryption and actual HTTP transfers."""
from dataclasses import replace
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
from types import SimpleNamespace
import time
from urllib.parse import quote

from cryptography.fernet import Fernet
import pytest
from starlette.testclient import TestClient

from openhook.channel_files import ChannelFiles, FILE_BYTES, UPLOAD_PATH
from openhook.channel_listener import Queue
from openhook.errors import ChannelError
from openhook.sessions import Sessions
from openhook.settings import Settings
from openhook.store import Store
from openhook.web import create_app
from openhook.web import WebBoundary


@pytest.fixture
def channel(tmp_path):
    settings = Settings(database=str(tmp_path/'files.db'), origin='http://testserver')
    store = Store(settings)
    sessions = Sessions(store)
    owner = sessions.create('Owner', 'Files')
    guest = sessions.join(owner['invite_code'], 'Guest')
    return settings, store, sessions, ChannelFiles(store), owner, guest


def upload(client, token, content=b'private report', filename='report.txt', upload_id='one', expiry=86400):
    return client.post(UPLOAD_PATH, content=content, headers={
        'Content-Type': 'application/octet-stream', 'Authorization': 'Bearer '+token,
        'X-Openhook-Filename': quote(filename, safe=''), 'X-Openhook-Upload-Id': upload_id,
        'X-Openhook-Expiry': str(expiry)})


def test_private_roundtrip_notification_and_idempotency(channel, tmp_path):
    _, store, sessions, files, owner, guest = channel
    token = owner['participant_token']
    first = files.upload(token, 'brief.md', b'# private brief', 'retry')
    assert first['size'] == 15 and first['untrusted']
    assert files.upload(token, 'brief.md', b'# private brief', 'retry')['duplicate']
    assert files.download(guest['participant_token'], first['file_id'])[1] == b'# private brief'
    assert len(files.info(token)['files']) == 1
    batch = sessions.read(guest['participant_token'])
    assert first['file_id'] in batch['events'][-1]['text']
    assert '# private brief' not in json.dumps(batch)
    queue = Queue(tmp_path/'queue.db')
    queue.accept(batch, owner['session_id'])
    assert first['file_id'] in queue.first()[1]['text']
    queue.close()
    for name, content, expiry in [('brief.md', b'changed', 86400), ('other.md', b'# private brief', 86400), ('brief.md', b'# private brief', 60)]:
        with pytest.raises(ChannelError) as exc: files.upload(token, name, content, 'retry', expiry)
        assert exc.value.status == 409
    with store.connection() as db:
        assert db.execute("SELECT count(*) FROM session_events WHERE kind='message'").fetchone()[0] == 1


def test_channel_isolation_readonly_revocation_rotation_and_delete(channel):
    _, store, sessions, files, owner, guest = channel
    token = owner['participant_token']
    identifier = files.upload(guest['participant_token'], 'report.txt', b'private', 'first')['file_id']
    outsider = sessions.create('Other', 'Unrelated')
    for operation in (files.info, files.download, files.delete):
        with pytest.raises(ChannelError) as exc: operation(outsider['participant_token'], identifier)
        assert exc.value.status == 404
    with pytest.raises(ChannelError): files.download(owner['session_id'], identifier)
    reader = sessions.join(sessions.invite(token, 'read')['invite_code'], 'Reader')
    assert files.download(reader['participant_token'], identifier)[1] == b'private'
    with pytest.raises(ChannelError) as exc: files.upload(reader['participant_token'], 'no.txt', b'no', 'no')
    assert exc.value.status == 403
    with pytest.raises(ChannelError) as exc: files.delete(reader['participant_token'], identifier)
    assert exc.value.status == 403
    rotated = sessions.rotate(guest['participant_token'])['participant_token']
    with pytest.raises(ChannelError): files.download(guest['participant_token'], identifier)
    assert files.download(rotated, identifier)[1] == b'private'
    sessions.revoke(token, guest['participant_id'])
    with pytest.raises(ChannelError): files.download(rotated, identifier)
    sessions.archive(token)
    with pytest.raises(ChannelError): files.upload(token, 'no.txt', b'no', 'blocked')
    assert files.download(token, identifier)[1] == b'private'
    assert files.delete(token, identifier)['deleted']
    with pytest.raises(ChannelError): files.download(token, identifier)
    sessions.archive(token, False)
    files.upload(token, 'new.txt', b'delete with channel', 'new')
    sessions.close(token)
    with store.connection() as db:
        assert db.execute('SELECT count(*) FROM channel_files').fetchone()[0] == 0


def test_expiry_blocks_immediately_and_cleanup_removes_payload(channel, monkeypatch):
    _, store, sessions, files, owner, guest = channel
    token = owner['participant_token']
    now = time.time()
    file = files.upload(token, 'short.txt', b'expire me', 'short', 60)
    monkeypatch.setattr('time.time', lambda: now+62)
    assert files.info(token)['files'] == []
    with pytest.raises(ChannelError) as exc: files.download(guest['participant_token'], file['file_id'])
    assert exc.value.status == 404
    with pytest.raises(ChannelError): files.upload(token, 'short.txt', b'expire me', 'short', 60)
    store.cleanup()
    with store.connection() as db:
        assert db.execute('SELECT count(*) FROM channel_files').fetchone()[0] == 0
    with pytest.raises(ChannelError): files.upload(token, 'short.txt', b'expire me', 'short', 60)
    # Files cannot outlive even a short channel.
    short = sessions.create('Owner', 'short', 60)
    files.upload(short['participant_token'], 'brief.txt', b'short channel', 'end')
    with store.connection() as db:
        row = db.execute('SELECT f.expires,c.expires AS channel_expires FROM channel_files f JOIN agent_sessions c ON c.id=f.session').fetchone()
        assert row['expires'] == row['channel_expires']


@pytest.mark.parametrize('filename,content', [('../note.txt', b'no'), ('x\\note.txt', b'no'),
    ('bad\r\n.txt', b'no'), ('hidden\u202e.txt', b'no'), ('script.html', b'<html>'),
    ('app.svg', b'<svg>'), ('fake.png', b'not png'), ('empty.txt', b''), ('binary.txt', b'\xff')])
def test_reject_unsafe_names_types_and_empty_files(channel, filename, content):
    *_, files, owner, guest = channel
    with pytest.raises(ChannelError): files.upload(owner['participant_token'], filename, content, 'invalid')


def test_resource_caps_are_transactional(channel, monkeypatch):
    _, store, sessions, files, owner, _ = channel
    token = owner['participant_token']
    monkeypatch.setattr('openhook.channel_files.CHANNEL_FILES', 1)
    first = files.upload(token, 'one.txt', b'one', 'one')
    with pytest.raises(ChannelError) as exc: files.upload(token, 'two.txt', b'two', 'two')
    assert exc.value.status == 429
    files.delete(token, first['file_id'])
    monkeypatch.setattr('openhook.channel_files.CHANNEL_FILE_BYTES', 2)
    with pytest.raises(ChannelError): files.upload(token, 'two.txt', b'too big', 'two')
    monkeypatch.setattr('openhook.channel_files.CHANNEL_FILE_BYTES', FILE_BYTES)
    monkeypatch.setattr('openhook.sessions.EVENT_LIMIT', 0)
    with pytest.raises(ChannelError): files.upload(token, 'two.txt', b'two', 'two')
    assert files.info(token)['files'] == []


def test_encryption_migration_rotation_and_tampering(channel, tmp_path):
    settings, store, _, files, owner, _ = channel
    token = owner['participant_token']
    file = files.upload(token, 'secret.txt', b'ATTACHMENT-PRIVATE-CONTENT', 'secret')
    key = tmp_path/'key.json'
    first = Fernet.generate_key().decode()
    key.write_text(json.dumps([first])); key.chmod(0o600)
    protected = replace(settings, storage_key_file=str(key))
    encrypted = ChannelFiles(Store(protected))
    assert encrypted.download(token, file['file_id'])[1] == b'ATTACHMENT-PRIVATE-CONTENT'
    with encrypted.store.connection() as db:
        row = db.execute('SELECT * FROM channel_files').fetchone()
        assert row['encrypted'] and b'ATTACHMENT-PRIVATE-CONTENT' not in row['content']
    second = Fernet.generate_key().decode()
    key.write_text(json.dumps([second, first])); ChannelFiles(Store(protected))
    key.write_text(json.dumps([second])); final = ChannelFiles(Store(protected))
    assert final.download(token, file['file_id'])[1] == b'ATTACHMENT-PRIVATE-CONTENT'
    with pytest.raises(ValueError): Store(settings)
    with final.store.connection(write=True) as db:
        db.execute("UPDATE channel_files SET filename='forged.txt'")
    with pytest.raises(ValueError, match='authentication failed'): final.download(token, file['file_id'])
    with pytest.raises(ValueError, match='authentication failed'): Store(protected)


def test_http_private_binary_transfer_and_boundary(channel):
    settings, _, _, _, owner, guest = channel
    token = owner['participant_token']
    with TestClient(create_app(settings)) as client:
        # File upload has a narrow 10-MiB exception; JSON and MCP limits stay unchanged.
        data = b'x' * (1024*1024+1)
        response = upload(client, token, data, filename='r\u00e9sum\u00e9.txt')
        assert response.status_code == 201, response.text
        result = response.json()['data']
        path = result['download_path']
        assert client.get(path).status_code == 405
        assert client.post(path, json={'participant_token': 'ohp_invalid'}).status_code == 401
        downloaded = client.post(path, json={'participant_token': guest['participant_token']})
        assert downloaded.content == data
        assert downloaded.headers['content-type'] == 'application/octet-stream'
        assert downloaded.headers['content-disposition'].startswith("attachment; filename*=UTF-8''r%C3%A9")
        for response in (response, downloaded):
            assert response.headers['cache-control'] == 'no-store'
            assert response.headers['x-content-type-options'] == 'nosniff'
            assert response.headers['referrer-policy'] == 'no-referrer'
        assert 'sandbox' in downloaded.headers['content-security-policy']
        assert upload(client, token, data, filename='r\u00e9sum\u00e9.txt').json()['data']['duplicate']
        assert upload(client, token, b'x'*(FILE_BYTES+1), upload_id='oversize').status_code == 413
        assert client.post('/api/v1/channels', content=data, headers={'Content-Type':'application/json'}).status_code == 413
        assert upload(client, '', upload_id='unauth').status_code == 401
        assert client.post(UPLOAD_PATH, content=b'no', headers={'Origin':'https://evil.test'}).status_code == 403
        assert client.post(path, content='{"participant_token":"a","participant_token":"b"}', headers={'Content-Type':'application/json'}).status_code == 400
        response = client.post('/api/v1/channels', json={'action':'files','participant_token':token})
        assert response.json()['data']['files'][0]['file_id'] == result['file_id']
        response = client.post('/api/v1/channels', json={'action':'delete_file','participant_token':token,'file_id':result['file_id']})
        assert response.json()['data']['deleted']
        assert client.post(path, json={'participant_token':token}).status_code == 404


def test_http_reauthorizes_after_upload_and_rejects_before_reading_unauthorized_body(channel):
    settings, _, sessions, files, owner, guest = channel
    consumed = []
    def content():
        consumed.append(True)
        yield b'private bytes'
    headers = {'Content-Type':'application/octet-stream','X-Openhook-Filename':'report.txt',
               'X-Openhook-Upload-Id':'revoked'}
    with TestClient(create_app(settings)) as client:
        assert client.post(UPLOAD_PATH, content=content(), headers=headers).status_code == 401
        assert not consumed
        def revoke_during_upload():
            yield b'first part'
            sessions.revoke(owner['participant_token'], guest['participant_id'])
            yield b'second part'
        response = client.post(UPLOAD_PATH, content=revoke_during_upload(), headers={
            **headers, 'Authorization':'Bearer '+guest['participant_token']})
        assert response.status_code == 401
        assert files.info(owner['participant_token'])['files'] == []


def test_mcp_transfer_contract_keeps_bytes_and_keys_out_of_results(channel):
    settings, _, _, files, owner, _ = channel
    token = owner['participant_token']
    file = files.upload(token, 'secret.txt', b'BODY-MUST-NOT-ENTER-MODEL-CONTEXT', 'mcp')
    with TestClient(create_app(settings)) as client:
        def tool(name, **arguments):
            response = client.post('/mcp', headers={'Accept':'application/json, text/event-stream'}, json={
                'jsonrpc':'2.0', 'id':1, 'method':'tools/call', 'params':{
                    'name':name, 'arguments':{'participant_token':token, **arguments}}})
            return response.json()['result']
        for result in (tool('prepare_agent_file_upload'), tool('get_agent_file', file_id=file['file_id'])):
            assert not result.get('isError')
            serialized = json.dumps(result)
            assert token not in serialized and 'BODY-MUST-NOT-ENTER-MODEL-CONTEXT' not in serialized
        assert not tool('delete_agent_file', file_id=file['file_id']).get('isError')


def test_cli_moves_bytes_privately_without_overwrites_or_symlink_reads(channel, tmp_path, monkeypatch, capsys):
    from openhook import channel_file_cli
    settings, _, _, _, owner, _ = channel
    key = tmp_path/'member.key'; key.write_text(owner['participant_token']); key.chmod(0o600)
    source = tmp_path/'local.txt'; source.write_bytes(b'CLI private bytes')
    target = tmp_path/'received.txt'
    configuration = replace(settings, origin='http://127.0.0.1')
    with TestClient(create_app(configuration), base_url=configuration.origin) as client:
        class LocalHTTP:
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def post(self, *args, **kwargs): return client.post(*args, **kwargs)
            def stream(self, *args, **kwargs): return client.stream(*args, **kwargs)
        monkeypatch.setattr(channel_file_cli.httpx, 'Client', lambda **_: LocalHTTP())
        args = SimpleNamespace(url=configuration.origin, token_file=str(key), action='upload',
                               path=str(source), upload_id='cli-retry', expiry=86400)
        result = channel_file_cli.transfer(args)
        assert channel_file_cli.transfer(args)['duplicate']
        args.action = 'download'; args.file_id = result['file_id']; args.output = str(target)
        assert channel_file_cli.transfer(args)['size'] == len(source.read_bytes())
        assert target.read_bytes() == source.read_bytes()
        assert target.stat().st_mode & 0o777 == 0o600
        with pytest.raises(FileExistsError): channel_file_cli.transfer(args)
        assert target.read_bytes() == source.read_bytes()
        link = tmp_path/'alias.txt'; link.symlink_to(source)
        with pytest.raises(OSError): channel_file_cli.read_source(link)
        assert owner['participant_token'] not in capsys.readouterr().out


def test_simultaneous_retries_share_one_file_and_one_notice(channel):
    _, store, _, files, owner, _ = channel
    def send(_): return files.upload(owner['participant_token'], 'retry.txt', b'one copy', 'concurrent')
    with ThreadPoolExecutor(max_workers=2) as pool:
        receipts = list(pool.map(send, range(2)))
    assert receipts[0]['file_id'] == receipts[1]['file_id']
    assert sorted(r['duplicate'] for r in receipts) == [False, True]
    with store.connection() as db:
        assert db.execute('SELECT count(*) FROM channel_files').fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM session_events WHERE kind='message'").fetchone()[0] == 1


@pytest.mark.asyncio
async def test_binary_transfer_concurrency_is_bounded_and_released(channel):
    settings = channel[0]
    release, entered = asyncio.Event(), asyncio.Queue()
    messages = []
    async def downstream(scope, receive, send):
        await entered.put(True)
        await release.wait()
    boundary = WebBoundary(downstream, settings)
    scope = {'type':'http','path':UPLOAD_PATH,'method':'POST','query_string':b'',
             'headers':[(b'host',b'testserver')], 'client':('127.0.0.1',1000)}
    async def receive(): return {'type':'http.request','body':b''}
    async def send(message): messages.append(message)
    active = [asyncio.create_task(boundary(scope, receive, send)) for _ in range(4)]
    try:
        for _ in active: await asyncio.wait_for(entered.get(), 1)
        await boundary(scope, receive, send)
        assert messages[0]['status'] == 429
    finally:
        release.set()
        await asyncio.gather(*active)
    assert boundary.transfers == boundary.active == 0 and not boundary.inflight
