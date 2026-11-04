"""Channel-only product boundary: distribution, data preservation and public/private surfaces."""
from dataclasses import replace
import json
import re
import sqlite3
import time
from xml.etree import ElementTree

import pytest
from starlette.testclient import TestClient
from openhook.pages import PAGES, PUBLIC_PATHS
from openhook.sessions import Sessions
from openhook.settings import Settings
from openhook.store import Store
from openhook.web import create_app


@pytest.fixture
def settings(tmp_path):
    return Settings(database=str(tmp_path/'product.db'), origin='http://testserver',
        umami_script_url='https://analytics.example/script.js',
        umami_website_id='d9c5e0f4-99f5-469e-9a2c-65f65954cbe8', metrics_token='m'*32)


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


def test_only_channel_tools_and_routes(client):
    expected = {'create_agent_channel','join_agent_channel','get_agent_channel',
        'send_agent_message','read_agent_messages','manage_agent_channel','delete_agent_channel',
        'prepare_agent_file_upload','get_agent_file','delete_agent_file'}
    tools = client.get('/api/v1/tools').json()['tools']
    assert {t['name'] for t in tools} == expected
    schema = client.get('/openapi.json').json()
    assert set(schema['paths']) == {'/api/v1/channels','/api/v1/tools','/health',
        '/api/v1/channel-files','/api/v1/channel-files/{file_id}/download'}
    assert schema['components']['schemas']['ChannelCall']['properties']['expiry']['default'] == 2592000
    for path in ('/app','/account','/pricing','/auth/github','/api/account'):
        assert client.get(path).status_code == 404
    for path in ('/api/call','/api/v1/call','/api/wait','/api/export','/h/not-a-channel','/billing/polar','/billing/stripe'):
        assert client.post(path, json={'action':'create'}).status_code == 404


def test_public_pages_and_discovery_are_current(client):
    for path in PUBLIC_PATHS:
        response = client.get(path)
        assert response.status_code == 200 and '{{' not in response.text
        assert 'analytics.example' in response.text
        assert 'href="/pricing"' not in response.text and 'href="/app"' not in response.text
        assert 'application/ld+json' in response.text
        md = client.get(path, headers={'Accept':'text/markdown'})
        assert md.headers['content-type'].startswith('text/markdown')
        assert 'Canonical: http://testserver' in md.text
        for href in re.findall(r'href="(/[^"#?]*)', response.text):
            assert client.get(href).status_code == 200, (path,href)
    sitemap = ElementTree.fromstring(client.get('/sitemap.xml').text)
    assert {loc.text for loc in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')} == {
        'http://testserver'+p for p in PUBLIC_PATHS}
    skill = client.get('/skill.md').text
    assert 'create_agent_channel' in skill and 'create_webhook' not in skill
    assert client.get('/agents.md').text == skill
    assert client.get('/.well-known/agent-skills/openhook/SKILL.md').text == skill
    assert 'Private channels' in client.get('/server.json').text


def test_private_page_cannot_leak_invite_to_analytics(client):
    response=client.get('/channels')
    assert response.headers['cache-control']=='no-store'
    assert 'noindex' in response.headers['x-robots-tag']
    assert response.headers['referrer-policy']=='no-referrer'
    assert 'analytics.example' not in response.text and 'analytics.js' not in response.text
    assert "frame-ancestors 'none'" in response.headers['content-security-policy']
    assert 'tools=(self)' in response.headers['permissions-policy']
    assert client.get('/sessions',follow_redirects=False).headers['location']=='/channels'


def test_analytics_routes_match_the_public_catalog(client):
    from html import unescape
    for path in PUBLIC_PATHS:
        html = client.get(path).text
        routes = re.search(r'data-public-paths="([^"]+)"', html)
        assert routes and set(json.loads(unescape(routes.group(1)))) == set(PUBLIC_PATHS)
    home = client.get('/').text
    assert 'data-analytics-event="copy-setup-click"' in home
    assert 'data-analytics-event="star-click"' in home and 'Star on GitHub' in home


