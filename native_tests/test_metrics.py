"""Metrics remain private and cannot leak capability URLs or event content."""

from dataclasses import replace

from starlette.testclient import TestClient

from openhook.metrics import CAPTURES, REGISTRY
from openhook.settings import Settings
from openhook.web import create_app


def test_metrics_auth_redaction_and_accepted_events(tmp_path):
    settings = Settings(database=str(tmp_path / "metrics.db"), origin="http://testserver", metrics_token="m" * 40)
    sample = lambda: REGISTRY.get_sample_value("openhook_captured_events_total", {"transport": "web", "traffic": "unmarked"}) or 0
    before = sample()
    with TestClient(create_app(settings)) as client:
        assert client.get('/metrics').status_code == 401
        assert client.get('/metrics', headers={'Authorization': 'Bearer wrong'}).status_code == 401
        inbox = client.post('/api/call', json={'action': 'create'}).json()['data']
        for _ in range(2):
            assert client.post(inbox['url'], content='private payload', headers={'Idempotency-Key': 'same'}).status_code == 200
        assert sample() == before + 1
        client.get('/untrusted-path-secret?token=secret')
        response = client.get('/metrics', headers={'Authorization': 'Bearer ' + settings.metrics_token})
        assert response.status_code == 200
        assert response.headers['cache-control'] == 'no-store'
        assert 'openhook_retained_events 1.0' in response.text
        assert 'route="other"' in response.text
        assert 'route="/h"' in response.text
        for secret in (inbox['token'], inbox['inbox_id'], 'private payload', 'untrusted-path-secret', 'token=secret', settings.metrics_token):
            assert secret not in response.text
    with TestClient(create_app(replace(settings, metrics_token=''))) as client:
        assert client.get('/metrics').status_code == 404


def test_analytics_public_only_and_csp(tmp_path):
    settings = Settings(database=str(tmp_path / 'analytics.db'), origin='https://openhook.dev', hosted_enabled=True,
                        umami_script_url='https://analytics.example.com/script.js',
                        umami_website_id='d9c5e0f4-99f5-469e-9a2c-65f65954cbe8')
    with TestClient(create_app(settings), base_url=settings.origin) as client:
        for path in ['/', '/connect', '/docs', '/pricing', '/privacy']:
            response = client.get(path)
            assert 'data-before-send="openhookAnalyticsBeforeSend"' in response.text
            assert 'data-exclude-search="true"' in response.text
            assert 'https://analytics.example.com' in response.headers['content-security-policy']
            assert "unsafe-inline" not in response.headers['content-security-policy']
            assert '{{' not in response.text
        for path in ['/app', '/account']:
            response = client.get(path)
            assert 'analytics.js' not in response.text
            assert 'analytics.example.com' not in response.headers['content-security-policy']
        assert 'self-hosted Umami' in client.get('/privacy').text
    with TestClient(create_app(replace(settings, umami_script_url='', umami_website_id=''))) as client:
        assert 'analytics.js' not in client.get('/').text
        assert 'Analytics are disabled' in client.get('/privacy').text
