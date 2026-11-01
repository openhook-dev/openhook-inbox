"""Durable channel storage. Existing unrelated tables are left untouched.

Short transactions and WAL allow the HTTP server and stdio agents to share
one database. Write transactions serialize membership and invite redemption.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import sqlite3
import time
from pathlib import Path

from openhook.settings import Settings


def timestamp(seconds=None):
    return datetime.fromtimestamp(time.time() if seconds is None else seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.prepare()
        # New databases are private even when the operator has a permissive umask.
        Path(settings.database).touch(mode=0o600, exist_ok=True)
        from openhook.sessions import initialize
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            initialize(db)

    @contextmanager
    def connection(self, write=False):
        db = sqlite3.connect(self.settings.database, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
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
