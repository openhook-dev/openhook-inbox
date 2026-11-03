"""Private channels through HTTP and MCP, with a small browser handoff."""

from __future__ import annotations

import asyncio
import time
import math
import re
from collections import deque
from contextlib import asynccontextmanager
from html import escape
from urllib.parse import urlsplit

from mcp.server.transport_security import TransportSecuritySettings
from starlette.exceptions import HTTPException
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from openhook.settings import Settings
from openhook.store import Store
from server import build_mcp
from openhook.discovery import openapi_schema, tools_markdown
from openhook.pages import CSP, PAGES, PUBLIC_PATHS, PRIVATE_PATHS, WEB_ROOT, render_page, template, markdown_page, prefers_markdown
from openhook.metrics import RequestMetrics, metrics_response
from openhook.http_errors import http_error, problem
from openhook.agent_discovery import ROUTES as DISCOVERY_ROUTES
from openhook.session_api import ChannelCall, session_call


async def tools_catalog(request):
    return JSONResponse({"tools": [tool.model_dump(by_alias=True, exclude_none=True) for tool in await request.app.state.mcp.list_tools()]})


async def health(request):
    store = request.app.state.store
    with store.connection() as db:
        db.execute("SELECT 1").fetchone()
    return JSONResponse({"status": "ok", "product": "openhook", "version": "0.2.0", "storage": "sqlite"})


async def page(request):
    tools = await request.app.state.mcp.list_tools() if request.url.path == "/docs" else ()
    if request.url.path not in PRIVATE_PATHS and prefers_markdown(request.headers.get("accept", "")):
        return markdown_page(request.url.path, request.app.state.store.settings, tools)
    return render_page(request.url.path, request.app.state.store.settings, tools)


async def llms(request):
    settings = request.app.state.store.settings
    values = {"origin": settings.origin}
    path = request.url.path
    if path == "/docs.md":
        text = tools_markdown(await request.app.state.mcp.list_tools())
    elif path == "/llms-full.txt":
        text = template("agent-skill.md", values) + "\n\n" + tools_markdown(await request.app.state.mcp.list_tools())
    else:
        text = template({"/llms.txt": "llms.txt", "/agents.md": "agent-skill.md", "/skill.md": "agent-skill.md"}[path], values)
    return Response(text, media_type="text/markdown" if path.endswith(".md") else "text/plain")


async def openapi(request):
    return JSONResponse(openapi_schema(request.app.state.store.settings.origin, ChannelCall))


async def robots(request):
    private = ''.join(f'Disallow: {path}\n' for path in sorted(PRIVATE_PATHS))
    return Response(f"User-agent: *\nAllow: /\nAllow: /api/tools\nAllow: /api/v1/tools\nDisallow: /api/\n{private}Disallow: /mcp\nDisallow: /health\nDisallow: /metrics\nSitemap: {request.app.state.store.settings.origin}/sitemap.xml\n", media_type="text/plain")


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
        self.inflight: dict[str, int] = {}
        self.active = 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope["path"]
        headers = {key.decode('latin-1').lower(): value.decode('latin-1') for key, value in scope["headers"]}
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
        protected = path.startswith(("/api/", "/mcp"))
        if protected and (headers.get("origin") not in {None, self.settings.origin}
                          or headers.get("sec-fetch-site") == "cross-site"):
            return await problem(403, "Origin is not allowed.")(scope, receive, send)
        host = headers.get("host", "")
        configured_host = urlsplit(self.settings.origin).netloc
        local_host = host.split(":", 1)[0] in {"localhost", "127.0.0.1"}
        allow_local = urlsplit(self.settings.origin).hostname in {"localhost", "127.0.0.1", "::1"}
        if protected and host != configured_host and not (allow_local and local_host):
            return await problem(403, "Host is not allowed.")(scope, receive, send)
        rate_headers = {}
        if path.startswith(("/api/", "/mcp")):
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

        async def rate_limited_send(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", []).extend(
                    (key.lower().encode(), value.encode()) for key, value in rate_headers.items())
            await send(message)

        # Bound long polls and other in-flight requests, not just request starts.
        if protected:
            if self.active >= 128 or self.inflight.get(ip, 0) >= 16:
                return await problem(429, "Too many concurrent requests.",
                    headers={"Retry-After": "5"})(scope, receive, rate_limited_send)
            self.active += 1
            self.inflight[ip] = self.inflight.get(ip, 0) + 1
        try:
            await self.app(scope, bounded_receive, rate_limited_send)
        finally:
            if protected:
                self.active -= 1
                self.inflight[ip] -= 1
                if not self.inflight[ip]:
                    del self.inflight[ip]


