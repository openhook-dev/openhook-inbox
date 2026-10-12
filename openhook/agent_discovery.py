"""Public discovery documents describing the interfaces actually served here."""

import hashlib

from mcp.types import LATEST_PROTOCOL_VERSION
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from openhook.pages import template


def skill_text(settings):
    return template("skill.md", {"origin": settings.origin, "event_limit": str(settings.event_limit), "body_limit": str(settings.body_limit)})


def server_manifest(settings):
    origin = settings.origin
    return {"$schema": "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json",
            "name": "io.github.openhook-dev/openhook-inbox", "title": "Openhook", "version": "0.1.0",
            "description": "Public capture addresses and private webhook, email and DNS inboxes for AI agents.",
            "websiteUrl": origin, "repository": {"source": "github", "url": "https://github.com/openhook-dev/openhook-inbox"},
            "icons": [{"src": origin + "/assets/organization-logo.png", "mimeType": "image/png", "sizes": ["460x460"]}],
            "remotes": [{"type": "streamable-http", "url": origin + "/mcp"}]}


async def discovery_document(request):
    settings = request.app.state.store.settings
    origin, path = settings.origin, request.url.path
    media_type = "application/json"
    if path.endswith("SKILL.md"):
        return Response(skill_text(settings), media_type="text/markdown")
    if path == "/.well-known/agent-skills/index.json":
        content = {"$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json", "skills": [{
            "name": "openhook", "type": "skill-md", "description": "Receive and inspect webhook events, test local integrations, or resume a running agent after a callback.",
            "url": origin + "/.well-known/agent-skills/openhook/SKILL.md",
            "digest": "sha256:" + hashlib.sha256(skill_text(settings).encode()).hexdigest()}]}
    elif path == "/.well-known/api-catalog":
        media_type = "application/linkset+json"
        content = {"linkset": [{"anchor": origin + "/api/v1/call", "service-desc": [{"href": origin + "/openapi.json", "type": "application/vnd.oai.openapi+json"}],
                               "service-doc": [{"href": origin + "/docs", "type": "text/html"}]}]}
    elif path == "/.well-known/ai-catalog.json":
        media_type = "application/ai-catalog+json"
        content = {"specVersion": "1.0", "entries": [{"identifier": "urn:air:" + origin.split("://", 1)[-1] + ":mcp:openhook",
                    "type": "application/mcp-server-card+json", "url": origin + "/.well-known/mcp/server-card.json"}]}
    else:
        content = server_manifest(settings)
        if path != "/server.json":
            media_type = "application/mcp-server-card+json"
            content["$schema"] = "https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json"
            content["remotes"][0]["supportedProtocolVersions"] = [LATEST_PROTOCOL_VERSION]
    return JSONResponse(content, media_type=media_type, headers={"Cache-Control": "no-cache"})


ROUTES = [Route(path, discovery_document) for path in (
    "/server.json", "/.well-known/mcp/server-card.json", "/mcp/server-card", "/.well-known/ai-catalog.json",
    "/.well-known/api-catalog", "/.well-known/agent-skills/index.json", "/.well-known/agent-skills/openhook/SKILL.md")]
