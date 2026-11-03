"""Deliver external data to an already loaded Codex thread, without user input."""
import json
import os
from pathlib import Path
from queue import Queue, Empty
import stat
from threading import Thread

from websockets.sync.client import unix_connect


class CodexDelivery:
    def __init__(self, path, thread_id):
        path = Path(path).expanduser()
        original_parent = path.parent.stat()
        original = path.lstat()
        if (original.st_uid != os.getuid() or original_parent.st_uid != os.getuid()
                or original_parent.st_mode & 0o077):
            raise ValueError('Use an owned Codex socket inside a private directory.')
        # Codex's private control directory may contain its owned socket alias.
        path = path.resolve(strict=True)
        info, parent = path.lstat(), path.parent.stat()
        if (not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid()
                or parent.st_uid != os.getuid() or parent.st_mode & 0o077):
            raise ValueError('Use an owned Codex socket inside a private directory.')
        self.thread_id, self.next_id = thread_id, 0
        self.responses = Queue(maxsize=4)
        self.context = unix_connect(str(path), open_timeout=3, close_timeout=1, max_size=2**20, proxy=None)
        self.connection = self.context.__enter__()
        self.reader = Thread(target=self._receive, daemon=True)
        self.reader.start()
        try:
            self.call('initialize', {'clientInfo': {'name': 'openhook_local_delivery', 'version': '0.2.0'}})
            self.connection.send(json.dumps({'method': 'initialized', 'params': {}}))
            self.check_thread()
        except Exception:
            self.close()
            raise

    def _receive(self):
        try:
            for raw in self.connection:
                message = json.loads(raw)
                if 'id' in message and 'method' not in message:
                    self.responses.put_nowait(message)
                elif 'id' in message:
                    # An automated channel bridge cannot grant human approval.
                    self.connection.send(json.dumps({'id': message['id'], 'error': {
                        'code': -32000, 'message': 'Openhook cannot approve actions. Use the agent UI.'}}))
        except Exception:
            pass
        finally:
            try:
                self.responses.put_nowait(None)
            except Exception:
                pass

    def call(self, method, params):
        self.next_id += 1
        self.connection.send(json.dumps({'id': self.next_id, 'method': method, 'params': params}))
        try:
            response = self.responses.get(timeout=5)
        except Empty:
            raise ConnectionError('Codex did not acknowledge the request.') from None
        if not response or response.get('id') != self.next_id:
            raise ConnectionError('Codex disconnected before acknowledgement.')
        if 'error' in response:
            raise ValueError('Codex rejected delivery; check runtime compatibility and the target session.')
        return response['result']

    def check_thread(self):
        thread = self.call('thread/read', {'threadId': self.thread_id})['thread']
        if thread['status']['type'] not in ('idle', 'active'):
            raise ValueError('Target must already be running in this Codex host.')

    def deliver(self, payload):
        self.check_thread()
        # No turn overrides, role injection, synthetic user prompt or approval grants.
        result = self.call('turn/start', {'threadId': self.thread_id, 'input': [], 'toolOutput': {
            'name': 'openhook_peer_message', 'namespace': None, 'output': json.dumps(payload)}})
        if (not isinstance(result, dict) or not isinstance(result.get('turn'), dict)
                or not isinstance(result['turn'].get('id'), str) or not result['turn']['id']):
            raise ValueError('Codex did not return a delivery receipt.')
        return result

    def close(self):
        self.context.__exit__(None, None, None)
        self.reader.join(timeout=2)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
