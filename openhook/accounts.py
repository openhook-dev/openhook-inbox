"""Optional hosted identity. Sessions and agent keys are separate capabilities.

The self-hosted capture service does not depend on an account or provider.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from uuid import uuid4

from openhook.store import InboxError, Store, token_hash
from openhook import hosted_store

SESSION_SECONDS = 30 * 86400
OAUTH_SECONDS = 600


class Accounts:
    def __init__(self, store: Store):
        self.store = store
        if not store.settings.hosted_enabled:
            raise InboxError("Hosted accounts are not enabled on this deployment.", 404)

    def begin_login(self) -> tuple[str, str]:
        state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(48)
        with self.store.connection(write=True) as db:
            db.execute("DELETE FROM oauth_states WHERE expires<=?", (time.time(),))
            if db.execute("SELECT COUNT(*) FROM oauth_states").fetchone()[0] >= 10000:
                raise InboxError("Sign-in capacity reached. Try again shortly.", 429)
            db.execute("INSERT INTO oauth_states VALUES(?,?,?)", (token_hash(state), verifier, time.time() + OAUTH_SECONDS))
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        return state, challenge

    def consume_login(self, state: str, browser_state: str) -> str:
        if not state or len(state) > 100 or not secrets.compare_digest(state.encode(), browser_state.encode()):
            raise InboxError("Sign-in expired or could not be verified. Start again.", 400)
        with self.store.connection(write=True) as db:
            row = db.execute("SELECT * FROM oauth_states WHERE state_hash=? AND expires>?", (token_hash(state), time.time())).fetchone()
            if not row:
                raise InboxError("Sign-in expired or could not be verified. Start again.", 400)
            db.execute("DELETE FROM oauth_states WHERE state_hash=?", (token_hash(state),))
            return row["verifier"]

    def sign_in(self, github_id: int, login: str) -> tuple[dict, str]:
        if type(github_id) is not int or github_id <= 0 or not isinstance(login, str) or not 1 <= len(login) <= 100:
            raise InboxError("The identity provider returned an invalid account.", 502)
        token = "ohs_" + secrets.token_urlsafe(32)
        now = time.time()
        with self.store.connection(write=True) as db:
            db.execute("INSERT INTO accounts(id,github_id,login,created) VALUES(?,?,?,?) "
                       "ON CONFLICT(github_id) DO UPDATE SET login=excluded.login",
                       (str(uuid4()), github_id, login, now))
            account = dict(db.execute("SELECT * FROM accounts WHERE github_id=?", (github_id,)).fetchone())
            db.execute("DELETE FROM account_sessions WHERE expires<=?", (now,))
            # Bound stored sessions without unexpectedly signing out current devices.
            db.execute("DELETE FROM account_sessions WHERE account=? AND key_hash NOT IN "
                       "(SELECT key_hash FROM account_sessions WHERE account=? ORDER BY created DESC LIMIT 19)",
                       (account["id"], account["id"]))
            db.execute("INSERT INTO account_sessions VALUES(?,?,?,?)", (token_hash(token), account["id"], now, now + SESSION_SECONDS))
        return account, token

    def session(self, token: str) -> dict:
        if not token.startswith("ohs_") or len(token) > 100:
            raise InboxError("Sign in to your hosted account.", 401)
        with self.store.connection() as db:
            row = db.execute("SELECT a.* FROM accounts a JOIN account_sessions s ON a.id=s.account "
                             "WHERE s.key_hash=? AND s.expires>?", (token_hash(token), time.time())).fetchone()
        if not row:
            raise InboxError("Your session expired. Sign in again.", 401)
        return dict(row)

    def sign_out(self, token: str) -> None:
        with self.store.connection(write=True) as db:
            db.execute("DELETE FROM account_sessions WHERE key_hash=?", (token_hash(token),))

    def keys(self, account: str) -> list[dict]:
        with self.store.connection() as db:
            return [dict(row) for row in db.execute(
                "SELECT id,name,suffix,created FROM account_keys WHERE account=? AND revoked IS NULL ORDER BY created DESC", (account,))]

    def create_key(self, account: str, name: str) -> dict:
        name = name.strip()
        if not 1 <= len(name) <= 60:
            raise InboxError("Name the key using 1 to 60 characters.")
        key = "oha_" + secrets.token_urlsafe(32)
        identifier, now = str(uuid4()), time.time()
        with self.store.connection(write=True) as db:
            if db.execute("SELECT COUNT(*) FROM account_keys WHERE account=? AND revoked IS NULL", (account,)).fetchone()[0] >= 10:
                raise InboxError("You can have 10 active agent keys. Revoke an unused key first.", 409)
            db.execute("INSERT INTO account_keys(id,account,name,key_hash,suffix,created) VALUES(?,?,?,?,?,?)",
                       (identifier, account, name, token_hash(key), key[-4:], now))
        return {"id": identifier, "name": name, "key": key, "suffix": key[-4:], "created": now}

    def revoke_key(self, account: str, identifier: str) -> None:
        with self.store.connection(write=True) as db:
            row = db.execute("SELECT id FROM account_keys WHERE id=? AND account=?", (identifier, account)).fetchone()
            if not row:
                raise InboxError("Agent key not found.", 404)
            db.execute("UPDATE account_keys SET revoked=COALESCE(revoked,?) WHERE id=?", (time.time(), identifier))

    def authenticate_key(self, key: str) -> dict:
        if not key.startswith("oha_") or len(key) > 100:
            raise InboxError("Supply a hosted agent key.", 401)
        with self.store.connection() as db:
            row = db.execute("SELECT a.* FROM accounts a JOIN account_keys k ON a.id=k.account "
                             "WHERE k.key_hash=? AND k.revoked IS NULL", (token_hash(key),)).fetchone()
        if not row:
            raise InboxError("Invalid or revoked hosted agent key.", 401)
        return dict(row)

    def usage(self, account: str) -> dict:
        now = time.time()
        with self.store.connection() as db:
            entitlement = db.execute("SELECT paid_until,status FROM hosted_entitlements WHERE account=?", (account,)).fetchone()
            usage = db.execute("SELECT events FROM account_usage WHERE account=? AND month=?", (account, hosted_store.month_at(now))).fetchone()
            count = db.execute("SELECT COUNT(*) FROM hosted_inboxes WHERE account=?", (account,)).fetchone()[0]
            size = hosted_store.retained_bytes(db, account)
        return {"plan": "pro" if entitlement and entitlement["paid_until"] > now else "free",
                "paid_until": entitlement["paid_until"] if entitlement else None,
                "billing_status": entitlement["status"] if entitlement else "free",
                "month": hosted_store.month_at(now), "events": usage["events"] if usage else 0,
                "inboxes": count, "retained_bytes": size,
                "limits": {"inboxes": hosted_store.PRO_INBOXES, "monthly_events": hosted_store.PRO_MONTHLY_EVENTS,
                           "retained_bytes": hosted_store.PRO_RETAINED_BYTES, "retention_days": 30}}

    def inboxes(self, account: str) -> list[dict]:
        with self.store.connection() as db:
            return [dict(row) for row in db.execute(
                "SELECT i.id,i.name,i.created,i.expires,(SELECT COUNT(*) FROM events e WHERE e.inbox=i.id) AS events "
                "FROM inboxes i JOIN hosted_inboxes h ON h.inbox=i.id WHERE h.account=? AND i.expires>? ORDER BY i.created DESC",
                (account, time.time()))]

    def inbox_access(self, account: str, identifier: str) -> dict:
        """Recover access across devices without storing plaintext inbox tokens."""
        token, now = "ohk_" + secrets.token_urlsafe(32), time.time()
        with self.store.connection(write=True) as db:
            inbox = db.execute("SELECT i.* FROM inboxes i JOIN hosted_inboxes h ON h.inbox=i.id "
                               "WHERE i.id=? AND h.account=? AND i.expires>?", (identifier, account, now)).fetchone()
            if not inbox:
                raise InboxError("Hosted inbox not found.", 404)
            db.execute("DELETE FROM inbox_access WHERE expires<=?", (now,))
            if db.execute("SELECT COUNT(*) FROM inbox_access WHERE inbox=?", (identifier,)).fetchone()[0] >= 20:
                raise InboxError("This inbox has 20 active access tokens. Rotate its token to revoke old access.", 409)
            db.execute("INSERT INTO inbox_access VALUES(?,?,?,?)", (token_hash(token), identifier, now, min(inbox["expires"], now + SESSION_SECONDS)))
            self.store._audit(db, identifier, "inbox.access_issued", actor="account")
        return self.store.info(token)
