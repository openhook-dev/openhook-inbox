"""Web inbox, native HTTP capture, and Streamable HTTP MCP on one service."""

from __future__ import annotations

import asyncio
import json
import time
import math
import re
from collections import deque
from contextlib import asynccontextmanager
from html import escape
from typing import Any, Literal
from urllib.parse import urlsplit

from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, Field, ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response, StreamingResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.transports import CaptureTransports
from server import build_mcp
from openhook.discovery import openapi_schema, tools_markdown
from openhook.pages import CSP, PAGES, PUBLIC_PATHS, PRIVATE_PATHS, WEB_ROOT, render_page, template, markdown_page, prefers_markdown
from openhook.accounts import Accounts
from openhook.metrics import RequestMetrics, metrics_response
from openhook.http_errors import http_error, problem
from openhook.agent_discovery import ROUTES as DISCOVERY_ROUTES


class WebCall(BaseModel):
    action: Literal["create", "info", "list", "get", "send", "configure", "export", "links", "delete", "rotate", "activity"]
    token: str = ""
    request_id: str | None = None
    page: int = Field(default=1, ge=1, le=1000)
    since: int = Field(default=0, ge=0)
    limit: int = Field(default=100, ge=1, le=1000)
    payload: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)


class WaitCall(BaseModel):
    token: str
    since: int = Field(default=0, ge=0)
    timeout_seconds: float = Field(default=25, gt=0, le=30)


async def wait_events(request):
    try:
        call = WaitCall.model_validate(await request.json())
        result = await request.app.state.store.wait(call.token, call.timeout_seconds, since=call.since)
        return JSONResponse({"success": True, "data": result})
    except InboxError as exc:
        return problem(exc.status, str(exc))
    except (ValidationError, ValueError):
        return problem(400, "Invalid request fields. Check /openapi.json.")


async def api_call(request: Request) -> Response:
    store = request.app.state.store
    try:
        call = WebCall.model_validate(await request.json())
        if call.action == "create":
            result = store.create()
        elif call.action == "info":
            result = store.info(call.token)
        elif call.action == "list":
            result = store.requests(call.token, page=call.page)
        elif call.action == "get":
            result = store.request(call.token, call.request_id)
        elif call.action == "send":
            inbox = store.info(call.token)
            event = store.capture(inbox["inbox_id"], json.dumps(call.payload).encode(), url=inbox["url"],
                                  headers={"content-type": ["application/json"]}, extra={"test_event": True})
            result = {"sent": 1, "request": event}
        elif call.action == "configure":
            result = store.configure(call.token, call.config)
        elif call.action == "links":
            result = store.links(call.token, call.request_id)
        elif call.action == "delete":
            result = store.delete(call.token)
        elif call.action == "rotate":
            result = store.rotate(call.token)
        elif call.action == "activity":
            result = store.activity(call.token, since=call.since, limit=call.limit)
        else:
            result = store.requests(call.token, limit=1000, oldest=True)
        return JSONResponse({"success": True, "data": result})
    except InboxError as exc:
        return problem(exc.status, str(exc))
    except (ValidationError, ValueError):
        return problem(400, "Invalid request fields. Check /openapi.json.")


