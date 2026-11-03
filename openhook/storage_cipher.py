"""Authenticated encryption for event bodies; server-held keys, not E2EE."""
import json
import os
from pathlib import Path
import stat

from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class StorageCipher:
    def __init__(self, key_file):
        path = Path(key_file).expanduser()
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(descriptor) as source:
            info = os.fstat(source.fileno())
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                    or info.st_mode & 0o077 or info.st_size > 4096):
                raise ValueError('Storage key file must be a private regular file of at most 4096 bytes.')
            try:
                keys = json.loads(source.read(4097))
                if not isinstance(keys, list) or not 1 <= len(keys) <= 8 or not all(isinstance(k, str) for k in keys):
                    raise ValueError
                self.keys = [Fernet(key.encode('ascii')) for key in keys]
            except (ValueError, TypeError, UnicodeError):
                raise ValueError('Storage key file must contain a JSON list of valid Fernet keys.') from None
        self.cipher = MultiFernet(self.keys)

    def encrypt(self, text, context):
        return self.keys[0].encrypt(json.dumps([context, text], ensure_ascii=False).encode()).decode('ascii')

    def decrypt(self, body, context):
        try:
            bound_context, text = json.loads(self.cipher.decrypt(body.encode('ascii')))
            if bound_context != context or not isinstance(text, str):
                raise ValueError
            return text
        except (InvalidToken, ValueError, TypeError, UnicodeError):
            raise ValueError('Stored event authentication failed; check storage keys and database integrity.') from None

    def uses_active_key(self, body):
        try:
            self.keys[0].decrypt(body.encode('ascii'))
            return True
        except InvalidToken:
            return False


def event_context(session, sender, kind, message_id):
    return ['openhook-event-v1', session, sender, kind, message_id]
