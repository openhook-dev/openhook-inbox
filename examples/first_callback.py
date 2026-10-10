"""Create a disposable inbox, receive one real callback, verify it, and clean up.

Uses only Python's standard library. No account or installation is required.
The default destination is the public Openhook service. Private tokens are never
printed; the inbox and its event are deleted even if verification fails.
"""

import argparse
import base64
import json
import sys
import urllib.error
import urllib.request
from uuid import uuid4


def request(url, payload):
    body = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=35) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='https://openhook.dev', help='Hosted or self-hosted Openhook origin')
    origin = parser.parse_args().url.rstrip('/')
    inbox = None
    try:
        result = json.loads(request(origin + '/api/call', {'action': 'create'}))
        inbox = result['data']
        print('1. Created a disposable inbox. Its private token stays in memory.')
        payload = {'event': 'openhook.quickstart', 'delivery': str(uuid4())}
        sent = json.dumps(payload).encode()
        request(inbox['url'], payload)
        print('2. Sent a real HTTP callback to its public URL.')
        received = json.loads(request(origin + '/api/wait', {
            'token': inbox['token'], 'since': 0, 'timeout_seconds': 5,
        }))['data']
        if received['timeout'] or not received['request']:
            raise RuntimeError('The inbox did not return the callback.')
        if base64.b64decode(received['request']['body_base64']) != sent:
            raise RuntimeError('The received bytes differ from the sent callback.')
        print('3. Read the callback from the private inbox; original bytes match.')
        print(json.dumps(payload, indent=2))
    finally:
        if inbox:
            result = json.loads(request(origin + '/api/call', {'action': 'delete', 'token': inbox['token']}))
            if not result.get('success'):
                raise RuntimeError('The disposable inbox could not be deleted; it will expire automatically.')
            print('4. Deleted the disposable inbox and payload. Minimal activity metadata remains.')


if __name__ == '__main__':
    try:
        main()
    except urllib.error.HTTPError as exc:
        # Provider bodies and URLs might contain secrets. Report only the status.
        print(f'Openhook returned HTTP {exc.code}. Check the origin and try again.', file=sys.stderr)
        sys.exit(1)
    except (urllib.error.URLError, TimeoutError):
        print('Could not reach Openhook. Check the origin and connection.', file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, RuntimeError) as exc:
        print('The callback check failed: ' + str(exc), file=sys.stderr)
        sys.exit(1)
