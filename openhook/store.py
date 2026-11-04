"""Durable channel storage. Existing unrelated tables are left untouched.

Short transactions and WAL allow the HTTP server and stdio agents to share
one database. Write transactions serialize membership and invite redemption.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import os
import sqlite3
import stat
import time
from pathlib import Path

from openhook.settings import Settings
from openhook.storage_cipher import StorageCipher, event_context, file_context


def timestamp(seconds=None):
    return datetime.fromtimestamp(time.time() if seconds is None else seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.cipher = StorageCipher(settings.storage_key_file) if settings.storage_key_file else None
        settings.prepare()
        # New databases are private even when the operator has a permissive umask.
        path = Path(settings.database)
        descriptor = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError('Database must be a regular file.')
            os.fchmod(descriptor, 0o600)
        finally:
            os.close(descriptor)
        from openhook.sessions import initialize
        from openhook.channel_files import initialize as initialize_files
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            initialize(db)
            initialize_files(db)
            db.execute('CREATE TABLE IF NOT EXISTS storage_protection (id INTEGER PRIMARY KEY CHECK(id=1), required INTEGER NOT NULL)')
            db.execute('INSERT OR IGNORE INTO storage_protection VALUES(1,0)')
        self._protect_events()
        self._ready = True

    def encode_event(self, text, context):
        return self.cipher.encrypt(text, context) if self.cipher else text

    def decode_event(self, row, *, migrating=False):
        if not row['body_encrypted']:
            if self.cipher and not migrating:
                raise ValueError('Plaintext event found in encrypted storage; refusing mixed-mode writes.')
            return row['body']
        if not self.cipher:
            raise ValueError('Encrypted storage requires OPENHOOK_STORAGE_KEY_FILE; refusing plaintext fallback.')
        return self.cipher.decrypt(row['body'], event_context(row['session'], row['sender'], row['kind'], row['message_id']))

    def _protect_events(self):
        # Validate every retained encrypted event before accepting traffic. Migration
        # and key rotation are atomic; a missing/wrong key never rewrites history.
        with self.connection(write=True) as db:
            required = db.execute('SELECT required FROM storage_protection WHERE id=1').fetchone()[0]
            if required and not self.cipher:
                raise ValueError('Encrypted storage requires OPENHOOK_STORAGE_KEY_FILE; refusing plaintext fallback.')
            for row in db.execute('SELECT * FROM session_events'):
                text = self.decode_event(row, migrating=not required)
                if self.cipher and (not row['body_encrypted'] or not self.cipher.uses_active_key(row['body'])):
                    context = event_context(row['session'], row['sender'], row['kind'], row['message_id'])
                    db.execute('UPDATE session_events SET body=?,body_encrypted=1 WHERE sequence=?',
                               (self.encode_event(text, context), row['sequence']))
            for row in db.execute('SELECT * FROM channel_files'):
                if row['encrypted']:
                    if not self.cipher:
                        raise ValueError('Attachment storage requires OPENHOOK_STORAGE_KEY_FILE.')
                    content = self.cipher.decrypt_bytes(row['content'], file_context(row))
                else:
                    if required and self.cipher:
                        raise ValueError('Plaintext attachment in encrypted storage.')
                    content = row['content']
                if self.cipher and (not row['encrypted'] or not self.cipher.uses_active_key(row['content'])):
                    db.execute('UPDATE channel_files SET content=?,encrypted=1 WHERE id=?',
                               (self.cipher.encrypt_bytes(content, file_context(row)), row['id']))
            if self.cipher:
                db.execute('UPDATE storage_protection SET required=1 WHERE id=1')

    @contextmanager
    def connection(self, write=False):
        db = sqlite3.connect(self.settings.database, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA secure_delete=ON")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            if getattr(self, '_ready', False) and not self.cipher:
                required = db.execute('SELECT required FROM storage_protection WHERE id=1').fetchone()[0]
                if required:
                    raise ValueError('Encrypted storage requires OPENHOOK_STORAGE_KEY_FILE; refusing plaintext fallback.')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def cleanup(self):
        from openhook.sessions import expire
        with self.connection(write=True) as db:
            expire(db)
            db.execute('DELETE FROM channel_files WHERE expires<=?', (time.time(),))
