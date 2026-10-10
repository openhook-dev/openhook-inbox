"""A single durable store for every Openhook transport.

Connections are short-lived so SMTP threads and separate stdio processes share
the same WAL database safely. Write transactions enforce bounds atomically.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import re
import secrets
import shutil
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from openhook.settings import Settings


class InboxError(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


class ResponseSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    default_status: int = Field(default=200, ge=200, le=599)
    default_content: str = Field(default="Received by Openhook", max_length=10000)
    default_content_type: str = Field(default="text/plain", pattern=r"^[a-zA-Z0-9.+-]+/[a-zA-Z0-9.+-]+(?:;[a-zA-Z0-9 =.+-]+)?$", max_length=200)
    cors: bool = False
    verification_secret: str = Field(default="", max_length=256)
    signature_provider: Literal["generic", "github", "stripe", "linear"] = "generic"
    enabled: bool = True


def timestamp(seconds: float | None = None) -> str:
    return datetime.fromtimestamp(seconds or time.time(), timezone.utc).isoformat().replace("+00:00", "Z")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Store:
    def __init__(self, settings: Settings):
        self.settings = settings
        settings.prepare()
        with self.connection() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS inboxes (
                    id TEXT PRIMARY KEY, key_hash TEXT NOT NULL UNIQUE,
                    created REAL NOT NULL, expires REAL NOT NULL,
                    config TEXT NOT NULL, name TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS events (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    id TEXT NOT NULL UNIQUE, inbox TEXT NOT NULL,
                    created REAL NOT NULL, kind TEXT NOT NULL,
                    payload TEXT NOT NULL, source_id TEXT,
                    FOREIGN KEY (inbox) REFERENCES inboxes(id) ON DELETE CASCADE,
                    UNIQUE(inbox, source_id)
                );
                CREATE INDEX IF NOT EXISTS events_inbox_sequence ON events(inbox, sequence);
                CREATE TABLE IF NOT EXISTS subscriptions (
                    inbox TEXT PRIMARY KEY, provider TEXT NOT NULL,
                    external_id TEXT NOT NULL, target TEXT NOT NULL,
                    FOREIGN KEY (inbox) REFERENCES inboxes(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS responses (
                    event TEXT PRIMARY KEY, status INTEGER NOT NULL, content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    FOREIGN KEY (event) REFERENCES events(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS activity (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    inbox TEXT NOT NULL, event TEXT,
                    created REAL NOT NULL, action TEXT NOT NULL,
                    actor TEXT NOT NULL, details TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS activity_inbox_sequence ON activity(inbox, sequence);
                CREATE INDEX IF NOT EXISTS activity_event ON activity(event);
            """)
        # Preserve existing payloads; do not invent a pre-release mutation trail.
        with self.connection(write=True) as db:
            for row in db.execute("SELECT id,created FROM inboxes WHERE NOT EXISTS (SELECT 1 FROM activity WHERE activity.inbox=inboxes.id)").fetchall():
                self._audit(db, row["id"], "inbox.imported", actor="system", created=row["created"])
            for row in db.execute("SELECT id,inbox,created,kind FROM events WHERE NOT EXISTS (SELECT 1 FROM activity WHERE activity.event=events.id)").fetchall():
                self._audit(db, row["inbox"], "event.imported", row["id"], {"type": row["kind"]}, actor="system", created=row["created"])

    @contextmanager
    def connection(self, write: bool = False):
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

    def _row(self, db, identifier: str, *, public: bool = False):
        if public:
            row = db.execute("SELECT * FROM inboxes WHERE id=?", (identifier,)).fetchone()
        else:
            if not identifier.startswith("ohk_") or len(identifier) > 100:
                raise InboxError("Use the private management token returned by create_webhook, not the public capture URL.", 401)
            row = db.execute("SELECT * FROM inboxes WHERE key_hash=?", (token_hash(identifier),)).fetchone()
        if not row or row["expires"] <= time.time():
            raise InboxError("Inbox not found or expired.", 404)
        return row

    def cleanup(self) -> int:
        with self.connection(write=True) as db:
            return self._expire(db)

    def _audit(self, db, inbox: str, action: str, event: str | None = None, details: dict | None = None,
               *, actor: str = "management-token", created: float | None = None):
        # No foreign key: minimal history survives intentional payload deletion.
        # Callers allowlist details; never copy secrets, bodies, notes or config.
        db.execute("INSERT INTO activity(inbox,event,created,action,actor,details) VALUES(?,?,?,?,?,?)",
                   (inbox, event, created if created is not None else time.time(), action, actor, json.dumps(details or {})))

    def _delete_events(self, db, inbox: str, request_id: str | None = None, *, reason: str = "event.deleted", actor: str = "management-token") -> int:
        where = "inbox=?" + (" AND id=?" if request_id else "")
        args = [inbox, request_id] if request_id else [inbox]
        for row in db.execute(f"SELECT id,kind FROM events WHERE {where}", args).fetchall():
            self._audit(db, inbox, reason, row["id"], {"type": row["kind"]}, actor=actor)
        return db.execute(f"DELETE FROM events WHERE {where}", args).rowcount

    def _expire(self, db) -> int:
        rows = db.execute("SELECT id FROM inboxes WHERE expires <= ?", (time.time(),)).fetchall()
        for row in rows:
            count = self._delete_events(db, row["id"], reason="event.expired", actor="system")
            self._audit(db, row["id"], "inbox.expired", details={"deleted_events": count}, actor="system")
            db.execute("DELETE FROM inboxes WHERE id=?", (row["id"],))
        return len(rows)

    def activity(self, token: str, *, since: int = 0, limit: int = 100) -> dict:
        if since < 0 or not 1 <= limit <= 1000:
            raise InboxError("Invalid activity cursor or limit.")
        with self.connection() as db:
            inbox = self._row(db, token)
            rows = db.execute("SELECT * FROM activity WHERE inbox=? AND sequence>? ORDER BY sequence LIMIT ?",
                              (inbox["id"], since, limit + 1)).fetchall()
        records = [{"sequence": row["sequence"], "inbox_id": row["inbox"], "event_id": row["event"],
                    "created_at": timestamp(row["created"]), "action": row["action"], "actor": row["actor"],
                    "details": json.loads(row["details"])} for row in rows[:limit]]
        return {"activity": records, "next_since": records[-1]["sequence"] if records else since,
                "has_more": len(rows) > limit}

    def record_activity(self, token: str, action: str, details: dict) -> None:
        with self.connection(write=True) as db:
            inbox = self._row(db, token)
            self._audit(db, inbox["id"], action, details=details, actor="provider")

    def create(self, expiry: int = 604800, name: str = "", config: dict | None = None) -> dict:
        if not 60 <= expiry <= 604800:
            raise InboxError("Expiry must be between 60 seconds and seven days.")
        if len(name) > 60:
            raise InboxError("Inbox names are limited to 60 characters.")
        options = ResponseSettings.model_validate(config or {}).model_dump()
        key = "ohk_" + secrets.token_urlsafe(32)
        identifier = str(uuid4())
        now = time.time()
        with self.connection(write=True) as db:
            self._expire(db)
            count = db.execute("SELECT COUNT(*) FROM inboxes").fetchone()[0]
            if count >= self.settings.inbox_limit:
                raise InboxError("Inbox capacity reached. Try again later.", 429)
            db.execute("INSERT INTO inboxes(id,key_hash,created,expires,config,name) VALUES(?,?,?,?,?,?)",
                       (identifier, token_hash(key), now, now + expiry, json.dumps(options), name))
            self._audit(db, identifier, "inbox.created", details={"expiry_seconds": expiry}, actor="client")
        return self.info(key)

    def _info(self, db, row, token: str) -> dict:
        config = json.loads(row["config"])
        config.pop("verification_secret", None)
        identifier = row["id"]
        subscription = db.execute("SELECT provider,external_id,target FROM subscriptions WHERE inbox=?", (identifier,)).fetchone()
        return {
            "token": token, "inbox_id": identifier, "name": row["name"],
            "url": f"{self.settings.origin}/h/{identifier}",
            "email": f"{identifier}@{self.settings.email_domain}" if self.settings.email_domain else None,
            "dns": f"{identifier}.{self.settings.dns_domain}" if self.settings.dns_domain else None,
            "created_at": timestamp(row["created"]), "expires_at": timestamp(row["expires"]),
            "requests_count": db.execute("SELECT COUNT(*) FROM events WHERE inbox=?", (identifier,)).fetchone()[0],
            "request_limit": self.settings.event_limit,
            "subscription": dict(subscription) if subscription else None,
            "signature_required": bool(json.loads(row["config"])["verification_secret"]), **config,
        }

    def info(self, token: str) -> dict:
        with self.connection() as db:
            return self._info(db, self._row(db, token), token)

    def public_info(self, identifier: str) -> dict:
        with self.connection() as db:
            row = self._row(db, identifier, public=True)
            if not json.loads(row["config"]).get("enabled", True):
                raise InboxError("Inbox is being provisioned. Retry shortly.", 503)
            return {"id": row["id"], **json.loads(row["config"])}

    def configure(self, token: str, changes: dict) -> dict:
        with self.connection(write=True) as db:
            row = self._row(db, token)
            config = ResponseSettings.model_validate({**json.loads(row["config"]), **changes}).model_dump()
            db.execute("UPDATE inboxes SET config=? WHERE id=?", (json.dumps(config), row["id"]))
            self._audit(db, row["id"], "inbox.configured", details={"fields": sorted(changes)})
        return self.info(token)

    def delete(self, token: str) -> dict:
        with self.connection(write=True) as db:
            row = self._row(db, token)
            count = self._delete_events(db, row["id"])
            self._audit(db, row["id"], "inbox.deleted", details={"deleted_events": count})
            db.execute("DELETE FROM inboxes WHERE id=?", (row["id"],))
        return {"deleted": True}

    def rotate(self, token: str) -> dict:
        new_token = "ohk_" + secrets.token_urlsafe(32)
        with self.connection(write=True) as db:
            row = self._row(db, token)
            db.execute("UPDATE inboxes SET key_hash=? WHERE id=?", (token_hash(new_token), row["id"]))
            self._audit(db, row["id"], "inbox.token_rotated")
        return self.info(new_token)

    def capture(self, identifier: str, body: bytes, *, kind: str = "web", method: str = "POST",
                url: str = "", headers: dict | None = None, query: dict | None = None,
                ip: str = "", source_id: str | None = None, extra: dict | None = None) -> dict:
        if len(body) > self.settings.body_limit:
            raise InboxError("Event exceeds the 1 MB limit.", 413)
        if source_id and len(source_id) > 200:
            raise InboxError("Event ID exceeds 200 characters.")
        if kind not in {"web", "email", "dns"}:
            raise InboxError("Unknown event type.")
        now = time.time()
        event = {"uuid": str(uuid4()), "type": kind, "method": method, "url": url,
                 "created_at": timestamp(now), "headers": headers or {}, "query": query or {},
                 "ip": ip, "content": body.decode("utf-8", errors="replace"),
                 "body_base64": base64.b64encode(body).decode(), "note": "", **(extra or {})}
        with self.connection(write=True) as db:
            row = self._row(db, identifier, public=True)
            if not json.loads(row["config"]).get("enabled", True):
                raise InboxError("Inbox is being provisioned. Retry shortly.", 503)
            if source_id:
                existing = db.execute("SELECT sequence,payload FROM events WHERE inbox=? AND source_id=?", (identifier, source_id)).fetchone()
                if existing:
                    self._audit(db, identifier, "event.duplicate_received", json.loads(existing["payload"])["uuid"],
                                {"type": kind, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}, actor=kind)
                    return {**json.loads(existing["payload"]), "sorting": existing["sequence"], "duplicate": True}
            pages = db.execute("PRAGMA page_count").fetchone()[0]
            free = db.execute("PRAGMA freelist_count").fetchone()[0]
            page_size = db.execute("PRAGMA page_size").fetchone()[0]
            if (pages - free) * page_size >= self.settings.storage_limit or shutil.disk_usage(self.settings.database).free < 524_288_000:
                raise InboxError("Storage capacity reached. Try again after events expire.", 429)
            if db.execute("SELECT COUNT(*) FROM events WHERE inbox=?", (identifier,)).fetchone()[0] >= self.settings.event_limit:
                raise InboxError("Inbox event capacity reached. Export or delete events before sending more.", 429)
            cursor = db.execute("INSERT INTO events(id,inbox,created,kind,payload,source_id) VALUES(?,?,?,?,?,?)",
                                (event["uuid"], row["id"], now, kind, json.dumps(event), source_id))
            event["sorting"] = cursor.lastrowid
            self._audit(db, identifier, "event.received", event["uuid"],
                        {"type": kind, "method": method, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                         "test_event": bool((extra or {}).get("test_event"))}, actor=kind, created=now)
        return event

    def requests(self, token: str, *, limit: int = 50, page: int = 1, since: int = 0,
                 request_type: str | None = None, query: str = "", oldest: bool = False, full: bool = False) -> dict:
        if not 1 <= limit <= 1000 or not 1 <= page <= 1000 or since < 0:
            raise InboxError("Invalid page, limit, or cursor.")
        if request_type not in {None, "web", "email", "dns"}:
            raise InboxError("Type must be web, email, or dns.")
        with self.connection() as db:
            row = self._row(db, token)
            where = "inbox=? AND sequence>?"
            args: list[Any] = [row["id"], since]
            if request_type:
                where += " AND kind=?"
                args.append(request_type)
            if query:
                where += " AND instr(lower(payload), lower(?))>0"
                args.append(query)
            total = db.execute(f"SELECT COUNT(*) FROM events WHERE {where}", args).fetchone()[0]
            order = "ASC" if oldest else "DESC"
            rows = db.execute(f"SELECT sequence,payload FROM events WHERE {where} ORDER BY sequence {order} LIMIT ? OFFSET ?",
                              [*args, limit, (page - 1) * limit])
            events = []
            for item in rows:
                event = {**json.loads(item["payload"]), "sorting": item["sequence"]}
                if not full:
                    event.pop("body_base64", None)
                    for field in ("content", "text_content", "url", "sender", "recipient", "subject", "note"):
                        if len(event.get(field, "")) > 2048:
                            event[field] = event[field][:2048] + "…"
                            event["preview_only"] = True
                    event["headers"] = {name[:100]: [str(value)[:256] for value in values[:4]]
                                        for name, values in list(event["headers"].items())[:32]}
                    event["query"] = {name[:100]: [str(value)[:256] for value in values[:4]]
                                      for name, values in list(event["query"].items())[:32]}
                events.append(event)
        return {"requests": events, "total_requests": total,
                "pagination": {"total": total, "page": page, "per_page": limit, "is_last_page": page * limit >= total},
                "next_since": max([event["sorting"] for event in events], default=since)}

    def request(self, token: str, request_id: str | None = None) -> dict:
        if request_id is None:
            events = self.requests(token, limit=1, full=True)["requests"]
            return {"request": events[0] if events else None}
        with self.connection() as db:
            row = self._row(db, token)
            event = db.execute("SELECT sequence,payload FROM events WHERE inbox=? AND id=?", (row["id"], request_id)).fetchone()
            if not event:
                raise InboxError("Event not found in this inbox.", 404)
            return {"request": {**json.loads(event["payload"]), "sorting": event["sequence"]}}

    def update_request(self, token: str, request_id: str, note: str) -> dict:
        if len(note) > 2000:
            raise InboxError("Notes are limited to 2000 characters.")
        with self.connection(write=True) as db:
            row = self._row(db, token)
            event = db.execute("SELECT payload FROM events WHERE inbox=? AND id=?", (row["id"], request_id)).fetchone()
            if not event:
                raise InboxError("Event not found in this inbox.", 404)
            payload = {**json.loads(event["payload"]), "note": note}
            db.execute("UPDATE events SET payload=? WHERE id=?", (json.dumps(payload), request_id))
            self._audit(db, row["id"], "event.note_updated", request_id, {"note_characters": len(note)})
        return self.request(token, request_id)

    def delete_requests(self, token: str, request_id: str | None = None) -> dict:
        with self.connection(write=True) as db:
            row = self._row(db, token)
            count = self._delete_events(db, row["id"], request_id)
        return {"deleted": count}

    async def wait(self, token: str, timeout_seconds: float = 60, request_type: str | None = None,
                   since: int | None = None, return_existing: bool = False) -> dict:
        if not 0 < timeout_seconds <= 120:
            raise InboxError("Wait timeout must be greater than zero and at most 120 seconds.")
        initial = self.requests(token, limit=1)
        cursor = since if since is not None else (0 if return_existing else initial["next_since"])
        deadline = time.monotonic() + timeout_seconds
        while True:
            result = self.requests(token, limit=1, since=cursor, request_type=request_type, oldest=True, full=True)
            if result["requests"]:
                return {"request": result["requests"][0], "next_since": result["next_since"], "timeout": False}
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return {"request": None, "next_since": cursor, "timeout": True}
            await asyncio.sleep(min(0.25, remaining))

    def links(self, token: str, request_id: str | None = None) -> dict:
        event = self.request(token, request_id)["request"]
        body = event.get("text_content", event["content"]) if event else ""
        return {"request_id": event["uuid"] if event else None,
                "links": list(dict.fromkeys(re.findall(r'https?://[^\s<>"\)]+', body))),
                "verification_codes": list(dict.fromkeys(re.findall(r"(?<!\d)\d{4,8}(?!\d)", body)))}

    def export(self, token: str):
        """Stream a consistent snapshot without loading the inbox into memory."""
        with self.connection() as db:
            db.execute("BEGIN")
            inbox = self._row(db, token)
            yield '{"requests":['
            separator = ""
            for row in db.execute("SELECT sequence,payload FROM events WHERE inbox=? ORDER BY sequence", (inbox["id"],)):
                event = {**json.loads(row["payload"]), "sorting": row["sequence"]}
                yield separator + json.dumps(event)
                separator = ","
            yield "]}"

    def attach_subscription(self, token: str, provider: str, external_id: str, target: str) -> None:
        with self.connection(write=True) as db:
            inbox = self._row(db, token)
            db.execute("INSERT INTO subscriptions(inbox,provider,external_id,target) VALUES(?,?,?,?)",
                       (inbox["id"], provider, external_id, target))
            self._audit(db, inbox["id"], "subscription.registered", details={"provider": provider, "external_id": external_id}, actor="provider")

    def detach_subscription(self, token: str) -> None:
        with self.connection(write=True) as db:
            inbox = self._row(db, token)
            row = db.execute("SELECT provider,external_id FROM subscriptions WHERE inbox=?", (inbox["id"],)).fetchone()
            if row:
                self._audit(db, inbox["id"], "subscription.removed", details=dict(row), actor="provider")
                db.execute("DELETE FROM subscriptions WHERE inbox=?", (inbox["id"],))

    def verify(self, identifier: str, body: bytes, headers: dict) -> None:
        config = self.public_info(identifier)
        secret = config["verification_secret"]
        provider = config.get("signature_provider", "generic")
        if not secret:
            if provider != "generic":
                raise InboxError("Signing secret is not configured.", 503)
            return
        if provider == "stripe":
            values = [value.strip().partition("=") for value in headers.get("stripe-signature", "").split(",")]
            sent = next((value for key, _, value in values if key == "t"), "")
            try:
                if abs(time.time() - int(sent)) > 300:
                    raise ValueError
            except ValueError:
                raise InboxError("Invalid or expired Stripe signature.", 401) from None
            expected = hmac.new(secret.encode(), sent.encode() + b"." + body, hashlib.sha256).hexdigest()
            valid = any(hmac.compare_digest(value, expected) for key, _, value in values if key == "v1")
        else:
            expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            if provider == "linear":
                valid = hmac.compare_digest(headers.get("linear-signature", ""), expected)
                if valid:
                    try:
                        valid = abs(time.time() * 1000 - float(json.loads(body)["webhookTimestamp"])) <= 60000
                    except (ValueError, KeyError, TypeError):
                        valid = False
            elif provider == "github":
                valid = hmac.compare_digest(headers.get("x-hub-signature-256", ""), "sha256=" + expected)
            else:
                valid = hmac.compare_digest(headers.get("x-openhook-signature", headers.get("x-hub-signature-256", "")), "sha256=" + expected)
        if not valid:
            raise InboxError("Invalid webhook signature.", 401)

    def set_response(self, token: str, request_id: str, status: int, content: str, content_type: str) -> dict:
        settings = ResponseSettings(default_status=status, default_content=content, default_content_type=content_type)
        with self.connection(write=True) as db:
            inbox = self._row(db, token)
            if not db.execute("SELECT 1 FROM events WHERE inbox=? AND id=?", (inbox["id"], request_id)).fetchone():
                raise InboxError("Event not found in this inbox.", 404)
            db.execute("INSERT OR REPLACE INTO responses(event,status,content,content_type) VALUES(?,?,?,?)",
                       (request_id, settings.default_status, settings.default_content, settings.default_content_type))
            self._audit(db, inbox["id"], "event.response_set", request_id,
                        {"status": status, "content_type": content_type, "content_characters": len(content)})
        return {"responded": True, "request_id": request_id}

    def response(self, request_id: str) -> dict | None:
        with self.connection() as db:
            row = db.execute("SELECT * FROM responses WHERE event=?", (request_id,)).fetchone()
            return dict(row) if row else None
