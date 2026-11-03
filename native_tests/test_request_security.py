"""Regression checks for hostile input and privacy after local acknowledgement."""
import asyncio
from dataclasses import replace
import json
import os

import pytest
from starlette.exceptions import HTTPException
from starlette.testclient import TestClient

from openhook import channel_listener, web
from openhook.settings import Settings
from openhook.web import WebBoundary, create_app


@pytest.fixture
def config(tmp_path):
    return Settings(database=str(tmp_path/'security.db'),origin='https://openhook.test')


@pytest.mark.parametrize('content_type',[None,'text/plain','application/x-www-form-urlencoded'])
def test_channel_api_requires_json_content_type(config,content_type):
    with TestClient(create_app(config),base_url=config.origin) as client:
        headers={'Content-Type':content_type} if content_type else {}
        r=client.post('/api/v1/channels',content='{"action":"create","name":"A","title":"B"}',headers=headers)
        assert r.status_code==415
        with client.app.state.store.connection() as db:
            assert db.execute('SELECT count(*) FROM agent_sessions').fetchone()[0]==0


@pytest.mark.parametrize('payload',[
    b'{"action":"create","action":"create","name":"A","title":"B"}',
    '{"action":"create","name":"A","title":"B"}'.encode('utf-16'),
    b'{"action":"info","timeout_seconds":NaN}',
    b'{"action":"info","timeout_seconds":Infinity}',
    b'{"action":"info","timeout_seconds":-Infinity}',
    b'['*2000+b'0'+b']'*2000,
])
def test_ambiguous_or_nonstandard_json_is_rejected_without_writes(config,payload):
    with TestClient(create_app(config),base_url=config.origin,raise_server_exceptions=False) as client:
        r=client.post('/api/v1/channels',content=payload,headers={'Content-Type':'application/json'})
        assert r.status_code==400
        with client.app.state.store.connection() as db:
            assert db.execute('SELECT count(*) FROM agent_sessions').fetchone()[0]==0


def test_unexpected_server_errors_keep_security_headers_and_hide_details(config,monkeypatch):
    async def fail(request):raise RuntimeError('PRIVATE_INTERNAL_DETAIL')
    monkeypatch.setattr(web,'tools_catalog',fail)
    with TestClient(create_app(config),base_url=config.origin,raise_server_exceptions=False) as client:
        r=client.get('/api/v1/tools')
        assert r.status_code==500 and 'PRIVATE_INTERNAL_DETAIL' not in r.text
        assert r.headers['cache-control']=='no-store'
        assert r.headers.get('strict-transport-security')=='max-age=31536000'
        assert r.headers.get('x-frame-options')=='DENY'
        assert r.headers.get('content-security-policy')


def scope(headers=()):
    return {'type':'http','path':'/api/v1/channels','method':'POST',
            'headers':[(b'host',b'openhook.test'),*headers],'client':('203.0.113.1',1000),'query_string':b''}


@pytest.mark.asyncio
@pytest.mark.parametrize('headers,expected',[
    ([(b'content-length',b'9'*5000)],413),
    ([(b'content-length',b'-1')],400),
    ([(b'content-length',b'no')],400),
    ([(b'content-length',b'')],400),
    ([(b'content-length',b'2'),(b'content-length',b'2')],400),
    ([(b'origin',b'https://openhook.test'),(b'origin',b'https://openhook.test')],400),
    ([(b'host',b'openhook.test')],400),
    ([(b'content-length',b'2'),(b'transfer-encoding',b'chunked')],400),
])
async def test_ambiguous_headers_and_huge_lengths_fail_without_dispatch(config,headers,expected):
    called=False;messages=[]
    async def downstream(scope,receive,send):
        nonlocal called
        called=True
    async def receive():return {'type':'http.request','body':b'{}'}
    async def send(message):messages.append(message)
    await WebBoundary(downstream,config)(scope(headers),receive,send)
    assert not called
    assert next(m['status'] for m in messages if m['type']=='http.response.start')==expected


@pytest.mark.asyncio
async def test_slow_body_times_out_and_releases_slot(config):
    config=replace(config,body_timeout=.01)
    async def downstream(scope,receive,send):await receive()
    async def receive():await asyncio.sleep(1)
    async def send(message):pass
    app=WebBoundary(downstream,config)
    with pytest.raises(HTTPException) as error:await app(scope(),receive,send)
    assert error.value.status_code==408
    assert app.active==0 and not app.inflight


@pytest.mark.asyncio
async def test_completed_body_does_not_time_out_long_poll_or_disconnect_wait(config):
    config=replace(config,body_timeout=.01);calls=0
    async def downstream(scope,receive,send):
        assert (await receive())['body']==b'{}'
        await asyncio.sleep(.03)
        assert (await receive())['type']=='http.disconnect'
    async def receive():
        nonlocal calls
        calls+=1
        return {'type':'http.request','body':b'{}','more_body':False} if calls==1 else {'type':'http.disconnect'}
    async def send(message):pass
    app=WebBoundary(downstream,config)
    await app(scope(),receive,send)
    assert app.active==0


