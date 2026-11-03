"""Smoke-test an isolated installed wheel, including removed surfaces."""
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
from zipfile import ZipFile


def main():
    getenv = os.getenv
    def safe_env(name, default=None):
        assert not name.startswith(("OPENHOOK_GITHUB_", "OPENHOOK_POLAR_", "OPENHOOK_STRIPE_", "OPENHOOK_BILLING_")), name
        return getenv(name, default)
    os.getenv = safe_env
    with ZipFile(sys.argv[1]) as wheel:
        names = wheel.namelist()
        for removed in ("tools", "providers", "transports", "accounts", "hosted_store", "listener"):
            assert f"openhook/{removed}.py" not in names
        assert not any(name.startswith("openhook_hosted/") for name in names)
        for module in ('channel_inbox', 'channel_listener'):
            assert f'openhook/{module}.py' in names
    for module in ('channel_inbox', 'channel_listener'):
        subprocess.run([sys.executable, '-I', '-m', f'openhook.{module}', '--help'],
                       check=True, stdout=subprocess.DEVNULL)
    from starlette.testclient import TestClient
    from openhook.settings import Settings
    from openhook.web import create_app
    with tempfile.TemporaryDirectory() as directory:
        settings = Settings(database=str(Path(directory) / "channels.db"), origin="http://testserver")
        with TestClient(create_app(settings)) as client:
            assert client.get('/health').status_code == 200
            for path in ('/api/account', '/auth/github', '/pricing', '/app'):
                assert client.get(path).status_code == 404
            assert client.post('/api/call', json={'action': 'create'}).status_code == 404
            def call(action, **args):
                response = client.post('/api/v1/channels', json={'action': action, **args})
                assert response.status_code == 200, response.text
                return response.json()['data']
            owner = call('create', name='Owner', title='Wheel check')
            guest = call('join', invite_code=owner['invite_url'], name='Guest')
            call('send', participant_token=guest['participant_token'], text='Packaged channel', message_id='wheel')
            assert call('read', participant_token=owner['participant_token'])['events'][-1]['text'] == 'Packaged channel'
            tools = client.get('/api/v1/tools').json()['tools']
            assert len(tools) == 7
            result = client.post('/mcp', headers={'Accept': 'application/json, text/event-stream'}, json={
                'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {
                    'name': 'read_agent_messages', 'arguments': {'participant_token': owner['participant_token']}}}).json()['result']
            assert not result.get('isError') and 'Packaged channel' in json.dumps(result)
            assert client.get('/channels').status_code == 200
            assert client.get('/assets/sessions.js').status_code == 200
    print('Isolated channel wheel: create, join, send, MCP read and retired-surface checks passed.')


if __name__ == '__main__':
    main()
