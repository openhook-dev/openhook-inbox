"""Adversarial regression checks for transport, storage and resource boundaries."""
import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path

from cryptography.fernet import Fernet
import pytest
from starlette.testclient import TestClient

from openhook.sessions import Sessions
from openhook.settings import Settings
from openhook.store import Store
from openhook.storage_cipher import StorageCipher
from openhook.web import WebBoundary, create_app


def key_file(tmp_path, keys=None, name='keys.json'):
    path = tmp_path / name
    path.write_text(json.dumps(keys or [Fernet.generate_key().decode()]))
    path.chmod(0o600)
    return path


def settings(tmp_path, key=None):
    return Settings(database=str(tmp_path/'db.sqlite3'), origin='https://openhook.test',
                    storage_key_file=str(key) if key else '')


def test_encrypted_round_trip_retries_restart_and_no_plaintext_rows(tmp_path):
    config=settings(tmp_path,key_file(tmp_path)); sessions=Sessions(Store(config))
    owner=sessions.create('Owner','Encrypted channel')
    guest=sessions.join(owner['invite_code'],'Guest')
    text='PRIVATE-MESSAGE-SECRET-4721 💬'
    sent=sessions.send(owner['participant_token'],text,'idempotent')
    assert sessions.send(owner['participant_token'],text,'idempotent')['duplicate']
    reopened=Sessions(Store(config))
    assert reopened.read(guest['participant_token'])['events'][-1]['text']==text
    with reopened.store.connection() as db:
        rows=db.execute('SELECT body,body_encrypted FROM session_events').fetchall()
        assert rows and all(r['body_encrypted'] and text not in r['body'] for r in rows)
    assert text.encode() not in Path(config.database).read_bytes()
    with pytest.raises(ValueError,match='requires OPENHOOK_STORAGE_KEY_FILE'):
        Store(replace(config,storage_key_file=''))
    # Even an empty protected database must never silently downgrade.
    reopened.close(owner['participant_token'])
    with pytest.raises(ValueError,match='requires OPENHOOK_STORAGE_KEY_FILE'):
        Store(replace(config,storage_key_file=''))


def test_migration_preserves_keys_history_and_rotation(tmp_path):
    config=settings(tmp_path); old=Sessions(Store(config))
    owner=old.create('Owner','Keep channel')
    old.send(owner['participant_token'],'existing retained history','old')
    first=key_file(tmp_path); first_keys=json.loads(first.read_text())
    protected=replace(config,storage_key_file=str(first))
    migrated=Sessions(Store(protected))
    assert migrated.read(owner['participant_token'])['events'][-1]['text']=='existing retained history'
    replacement=Fernet.generate_key().decode()
    first.write_text(json.dumps([replacement,*first_keys]))
    rotated=Sessions(Store(protected))
    first.write_text(json.dumps([replacement]))
    final=Sessions(Store(protected))
    assert final.read(owner['participant_token'])==rotated.read(owner['participant_token'])
    wrong=key_file(tmp_path,name='wrong.json')
    with pytest.raises(ValueError,match='authentication failed'):
        Store(replace(protected,storage_key_file=str(wrong)))
    # Old app instances without a key cannot add plaintext to protected storage.
    with pytest.raises(ValueError,match='requires OPENHOOK_STORAGE_KEY_FILE'):
        old.send(owner['participant_token'],'plaintext downgrade','downgrade')


@pytest.mark.parametrize('change',['tamper','swap_context','plaintext_downgrade'])
def test_stored_content_cannot_be_tampered_or_moved_between_events(tmp_path,change):
    config=settings(tmp_path,key_file(tmp_path)); sessions=Sessions(Store(config))
    owner=sessions.create('Owner','Integrity')
    first=sessions.send(owner['participant_token'],'first','one')['sequence']
    second=sessions.send(owner['participant_token'],'second','two')['sequence']
    with sessions.store.connection(write=True) as db:
        if change=='tamper':db.execute("UPDATE session_events SET body='corrupted' WHERE sequence=?",(first,))
        elif change=='plaintext_downgrade':db.execute("UPDATE session_events SET body='forged',body_encrypted=0 WHERE sequence=?",(first,))
        else:
            body=db.execute('SELECT body FROM session_events WHERE sequence=?',(first,)).fetchone()[0]
            db.execute('UPDATE session_events SET body=? WHERE sequence=?',(body,second))
    with pytest.raises(ValueError):sessions.read(owner['participant_token'])
    with pytest.raises(ValueError):Store(config)


def test_private_key_file_required_and_database_permissions_repaired(tmp_path):
    path=key_file(tmp_path); path.chmod(0o644)
    with pytest.raises(ValueError,match='private regular file'):StorageCipher(path)
    path.chmod(0o600)
    link=tmp_path/'link';link.symlink_to(path)
    with pytest.raises(OSError):StorageCipher(link)
    config=settings(tmp_path);Store(config);Path(config.database).chmod(0o666)
    store=Store(config)
    assert Path(config.database).stat().st_mode & 0o077==0
    with store.connection() as db:assert db.execute('PRAGMA secure_delete').fetchone()[0]==1
    target=tmp_path/'foreign';target.write_text('do not alter');target.chmod(0o644)
    alias=tmp_path/'alias';alias.symlink_to(target)
    with pytest.raises(OSError):Store(replace(config,database=str(alias)))
    assert target.read_text()=='do not alter' and target.stat().st_mode & 0o777==0o644


