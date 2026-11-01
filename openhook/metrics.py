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
    if path in {"/", "/channels", "/connect", "/docs", "/agents", "/privacy", "/api/v1/channels", "/api/v1/sessions", "/api/tools", "/api/v1/tools"}:
        return path
    for prefix in ("/mcp", "/assets/"):
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
                "channels": ("Retained channels including test activity", db.execute("SELECT COUNT(*) FROM agent_sessions").fetchone()[0]),
                "retained_messages": ("Retained messages including test activity", db.execute("SELECT COUNT(*) FROM session_events WHERE kind='message'").fetchone()[0]),
                "storage_used_bytes": ("SQLite allocated data pages excluding freelist", (db.execute("PRAGMA page_count").fetchone()[0] - db.execute("PRAGMA freelist_count").fetchone()[0]) * db.execute("PRAGMA page_size").fetchone()[0]),
                "storage_limit_bytes": ("Configured SQLite data limit", settings.storage_limit),
                "channel_limit": ("Configured shared channel limit", settings.channel_limit),
                "disk_free_bytes": ("Free disk space on the data volume", shutil.disk_usage(settings.database).free),
            }
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
