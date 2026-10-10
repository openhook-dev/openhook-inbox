"""Hosted identity must not weaken the anonymous/self-hosted capture service."""

import base64
import hashlib
import json
import time
from dataclasses import replace
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest
import respx
from starlette.testclient import TestClient

from openhook.accounts import Accounts
from openhook.hosted_web import cookie_name
from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.web import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(database=str(tmp_path / 'accounts.sqlite3'), origin='https://hosted.test',
                    hosted_enabled=True, github_client_id='dedicated-client', github_client_secret='private-client-secret')


def login(client, user_id=42, name='developer'):
    with respx.mock:
        def exchange(request):
            body = parse_qs(request.content.decode())
            digest = base64.urlsafe_b64encode(hashlib.sha256(body['code_verifier'][0].encode()).digest()).rstrip(b'=').decode()
            assert digest == params['code_challenge'][0]
            assert body['redirect_uri'] == ['https://hosted.test/auth/github/callback']
            return httpx.Response(200, json={'access_token':'transient-github-secret'})
        respx.post('https://github.com/login/oauth/access_token').mock(side_effect=exchange)
        respx.get('https://api.github.com/user').respond(200,json={'id':user_id,'login':name})
        start=client.get('/auth/github',follow_redirects=False)
        assert start.status_code == 303
        params=parse_qs(urlsplit(start.headers['location']).query)
        assert params['scope']==['read:user']
        assert params['code_challenge_method']==['S256']
        callback=client.get('/auth/github/callback',params={'state':params['state'][0],'code':'one-time-code'},follow_redirects=False)
        assert callback.status_code==303,callback.text
        assert callback.headers['location']=='/account'
        assert 'HttpOnly' in callback.headers['set-cookie'] and 'Secure' in callback.headers['set-cookie']
        assert callback.headers['cache-control']=='no-store'
        return params['state'][0]


def test_oauth_identity_keys_and_logout(settings):
    with TestClient(create_app(settings),base_url=settings.origin) as client:
        state=login(client)
        status=client.get('/api/account')
        assert status.headers['cache-control']=='no-store'
        assert status.headers['x-robots-tag']=='noindex, nofollow'
        account=status.json()['data']['account']
        assert account['github_id']==42
        service=Accounts(Store(settings))
        # An intercepted or replayed callback cannot mint another session.
        assert client.get('/auth/github/callback',params={'state':state,'code':'replay'}).status_code==400
        headers={'Origin':settings.origin}
        key=client.post('/api/account/keys',headers=headers,json={'name':'Laptop'}).json()['data']
        assert key['key'].startswith('oha_')
        assert service.authenticate_key(key['key'])['id']==account['id']
        assert key['key'] not in client.get('/api/account').text
        with service.store.connection() as db:
            for table in ('accounts','account_sessions','account_keys','oauth_states'):
                stored=json.dumps([dict(row) for row in db.execute('SELECT * FROM '+table)])
                for secret in (key['key'],'transient-github-secret','private-client-secret','one-time-code'):
                    assert secret not in stored
        assert client.post('/api/account/keys/'+key['id']+'/revoke',headers=headers).status_code==200
        with pytest.raises(InboxError): service.authenticate_key(key['key'])
        assert client.post('/api/account/sign-out',headers=headers).status_code==200
        assert client.get('/api/account').json()['data']['account'] is None
        assert client.post('/api/account/keys',headers=headers,json={'name':'after logout'}).status_code==401


def test_account_isolation_csrf_and_stable_github_id(settings):
    with TestClient(create_app(settings),base_url=settings.origin) as first:
        login(first)
        account=first.get('/api/account').json()['data']['account']
        headers={'Origin':settings.origin}
        key=first.post('/api/account/keys',headers=headers,json={'name':'My agent'}).json()['data']
        for origin in (None,'https://attacker.test'):
            assert first.post('/api/account/keys',headers={'Origin':origin} if origin else {},json={'name':'csrf'}).status_code==403
            assert first.post('/api/account/sign-out',headers={'Origin':origin} if origin else {}).status_code==403
        with TestClient(create_app(settings),base_url=settings.origin) as second:
            login(second,user_id=43,name='another-developer')
            assert second.get('/api/account').json()['data']['keys']==[]
            assert second.post('/api/account/keys/'+key['id']+'/revoke',headers=headers).status_code==404
        login(first,name='renamed-developer')
        assert first.get('/api/account').json()['data']['account']['id']==account['id']
        assert first.get('/api/account').json()['data']['account']['login']=='renamed-developer'
        # The agent capability never grants browser account-management access.
        with TestClient(create_app(settings),base_url=settings.origin) as agent:
            assert agent.post('/api/account/keys',headers={**headers,'Authorization':'Bearer '+key['key']},json={'name':'escalation'}).status_code==401