def test_acknowledged_payload_is_overwritten_in_queue_database(tmp_path,monkeypatch):
    original=channel_listener.sqlite3.connect
    def insecure_default(*args,**kwargs):
        db=original(*args,**kwargs);db.execute('PRAGMA secure_delete=OFF');return db
    monkeypatch.setattr(channel_listener.sqlite3,'connect',insecure_default)
    path=tmp_path/'queue.db';q=channel_listener.Queue(path)
    marker='PRIVATE-QUEUED-MESSAGE-'+'Q'*200
    q.accept({'events':[{'sequence':1,'kind':'message','is_self':False,'text':marker,
        'sender_id':'peer','sender_name':'Peer','created_at':'now'}],'next_since':1},'channel')
    q.ack_through(1);q.close()
    assert marker.encode() not in path.read_bytes()


@pytest.mark.parametrize('kind',['symlink','fifo'])
def test_unsafe_queue_files_rejected_before_sqlite_opens_them(tmp_path,monkeypatch,kind):
    path=tmp_path/'queue.db'
    if kind=='symlink':
        target=tmp_path/'target';target.write_text('do not touch');path.symlink_to(target)
    else:os.mkfifo(path,0o600)
    monkeypatch.setattr(channel_listener.sqlite3,'connect',lambda *a,**k:pytest.fail('Unsafe queue path reached SQLite'))
    with pytest.raises((OSError,ValueError)):channel_listener.Queue(path)


@pytest.mark.parametrize('timeout',[0,-1,float('nan'),float('inf'),61])
def test_invalid_body_deadline_rejected_at_startup(config,timeout):
    with pytest.raises(ValueError,match='Body timeout'):replace(config,body_timeout=timeout)


@pytest.mark.asyncio
async def test_dripping_chunks_cannot_reset_the_body_deadline(config):
    config=replace(config,body_timeout=.02)
    async def downstream(scope,receive,send):
        while True:await receive()
    async def receive():
        await asyncio.sleep(.005)
        return {'type':'http.request','body':b' ','more_body':True}
    async def send(message):pass
    app=WebBoundary(downstream,config)
    with pytest.raises(HTTPException) as error:await app(scope(),receive,send)
    assert error.value.status_code==408 and app.active==0


def test_legacy_queue_compaction_preserves_pending_and_scrubs_old_free_pages(tmp_path):
    path=tmp_path/'legacy.db'
    # Construct a real pre-hardening queue with insecure deletion.
    with channel_listener.sqlite3.connect(path) as db:
        db.execute('PRAGMA secure_delete=OFF')
        db.execute('CREATE TABLE pending(sequence INTEGER PRIMARY KEY,payload TEXT NOT NULL)')
        old='PREVIOUSLY-ACKNOWLEDGED-PRIVATE-'+'Z'*256
        pending=json.dumps({'text':'keep this pending work','sequence':2})
        db.executemany('INSERT INTO pending VALUES(?,?)',[(1,old),(2,pending)])
        db.execute('DELETE FROM pending WHERE sequence=1')
    assert old.encode() in path.read_bytes()
    q=channel_listener.Queue(path)
    assert q.first()[1]['text']=='keep this pending work'
    assert q.db.execute('PRAGMA secure_delete').fetchone()[0]==1
    assert q.db.execute('PRAGMA user_version').fetchone()[0]==1
    q.close()
    assert old.encode() not in path.read_bytes()


@pytest.mark.asyncio
async def test_upload_timeout_is_a_protected_http_response(config):
    import httpx
    config=replace(config,body_timeout=.02)
    app=create_app(config)
    async def slow_body():
        yield b'{'
        await asyncio.sleep(.1)
        yield b'}'
    with TestClient(app,base_url=config.origin):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url=config.origin) as client:
            response=await client.post('/api/v1/channels',content=slow_body(),headers={'Content-Type':'application/json'})
            assert response.status_code==408
            assert response.headers['cache-control']=='no-store'
            assert response.headers['strict-transport-security']=='max-age=31536000'


@pytest.mark.asyncio
async def test_real_channel_long_poll_survives_short_upload_deadline(config):
    import httpx
    from openhook.sessions import Sessions
    config=replace(config,body_timeout=.02)
    app=create_app(config)
    with TestClient(app,base_url=config.origin):
        sessions=Sessions(app.state.store)
        owner=sessions.create('Owner','Long poll')
        cursor=sessions.read(owner['participant_token'])['next_since']
        async def late_message():
            await asyncio.sleep(.05)
            sessions.send(owner['participant_token'],'arrived after upload deadline','late')
        task=asyncio.create_task(late_message())
        try:
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url=config.origin) as client:
                response=await client.post('/api/v1/channels',json={'action':'read','participant_token':owner['participant_token'],'since':cursor,'timeout_seconds':.2})
            assert response.status_code==200
            assert response.json()['data']['events'][-1]['text']=='arrived after upload deadline'
        finally:await task