async def capture(request: Request) -> Response:
    store = request.app.state.store
    identifier = request.path_params["identifier"]
    try:
        config = store.public_info(identifier)
        headers = {}
        for key, value in request.headers.items():
            # A public capture URL may belong to someone else. Never let a visit
            # copy the browser's hosted login cookie into that person's inbox.
            if key.lower() == "cookie":
                continue
            headers.setdefault(key.lower(), []).append(value)
        cors = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*"} if config["cors"] else {}
        if request.method == "OPTIONS" and config["cors"]:
            return Response(status_code=204, headers=cors)
        body = await request.body()
        store.verify(identifier, body, dict(request.headers))
        query = {key: request.query_params.getlist(key) for key in request.query_params}
        # Source IDs are opt-in; unlabelled identical bodies remain separate events.
        source_id = request.headers.get("idempotency-key", request.headers.get("x-github-delivery", request.headers.get("linear-delivery")))
        if config.get("signature_provider") == "stripe":
            try:
                source_id = json.loads(body).get("id")
            except (ValueError, AttributeError):
                raise InboxError("Invalid Stripe event body.") from None
        event = store.capture(identifier, body, method=request.method, url=str(request.url), headers=headers,
                              query=query, ip=request.client.host if request.client else "", source_id=source_id)
        if query.get("openhook_wait") == ["1"]:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                answer = store.response(event["uuid"])
                if answer:
                    return Response(answer["content"], status_code=answer["status"], media_type=answer["content_type"], headers=cors)
                if await request.is_disconnected():
                    return Response(status_code=204)
                await asyncio.sleep(0.1)
        return Response(config["default_content"], status_code=config["default_status"],
                        media_type=config["default_content_type"], headers={**cors, "X-Openhook-Event": event["uuid"],
                                                                          "Cache-Control": "no-store"})
    except InboxError as exc:
        return problem(exc.status, str(exc))


async def tools_catalog(request):
    return JSONResponse({"tools": [tool.model_dump(by_alias=True, exclude_none=True) for tool in await request.app.state.mcp.list_tools()]})


async def export_events(request):
    try:
        token = (await request.json()).get("token", "")
        request.app.state.store.info(token)
        return StreamingResponse(request.app.state.store.export(token), media_type="application/json",
                                 headers={"Content-Disposition": 'attachment; filename="openhook-events.json"'})
    except InboxError as exc:
        return problem(exc.status, str(exc))
    except (ValueError, AttributeError):
        return problem(400, "Invalid export request.")


async def health(request):
    store = request.app.state.store
    with store.connection() as db:
        db.execute("SELECT 1").fetchone()
    return JSONResponse({"status": "ok", "product": "openhook", "version": "0.1.0", "storage": "sqlite",
                         "email": bool(store.settings.email_domain), "dns": bool(store.settings.dns_domain)})


async def page(request):
    if request.url.path == "/account" and not request.app.state.store.settings.hosted_enabled:
        raise HTTPException(404)
    tools = await request.app.state.mcp.list_tools() if request.url.path == "/docs" else ()
    if request.url.path not in PRIVATE_PATHS and prefers_markdown(request.headers.get("accept", "")):
        return markdown_page(request.url.path, request.app.state.store.settings, tools)
    return render_page(request.url.path, request.app.state.store.settings, tools)


async def llms(request):
    settings = request.app.state.store.settings
    values = {"origin": settings.origin, "event_limit": str(settings.event_limit), "body_limit": str(settings.body_limit)}
    path = request.url.path
    if path == "/docs.md":
        text = tools_markdown(await request.app.state.mcp.list_tools())
    elif path == "/llms-full.txt":
        text = template("agent-guide.md", values) + "\n\n" + tools_markdown(await request.app.state.mcp.list_tools())
    else:
        text = template({"/llms.txt": "llms.txt", "/agents.md": "agent-guide.md", "/skill.md": "skill.md"}[path], values)
    return Response(text, media_type="text/markdown" if path.endswith(".md") else "text/plain")


async def openapi(request):
    return JSONResponse(openapi_schema(request.app.state.store.settings.origin, WebCall, WaitCall))


async def robots(request):
    return Response(f"User-agent: *\nAllow: /\nAllow: /api/tools\nAllow: /api/v1/tools\nDisallow: /api/\nDisallow: /h/\nDisallow: /app\nDisallow: /account\nDisallow: /auth/\nDisallow: /billing/\nDisallow: /mcp\nDisallow: /health\nDisallow: /metrics\nSitemap: {request.app.state.store.settings.origin}/sitemap.xml\n", media_type="text/plain")