@pytest.mark.parametrize('headers', [{'Origin':'https://evil.test'}, {'Host':'evil.test'}, {'Origin':'null'}])
def test_http_boundary_rejects_cross_site_requests(client, headers):
    response=client.post('/api/v1/channels',json={'action':'create','name':'X','title':'X'},headers=headers)
    assert response.status_code==403


def test_http_rate_limit_and_secret_safe_errors(client):
    for _ in range(120):
        assert client.post('/api/v1/channels',json={'action':'info','participant_token':'ohp_secret'}).status_code==401
    limited=client.post('/api/v1/channels',json={'action':'info'})
    assert limited.status_code==429 and int(limited.headers['retry-after'])>0
    assert 'ohp_secret' not in limited.text


def test_body_limit_and_validation(client):
    response=client.post('/api/v1/channels',content=b'x'*1048577)
    assert response.status_code==413
    response=client.post('/api/v1/channels',json={'action':'info','participant_token':'ohp_secret','unknown':'private'})
    assert response.status_code==400 and 'ohp_secret' not in response.text and 'private' not in response.text


def test_channel_only_start_preserves_unrelated_legacy_data(settings):
    with sqlite3.connect(settings.database) as db:
        db.executescript("CREATE TABLE inboxes(id TEXT, expires REAL); CREATE TABLE accounts(id TEXT); CREATE TABLE polar_orders(id TEXT);")
        db.execute('INSERT INTO inboxes VALUES(?,?)',('legacy',time.time()-100))
        db.execute('INSERT INTO accounts VALUES(?)',('keep-account',))
        db.execute('INSERT INTO polar_orders VALUES(?)',('keep-order',))
    store=Store(settings)
    channel=Sessions(store).create('Owner','Keep my channel')
    Sessions(store).send(channel['participant_token'],'Keep my message','original')
    for _ in range(2):
        store=Store(settings); store.cleanup()
        assert Sessions(store).read(channel['participant_token'])['events'][-1]['text']=='Keep my message'
        with store.connection() as db:
            assert db.execute('SELECT id FROM inboxes').fetchone()[0]=='legacy'
            assert db.execute('SELECT id FROM accounts').fetchone()[0]=='keep-account'
            assert db.execute('SELECT id FROM polar_orders').fetchone()[0]=='keep-order'


def test_fresh_database_only_contains_channel_tables(settings):
    with Store(settings).connection() as db:
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert tables=={'agent_sessions','session_members','session_events','sqlite_sequence','storage_protection','channel_files'}


def test_metrics_require_key_and_only_expose_aggregate_channels(client):
    assert client.get('/metrics').status_code==401
    response=client.get('/metrics',headers={'Authorization':'Bearer '+'m'*32})
    assert response.status_code==200
    assert 'openhook_channels' in response.text and 'openhook_retained_messages' in response.text
    assert 'openhook_inboxes' not in response.text and 'participant_token' not in response.text


def test_runtime_never_reads_retired_provider_credentials(monkeypatch):
    import os
    original=os.getenv
    def getenv(name,default=None):
        assert not any(key in name for key in ('STRIPE','POLAR','GITHUB','SMTP','DNS','OPENCLAW'))
        return original(name,default)
    monkeypatch.setattr(os,'getenv',getenv)
    Settings.from_env()


def test_new_database_is_private_by_default(settings):
    from pathlib import Path
    Store(settings)
    assert Path(settings.database).stat().st_mode & 0o077 == 0


def test_react_homepage_is_readable_and_does_not_load_on_private_pages(client):
    home = client.get('/')
    assert 'id="home-root" data-origin="http://testserver"' in home.text
    assert 'A place for your agents' in home.text and 'work together.' in home.text
    assert 'Connect your agent' in home.text and 'Copy prompt' in home.text
    assert 'http://testserver/skill.md' in home.text
    assert '<noscript>' in home.text and 'Read the setup prompt' in home.text
    assert 'style=' not in home.text
    assert "'unsafe-inline'" not in home.headers['content-security-policy']
    for asset in ('home.js', 'home.css'):
        assert f'/assets/{asset}?v=' in home.text
        assert client.get(f'/assets/{asset}').status_code == 200
        assert f'/assets/{asset}' not in client.get('/channels').text
