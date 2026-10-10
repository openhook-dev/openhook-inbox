"""Web inbox, native HTTP capture, and Streamable HTTP MCP on one service."""

from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from contextlib import asynccontextmanager
from html import escape
from typing import Any, Literal
from urllib.parse import urlsplit

from mcp.server.transport_security import TransportSecuritySettings
from pydantic import BaseModel, Field, ValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse, Response, StreamingResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from openhook.settings import Settings
from openhook.store import InboxError, Store
from openhook.transports import CaptureTransports
from server import build_mcp
from openhook.discovery import openapi_schema, tools_markdown
from openhook.pages import CSP, PAGES, PUBLIC_PATHS, WEB_ROOT, render_page, template


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
        return JSONResponse({"message": str(exc)}, status_code=exc.status)
    except (ValidationError, ValueError) as exc:
        return JSONResponse({"message": str(exc)}, status_code=400)


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
        return JSONResponse({"success": False, "message": str(exc)}, status_code=exc.status)
    except (ValidationError, ValueError) as exc:
        return JSONResponse({"success": False, "message": str(exc)}, status_code=400)


async def capture(request: Request) -> Response:
    store = request.app.state.store
    identifier = request.path_params["identifier"]
    try:
        config = store.public_info(identifier)
        headers = {}
        for key, value in request.headers.items():
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
        return JSONResponse({"message": str(exc)}, status_code=exc.status)


async def tools_catalog(request):
    return JSONResponse({"tools": [tool.model_dump(by_alias=True, exclude_none=True) for tool in await request.app.state.mcp.list_tools()]})


async def export_events(request):
    try:
        token = (await request.json()).get("token", "")
        request.app.state.store.info(token)
        return StreamingResponse(request.app.state.store.export(token), media_type="application/json",
                                 headers={"Content-Disposition": 'attachment; filename="openhook-events.json"'})
    except InboxError as exc:
        return JSONResponse({"message": str(exc)}, status_code=exc.status)
    except (ValueError, AttributeError):
        return JSONResponse({"message": "Invalid export request."}, status_code=400)


async def health(request):
    store = request.app.state.store
    with store.connection() as db:
        db.execute("SELECT 1").fetchone()
    return JSONResponse({"status": "ok", "product": "openhook", "version": "0.1.0", "storage": "sqlite",
                         "email": bool(store.settings.email_domain), "dns": bool(store.settings.dns_domain)})


async def page(request):
    tools = await request.app.state.mcp.list_tools() if request.url.path == "/docs" else ()
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
    return Response(f"User-agent: *\nAllow: /\nAllow: /api/tools\nDisallow: /api/\nDisallow: /h/\nDisallow: /app\nDisallow: /mcp\nDisallow: /health\nSitemap: {request.app.state.store.settings.origin}/sitemap.xml\n", media_type="text/plain")


async def sitemap(request):
    origin = request.app.state.store.settings.origin
    urls = "".join(f"<url><loc>{escape(origin + path)}</loc></url>" for path in PUBLIC_PATHS)
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', media_type="application/xml")


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
        protected = path.startswith(("/api/", "/mcp"))
        if protected and headers.get("origin") not in {None, self.settings.origin}:
            return await JSONResponse({"message": "Origin is not allowed."}, status_code=403)(scope, receive, send)
        if path.startswith(("/api/", "/mcp", "/h/")):
            now = time.monotonic()
            ip = (scope.get("client") or ("unknown",))[0]
            self.hits = {key: values for key, values in self.hits.items() if values and values[-1] > now - 60}
            if ip not in self.hits and len(self.hits) >= 10000:
                return await Response("Capacity reached", status_code=429)(scope, receive, send)
            hits = self.hits.setdefault(ip, deque())
            while hits and hits[0] <= now - 60:
                hits.popleft()
            if len(hits) >= 120:
                return await JSONResponse({"message": "Too many requests. Try again in a minute."}, status_code=429,
                                          headers={"Retry-After": "60"})(scope, receive, send)
            hits.append(now)
        if headers.get("content-length", "").isdigit() and int(headers["content-length"]) > self.settings.body_limit:
            return await Response("Request exceeds 1 MB", status_code=413)(scope, receive, send)
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
                if not any(key.lower() == b"content-security-policy" for key, _ in message["headers"]):
                    message["headers"].append((b"content-security-policy", CSP.encode()))
                if path == "/app" or path.startswith(("/h/", "/mcp", "/health")) or (path.startswith("/api/") and path != "/api/tools"):
                    message["headers"].append((b"x-robots-tag", b"noindex, nofollow"))
                if protected or path == "/app":
                    message["headers"].append((b"cache-control", b"no-store"))
                elif path.startswith("/assets/"):
                    message["headers"].append((b"cache-control", b"no-cache"))
            await send(message)

        await self.app(scope, bounded_receive, secure_send)


def create_app(settings: Settings | None = None):
    settings = settings or Settings.from_env()
    mcp = build_mcp(settings)
    security = TransportSecuritySettings(enable_dns_rebinding_protection=True,
        allowed_hosts=[urlsplit(settings.origin).netloc, "localhost:*", "127.0.0.1:*"],
        allowed_origins=[settings.origin])
    app = mcp.streamable_http_app(stateless_http=True, json_response=True, transport_security=security)
    original_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        store = Store(settings)
        application.state.store = store
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
        Route("/health", health), Route("/api/call", api_call, methods=["POST"]), Route("/api/tools", tools_catalog),
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
    return app