async def sitemap(request):
    origin = request.app.state.store.settings.origin
    urls = "".join(f"<url><loc>{escape(origin + path)}</loc></url>" for path in PUBLIC_PATHS)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', media_type="application/xml")


def rate_limit_headers(remaining: int, reset: int) -> dict[str, str]:
    return {"RateLimit-Policy": '"default";q=120;w=60',
            "RateLimit": f'"default";r={remaining};t={reset}',
            "RateLimit-Limit": "120", "RateLimit-Remaining": str(remaining), "RateLimit-Reset": str(reset)}


class WebBoundary:
    def __init__(self, app, settings: Settings):
        self.app = app
        self.settings = settings
        self.hits: dict[str, deque] = {}

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope["path"]
        headers = {key.decode().lower(): value.decode() for key, value in scope["headers"]}
        if headers.get("host") == "www." + urlsplit(self.settings.origin).netloc:
            query = scope.get("query_string", b"").decode()
            target = self.settings.origin + path + ("?" + query if query else "")
            return await RedirectResponse(target, status_code=308)(scope, receive, send)
        if scope["method"] in {"GET", "HEAD"}:
            canonical_path = path.rstrip("/")
            if path.endswith("/") and canonical_path in PUBLIC_PATHS:
                query = scope.get("query_string", b"").decode()
                target = canonical_path + ("?" + query if query else "")
                return await RedirectResponse(target, status_code=308)(scope, receive, send)
            # Old indexed account links now lead to the current sign-in/access flow.
            if self.settings.hosted_enabled and path in {"/signup", "/login", "/dashboard", "/settings", "/settings/api-keys"}:
                return await RedirectResponse("/account", status_code=308)(scope, receive, send)
        protected = path.startswith(("/api/", "/mcp"))
        if protected and headers.get("origin") not in {None, self.settings.origin}:
            return await problem(403, "Origin is not allowed.")(scope, receive, send)
        rate_headers = {}
        if path.startswith(("/api/", "/mcp", "/h/", "/auth/")):
            now = time.monotonic()
            ip = (scope.get("client") or ("unknown",))[0]
            self.hits = {key: values for key, values in self.hits.items() if values and values[-1] > now - 60}
            if ip not in self.hits and len(self.hits) >= 10000:
                return await problem(429, "Capacity reached", headers={"Retry-After": "60"})(scope, receive, send)
            hits = self.hits.setdefault(ip, deque())
            while hits and hits[0] <= now - 60:
                hits.popleft()
            reset = max(1, math.ceil(hits[0] + 60 - now)) if hits else 60
            if len(hits) >= 120:
                return await problem(429, "Too many requests. Try again in a minute.",
                    headers={**rate_limit_headers(0, reset), "Retry-After": str(reset)})(scope, receive, send)
            hits.append(now)
            rate_headers = rate_limit_headers(120 - len(hits), reset)
        if headers.get("content-length", "").isdigit() and int(headers["content-length"]) > self.settings.body_limit:
            return await problem(413, "Request exceeds 1 MB", headers=rate_headers)(scope, receive, send)
        body_size = 0

        async def bounded_receive():
            nonlocal body_size
            message = await receive()
            body_size += len(message.get("body", b""))
            if body_size > self.settings.body_limit:
                raise HTTPException(413, "Request exceeds 1 MB")
            return message

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend([
                    (b"x-content-type-options", b"nosniff"), (b"referrer-policy", b"no-referrer"),
                ])
                message["headers"].extend((key.lower().encode(), value.encode()) for key, value in rate_headers.items())
                if path.startswith("/h/"):
                    # Inbox owners control response bodies and content types.
                    # Their HTML must never execute with the account UI's origin.
                    message["headers"].append((b"content-security-policy", b"sandbox; default-src 'none'; frame-ancestors 'none'"))
                elif not any(key.lower() == b"content-security-policy" for key, _ in message["headers"]):
                    message["headers"].append((b"content-security-policy", CSP.encode()))
                if path in {"/app", "/account"} or path.startswith(("/h/", "/mcp", "/health", "/auth/")) or (path.startswith("/api/") and path != "/api/tools"):
                    message["headers"].append((b"x-robots-tag", b"noindex, nofollow"))
                if protected or path in {"/app", "/account"} or path.startswith("/auth/"):
                    message["headers"].append((b"cache-control", b"no-store"))
                elif path.startswith("/assets/"):
                    versioned = re.fullmatch(rb"v=[0-9a-f]{12}", scope.get("query_string", b""))
                    policy = b"public, max-age=31536000, immutable" if versioned and message["status"] in {200, 304} else b"no-cache"
                    message["headers"].append((b"cache-control", policy))
            await send(message)

        await self.app(scope, bounded_receive, secure_send)