@pytest.mark.parametrize('case', ['ok','invalid_origin','invalid_host','cross_site','too_large','redirect','not_found','metrics'])
def test_security_headers_cover_errors_redirects_and_private_responses(tmp_path,case):
    config=settings(tmp_path)
    with TestClient(create_app(config),base_url=config.origin) as client:
        if case=='ok':r=client.get('/health')
        elif case=='invalid_origin':r=client.post('/api/v1/channels',headers={'Origin':'https://evil.test'})
        elif case=='invalid_host':r=client.post('/api/v1/channels',headers={'Host':'localhost:8788'})
        elif case=='cross_site':r=client.post('/api/v1/channels',headers={'Sec-Fetch-Site':'cross-site'})
        elif case=='too_large':r=client.post('/api/v1/channels',content=b'x'*(config.body_limit+1))
        elif case=='redirect':r=client.get('/',headers={'Host':'www.openhook.test'},follow_redirects=False)
        elif case=='metrics':r=client.get('/metrics')
        else:r=client.get('/not-found')
        assert r.headers['strict-transport-security']=='max-age=31536000'
        assert r.headers['x-frame-options']=='DENY'
        assert r.headers['referrer-policy']=='no-referrer'
        assert r.headers['x-content-type-options']=='nosniff'
        assert "frame-ancestors 'none'" in r.headers['content-security-policy']
        if case in {'invalid_origin','invalid_host','cross_site','too_large','metrics'}:
            assert r.status_code in {401,403,404,413}
            assert r.headers['cache-control']=='no-store'


def test_http_development_does_not_install_hsts(tmp_path):
    with TestClient(create_app(replace(settings(tmp_path),origin='http://testserver'))) as client:
        assert 'strict-transport-security' not in client.get('/health').headers


@pytest.mark.asyncio
async def test_inflight_limit_recovers_after_request_cancellation():
    entered=asyncio.Event();release=asyncio.Event();messages=[]
    async def downstream(scope,receive,send):
        entered.set();await release.wait()
    async def receive():return {'type':'http.request','body':b''}
    async def send(message):messages.append(message)
    app=WebBoundary(downstream,Settings(origin='https://openhook.test'))
    scope={'type':'http','path':'/api/v1/channels','method':'POST','headers':[(b'host',b'openhook.test')],'client':('203.0.113.1',1)}
    tasks=[asyncio.create_task(app(scope,receive,send)) for _ in range(16)]
    await entered.wait();await asyncio.sleep(0)
    await app(scope,receive,send)
    assert any(m.get('status')==429 for m in messages)
    assert app.active==16
    for task in tasks:task.cancel()
    await asyncio.gather(*tasks,return_exceptions=True)
    assert app.active==0 and not app.inflight


def test_key_generation_never_overwrites_or_prints_secrets(tmp_path,capsys):
    from scripts.storage_key import generate
    path=tmp_path/'private'/'storage-key.json'
    generate(path)
    original=path.read_bytes()
    assert path.stat().st_mode & 0o077==0
    assert len(json.loads(original))==1
    assert capsys.readouterr().out==''
    StorageCipher(path)
    with pytest.raises(FileExistsError):generate(path)
    assert path.read_bytes()==original
    pipe=tmp_path/'pipe';os.mkfifo(pipe,0o600)
    with pytest.raises(ValueError,match='private regular file'):StorageCipher(pipe)


def test_encrypted_http_and_mcp_share_transport_and_revocation_rules(tmp_path):
    config=settings(tmp_path,key_file(tmp_path))
    with TestClient(create_app(config),base_url=config.origin) as client:
        def http(action,**fields):
            response=client.post('/api/v1/channels',json={'action':action,**fields})
            assert response.status_code==200,response.text
            return response.json()['data']
        owner=http('create',name='Owner',title='Encrypted transport QA')
        guest=http('join',invite_code=owner['invite_url'],name='Guest')
        http('send',participant_token=guest['participant_token'],text='encrypted transport content',message_id='one')
        result=client.post('/mcp',headers={'Accept':'application/json, text/event-stream'},json={
            'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'read_agent_messages','arguments':{'participant_token':owner['participant_token']}}}).json()['result']
        assert not result.get('isError')
        assert json.loads(result['content'][0]['text'])['events'][-1]['text']=='encrypted transport content'
        http('revoke',participant_token=owner['participant_token'],participant_id=guest['participant_id'])
        assert client.post('/api/v1/channels',json={'action':'read','participant_token':guest['participant_token']}).status_code==401