def test_state_is_bound_to_browser_expires_and_is_consumed_once(settings):
    service=Accounts(Store(settings))
    state,_=service.begin_login()
    with pytest.raises(InboxError):service.consume_login(state,'different-browser')
    verifier=service.consume_login(state,state)
    assert len(verifier)>=43
    with pytest.raises(InboxError):service.consume_login(state,state)
    state,_=service.begin_login()
    with service.store.connection() as db:db.execute('UPDATE oauth_states SET expires=?',(time.time()-1,))
    with pytest.raises(InboxError):service.consume_login(state,state)


def test_sessions_expire_keys_are_bounded_and_separate(settings):
    service=Accounts(Store(settings));account,session=service.sign_in(42,'developer')
    assert service.session(session)['id']==account['id']
    with pytest.raises(InboxError):service.authenticate_key(session)
    for number in range(10):service.create_key(account['id'],str(number))
    with pytest.raises(InboxError,match='10 active'):service.create_key(account['id'],'eleventh')
    with service.store.connection() as db:db.execute('UPDATE account_sessions SET expires=?',(time.time()-1,))
    with pytest.raises(InboxError):service.session(session)
    assert 'private-client-secret' not in repr(settings)


def test_self_hosting_requires_no_account_or_oauth_configuration(settings):
    settings=replace(settings,hosted_enabled=False,github_client_id='',github_client_secret='')
    with TestClient(create_app(settings),base_url=settings.origin) as client:
        assert client.get('/account').status_code==404
        assert client.get('/auth/github').status_code==404
        assert client.get('/api/account').status_code==404
        inbox=client.post('/api/call',json={'action':'create'}).json()['data']
        assert client.post(inbox['url'],content=b'self-hosted callback').status_code==200
        assert client.post('/api/call',json={'action':'get','token':inbox['token']}).json()['data']['request']['content']=='self-hosted callback'


def test_missing_provider_configuration_and_provider_errors_fail_closed(settings):
    with TestClient(create_app(replace(settings,github_client_secret='')),base_url=settings.origin) as client:
        assert client.get('/auth/github').status_code==503
        assert client.get('/api/account').json()['data']['sign_in_available'] is False
    with TestClient(create_app(settings),base_url=settings.origin) as client,respx.mock:
        respx.post('https://github.com/login/oauth/access_token').respond(200,json={'error':'bad_verification_code'})
        start=client.get('/auth/github',follow_redirects=False)
        state=parse_qs(urlsplit(start.headers['location']).query)['state'][0]
        result=client.get('/auth/github/callback',params={'state':state,'code':'bad'})
        assert result.status_code==400
        assert client.get('/api/account').json()['data']['account'] is None


def test_public_capture_never_exposes_browser_session_cookies(tmp_path):
    settings = Settings(database=str(tmp_path/'cookies.sqlite3'), hosted_enabled=True)
    with TestClient(create_app(settings),base_url=settings.origin) as client:
        inbox=client.post('/api/call',json={'action':'create'}).json()['data']
        client.get(inbox['url'],headers={'Cookie':'openhook-session=ohs_secret; unrelated=private'})
        result=client.post('/api/call',json={'action':'get','token':inbox['token']}).json()['data']['request']
        assert 'cookie' not in result['headers']
        assert 'ohs_secret' not in json.dumps(result)


def test_owner_controlled_capture_html_is_sandboxed_from_hosted_accounts(tmp_path):
    settings=Settings(database=str(tmp_path/'capture-html.sqlite3'),hosted_enabled=True)
    with TestClient(create_app(settings),base_url=settings.origin) as client:
        inbox=client.post('/api/call',json={'action':'create'}).json()['data']
        html='<script src="/assets/app.js"></script><iframe src="/account"></iframe>'
        configured=client.post('/api/call',json={'action':'configure','token':inbox['token'],
            'config':{'default_content_type':'text/html','default_content':html}})
        assert configured.status_code==200
        response=client.get(inbox['url'])
        assert response.text==html
        assert response.headers['content-security-policy']=="sandbox; default-src 'none'; frame-ancestors 'none'"
        assert response.headers['x-content-type-options']=='nosniff'
