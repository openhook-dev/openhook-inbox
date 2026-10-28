"""Bounded, aggregate telemetry. Never use user input or identifiers as labels."""

from __future__ import annotations

import functools
import hmac
import inspect
import shutil
import time
from typing import get_type_hints

from prometheus_client import Counter, Histogram, CollectorRegistry, generate_latest
from prometheus_client.core import GaugeMetricFamily
from starlette.responses import Response


REGISTRY = CollectorRegistry()
HTTP_REQUESTS = Counter("openhook_http_requests_total", "Completed HTTP requests", ["route", "method", "status"], registry=REGISTRY)
HTTP_DURATION = Histogram("openhook_http_request_duration_seconds", "HTTP duration including long polls", ["route"],
                          buckets=(.01, .05, .1, .25, .5, 1, 2, 5, 15, 30, 60, 120), registry=REGISTRY)
TOOL_CALLS = Counter("openhook_mcp_tool_calls_total", "MCP tool executions", ["tool", "outcome"], registry=REGISTRY)
CAPTURES = Counter("openhook_captured_events_total", "New committed events; excludes duplicate deliveries", ["transport", "traffic"], registry=REGISTRY)
INBOXES = Counter("openhook_created_inboxes_total", "New inboxes", ["plan"], registry=REGISTRY)


def measured_tool(function):
    """Count actual MCP errors, which may be transported with HTTP 200."""
    def record(outcome):
        TOOL_CALLS.labels(function.__name__, outcome).inc()

    if inspect.iscoroutinefunction(function):
        @functools.wraps(function)
        async def wrapped(*args, **kwargs):
            try:
                result = await function(*args, **kwargs)
            except Exception:
                record("error")
                raise
            record("success")
            return result
    else:
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
            except Exception:
                record("error")
                raise
            record("success")
            return result
    wrapped.__annotations__ = get_type_hints(function)
    return wrapped


def route_group(path):
    if path in {"/", "/connect", "/docs", "/agents", "/privacy", "/pricing", "/app", "/account",
                "/sessions", "/api/v1/sessions", "/api/call", "/api/wait", "/api/export", "/api/tools", "/api/account",
                "/auth/github", "/auth/github/callback", "/api/account/billing/checkout", "/api/account/billing/portal"}:
        return path
    for prefix in ("/mcp", "/h/", "/assets/", "/api/account/", "/billing/", "/auth/"):
        if path.startswith(prefix):
            return prefix.rstrip("/")
    return "other"


class RequestMetrics:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] in {"/metrics", "/health"}:
            return await self.app(scope, receive, send)
        start = time.monotonic()
        status = 500
        route = route_group(scope["path"])
        method = scope["method"] if scope["method"] in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"} else "OTHER"

        async def observed_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        finally:
            HTTP_REQUESTS.labels(route, method, str(status)).inc()
            HTTP_DURATION.labels(route).observe(time.monotonic() - start)


class StoreMetrics:
    def __init__(self, store):
        self.store = store

    def collect(self):
        settings = self.store.settings
        with self.store.connection() as db:
            values = {
                "inboxes": ("Currently retained inboxes", db.execute("SELECT COUNT(*) FROM inboxes").fetchone()[0]),
                "retained_events": ("Currently retained events, including test traffic", db.execute("SELECT COUNT(*) FROM events").fetchone()[0]),
                "storage_used_bytes": ("SQLite allocated data pages excluding freelist", (db.execute("PRAGMA page_count").fetchone()[0] - db.execute("PRAGMA freelist_count").fetchone()[0]) * db.execute("PRAGMA page_size").fetchone()[0]),
                "storage_limit_bytes": ("Configured SQLite data limit", settings.storage_limit),
                "inbox_limit": ("Configured shared inbox limit", settings.inbox_limit),
                "disk_free_bytes": ("Free disk space on the data volume", shutil.disk_usage(settings.database).free),
            }
            if settings.hosted_enabled:
                values["accounts"] = ("Registered hosted accounts", db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0])
                values["paid_accounts"] = ("Accounts with current paid access, not MRR", db.execute("SELECT COUNT(*) FROM hosted_entitlements WHERE paid_until>?", (time.time(),)).fetchone()[0])
        for name, (description, value) in values.items():
            yield GaugeMetricFamily("openhook_" + name, description, value=value)


async def metrics_response(request):
    store = request.app.state.store
    token = store.settings.metrics_token
    headers = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow"}
    if not token:
        return Response(status_code=404, headers=headers)
    if not hmac.compare_digest(request.headers.get("authorization", "").encode(), ("Bearer " + token).encode()):
        return Response(status_code=401, headers={**headers, "WWW-Authenticate": "Bearer"})
    # Per-scrape registry avoids sharing database handles between deployments/tests.
    registry = CollectorRegistry()
    registry.register(StoreMetrics(store))
    return Response(generate_latest(REGISTRY) + generate_latest(registry),
                    media_type="text/plain; version=0.0.4; charset=utf-8", headers=headers)