class PublicCompression:
    """Compress public documents/assets; never buffer MCP or private responses."""

    def __init__(self, app):
        self.app = app
        self.compressed = GZipMiddleware(app, minimum_size=1000, compresslevel=5)

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        public = path in PUBLIC_PATHS or path.startswith("/assets/") or path in {
            "/sitemap.xml", "/openapi.json", "/llms.txt", "/llms-full.txt", "/agents.md", "/docs.md", "/skill.md"}
        app = self.compressed if scope["type"] == "http" and public else self.app
        await app(scope, receive, send)


def create_app(settings: Settings | None = None, *, hosted_routes=()):
    settings = settings or Settings.from_env()
    if settings.metrics_token and len(settings.metrics_token) < 32:
        raise ValueError("OPENHOOK_METRICS_TOKEN must have at least 32 characters.")
    mcp = build_mcp(settings)
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True,
        allowed_hosts=[urlsplit(settings.origin).netloc, "localhost:*", "127.0.0.1:*"],
        allowed_origins=[settings.origin])
    app = mcp.streamable_http_app(stateless_http=True, json_response=True, transport_security=security)
    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(500, http_error)
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        store = Store(settings)
        application.state.store = store
        application.state.accounts = Accounts(store) if settings.hosted_enabled else None
        application.state.mcp = mcp
        transports = CaptureTransports(store)
        await transports.start()
        async def maintain():
            while True:
                store.cleanup()
                await asyncio.sleep(60)
        cleanup = asyncio.create_task(maintain())
        try:
            async with original_lifespan(application):
                yield
        finally:
            cleanup.cancel()
            await asyncio.gather(cleanup, return_exceptions=True)
            await transports.stop()

    app.router.lifespan_context = lifespan
    app.router.routes.extend([
        *DISCOVERY_ROUTES,
        *hosted_routes,
        Route("/api/v1/call", api_call, methods=["POST"]), Route("/api/v1/wait", wait_events, methods=["POST"]),
        Route("/api/v1/export", export_events, methods=["POST"]), Route("/api/v1/tools", tools_catalog),
        Route("/health", health), Route("/metrics", metrics_response), Route("/api/call", api_call, methods=["POST"]), Route("/api/tools", tools_catalog),
        Route("/api/export", export_events, methods=["POST"]),
        Route("/api/wait", wait_events, methods=["POST"]),
        Route("/h/{identifier}", capture, methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
        Route("/h/{identifier}/{rest:path}", capture, methods=["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]),
        Route("/robots.txt", robots), Route("/sitemap.xml", sitemap),
        *[Route(path, llms) for path in ("/llms.txt", "/llms-full.txt", "/agents.md", "/docs.md", "/skill.md")],
        Route("/openapi.json", openapi), *[Route(path, page) for path in PAGES],
        Mount("/assets", StaticFiles(directory=WEB_ROOT / "assets")),
    ])
    app.add_middleware(WebBoundary, settings=settings)
    app.add_middleware(PublicCompression)
    app.add_middleware(RequestMetrics)
    return app
