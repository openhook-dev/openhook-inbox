"""A short-lived two-participant protocol demo; no AI models or credentials needed."""
import argparse
import json
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from uuid import uuid4


def run(origin):
    def call(action, **fields):
        request = Request(origin.rstrip('/') + '/api/v1/channels',
                          data=json.dumps({'action': action, **fields}).encode(),
                          headers={'Content-Type': 'application/json'})
        with urlopen(request, timeout=35) as response:
            return json.load(response)['data']

    owner = call('create', name='Demo agent A', title='Protocol demo (scripted QA)', expiry=300)
    token = owner['participant_token']
    try:
        guest = call('join', invite_code=owner['invite_code'], name='Demo agent B')
        question, answer = 'Are the designs ready?', 'The first two screens are ready for review.'
        call('send', participant_token=token, text=question, message_id=uuid4().hex)
        received = call('read', participant_token=guest['participant_token'])
        assert any(e.get('text') == question for e in received['events']), 'Question was not received'
        call('send', participant_token=guest['participant_token'], text=answer, message_id=uuid4().hex)
        reply = call('read', participant_token=token)
        assert any(e.get('text') == answer for e in reply['events']), 'Reply was not received'
        print('Agent A → Agent B:', question)
        print('Agent B → Agent A:', answer)
        print('Verified two-way HTTP delivery between scripted participants.')
    finally:
        call('close', participant_token=token)
        print('Demo channel deleted.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', default='http://127.0.0.1:8788', help='Openhook deployment URL')
    origin = parser.parse_args().origin
    url = urlsplit(origin)
    if url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1'}):
        parser.error('Use HTTPS for remote deployments, or HTTP on localhost.')
    run(origin)
