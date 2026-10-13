"""Exercise the public contracts used by independent agents and readiness scans."""

import hashlib

import pytest
from starlette.testclient import TestClient

from openhook.pages import PUBLIC_PATHS, prefers_markdown
from openhook_hosted.settings import HostedSettings as Settings
from openhook_hosted.app import create_app
from server import build_mcp


def test_canonical_markdown_and_recoverable_errors(tmp_path):
    settings = Settings(database=str(tmp_path / 'readiness.db'), origin='http://testserver', hosted_enabled=True)
    with TestClient(create_app(settings)) as client:
        for path in PUBLIC_PATHS:
            markdown = client.get(path, headers={'Accept': 'text/markdown'})
            html = client.get(path, headers={'Accept': 'text/html'})
            assert markdown.status_code == html.status_code == 200
            assert markdown.headers['content-type'].startswith('text/markdown')
            assert html.headers['content-type'].startswith('text/html')
            assert 'Accept' in markdown.headers['vary'] and 'Accept' in html.headers['vary']
            assert '# ' in markdown.text and 'Canonical: http://testserver' + path in markdown.text
            assert '{{' not in markdown.text and '<script' not in markdown.text
        assert client.get('/account', headers={'Accept': 'text/markdown'}).headers['content-type'].startswith('text/html')
        missing = client.get('/not-found?secret=do-not-reflect', headers={'Accept': 'text/markdown'})
        assert missing.status_code == 404 and missing.headers['content-type'].startswith('text/markdown')
        assert '/docs' in missing.text and 'do-not-reflect' not in missing.text
        for path, status in [('/api/missing', 404), ('/api/v1/call', 405)]:
            error = client.get(path)
            assert error.status_code == status
            assert error.headers['content-type'].startswith('application/problem+json')
            assert error.json()['status'] == status
            assert error.json()['code'] and error.json()['resolution']
        bad = client.post('/api/v1/call', json={'action': 'bad', 'token': 'secret-input'})
        assert bad.status_code == 400 and 'secret-input' not in bad.text
        assert bad.json()['success'] is False


def test_markdown_quality_values():
    assert prefers_markdown('text/markdown')
    assert not prefers_markdown('text/markdown;q=0, text/html')
    assert not prefers_markdown('text/markdown;q=.5, text/html;q=.9')
    assert not prefers_markdown('*/*')
    assert not prefers_markdown('text/markdown;q=broken')


def test_versioned_aliases_and_rate_limit_contract(tmp_path):
    with TestClient(create_app(Settings(database=str(tmp_path / 'limits.db'), origin='http://testserver'))) as client:
        created = client.post('/api/v1/call', json={'action': 'create'})
        assert created.status_code == 200
        assert created.headers['ratelimit-remaining'] == '119'
        inbox = created.json()['data']
        info = client.post('/api/call', json={'action': 'info', 'token': inbox['token']})
        assert info.json()['data']['inbox_id'] == inbox['inbox_id']
        for _ in range(118):
            assert client.get('/api/v1/tools').status_code == 200
        limited = client.get('/api/tools')
        assert limited.status_code == 429
        assert limited.json()['status'] == 429
        assert limited.headers['ratelimit-remaining'] == '0'
        assert 1 <= int(limited.headers['retry-after']) <= 60
        assert 'q=120;w=60' in limited.headers['ratelimit-policy']


def test_discovery_digest_and_actual_api_schemas(tmp_path):
    with TestClient(create_app(Settings(database=str(tmp_path / 'discovery.db'), origin='http://testserver'))) as client:
        entry = client.get('/.well-known/agent-skills/index.json').json()['skills'][0]
        text = client.get(entry['url']).text
        assert entry['digest'] == 'sha256:' + hashlib.sha256(text.encode()).hexdigest()
        assert text == client.get('/skill.md').text
        for path in ['/server.json', '/.well-known/mcp/server-card.json']:
            manifest = client.get(path).json()
            assert manifest['remotes'][0]['url'] == 'http://testserver/mcp'
            assert client.get(manifest['icons'][0]['src']).status_code == 200
        schema = client.get('/openapi.json').json()
        ids = []
        for path, operations in schema['paths'].items():
            for operation in operations.values():
                ids.append(operation['operationId'])
                assert 'content' in operation['responses']['200']
                assert 'application/problem+json' in operation['responses']['404']['content']
        assert len(ids) == len(set(ids))
        assert '/api/v1/call' in schema['paths'] and '/api/call' in schema['paths']
        assert schema['paths']['/h/{identifier}']['post']['parameters'][1]['name'] == 'Idempotency-Key'


@pytest.mark.asyncio
async def test_advertised_mcp_resources_have_useful_public_content(tmp_path):
    server = build_mcp(Settings(database=str(tmp_path / 'resources.db'), origin='https://example.com'))
    resources = await server.list_resources()
    assert len(resources) == 3
    for resource in resources:
        assert resource.mime_type == 'text/markdown'
        contents = await server.read_resource(str(resource.uri))
        assert contents and all(len(content.content) > 100 for content in contents)
    guide = await server.read_resource('openhook://docs/guide')
    assert 'Hosted Pro' in guide[0].content