class ResponseSecurity:
    """Apply security policy to successful responses, redirects and boundary errors."""

    def __init__(self, app, settings):
        self.app, self.settings = app, settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope["path"]
        private = path in PRIVATE_PATHS or path.startswith(("/api/", "/mcp", "/metrics"))

        async def secure_send(message):
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                headers.extend([
                    (b"x-content-type-options", b"nosniff"), (b"referrer-policy", b"no-referrer"),
                    (b"x-frame-options", b"DENY"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), payment=(), usb=()"),
                ])
                if urlsplit(self.settings.origin).scheme == "https":
                    headers.append((b"strict-transport-security", b"max-age=31536000"))
                if not any(key.lower() == b"content-security-policy" for key, _ in headers):
                    headers.append((b"content-security-policy", CSP.encode()))
                if private or path.startswith("/health"):
                    headers.append((b"x-robots-tag", b"noindex, nofollow"))
                if private:
                    headers[:] = [(key, value) for key, value in headers if key.lower() != b"cache-control"]
                    headers.extend([(b"cache-control", b"no-store"),
                                    (b"cross-origin-resource-policy", b"same-origin")])
                elif path.startswith("/assets/"):
                    versioned = re.fullmatch(rb"v=[0-9a-f]{12}", scope.get("query_string", b""))
                    policy = b"public, max-age=31536000, immutable" if versioned and message["status"] in {200, 304} else b"no-cache"
                    headers.append((b"cache-control", policy))
            await send(message)

        await self.app(scope, receive, secure_send)


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


def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    if settings.metrics_token and len(settings.metrics_token) < 32:
        raise ValueError("OPENHOOK_METRICS_TOKEN must have at least 32 characters.")
    mcp = build_mcp(settings)
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True,
        allowed_hosts=[urlsplit(settings.origin).netloc] + (
            ["localhost:*", "127.0.0.1:*"] if urlsplit(settings.origin).hostname in {"localhost", "127.0.0.1", "::1"} else []),
        allowed_origins=[settings.origin])
    app = mcp.streamable_http_app(stateless_http=True, json_response=True, transport_security=security)
    app.add_exception_handler(HTTPException, http_error)
    app.add_exception_handler(500, http_error)
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        store = Store(settings)
        application.state.store = store
        application.state.mcp = mcp
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

    app.router.lifespan_context = lifespan
    app.router.routes.extend([
        *DISCOVERY_ROUTES,
        # Old conversation clients retain access to existing keys through this alias.
        Route("/api/v1/sessions", session_call, methods=["POST"]),
        Route("/sessions", lambda request: RedirectResponse("/channels", status_code=308)),
        Route("/api/v1/channels", session_call, methods=["POST"]),
        Route("/api/v1/tools", tools_catalog), Route("/api/tools", tools_catalog),
        Route("/health", health), Route("/metrics", metrics_response),
        Route("/robots.txt", robots), Route("/sitemap.xml", sitemap),
        *[Route(path, llms) for path in ("/llms.txt", "/llms-full.txt", "/agents.md", "/docs.md", "/skill.md")],
        Route("/openapi.json", openapi), *[Route(path, page) for path in PAGES],
        Mount("/assets", StaticFiles(directory=WEB_ROOT / "assets")),
    ])
    app.add_middleware(WebBoundary, settings=settings)
    app.add_middleware(PublicCompression)
    app.add_middleware(RequestMetrics)
    app.add_middleware(ResponseSecurity, settings=settings)
    return app
