"""Public HTML for people and crawlers; JavaScript only adds interactions."""

from __future__ import annotations

import base64
import hashlib
import json
from html import escape
from pathlib import Path

from starlette.responses import HTMLResponse

WEB_ROOT = Path(__file__).parent.parent / "web"
SOURCE = "https://github.com/openhook-dev/openhook-inbox"
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
PAGES = {
    "/": ("home", "Openhook — Webhooks for AI agents", "Give your agent a public webhook URL. Test local integrations, wait for callbacks, and forward events without exposing your laptop. Open source."),
    "/connect": ("connect", "Connect your AI agent — Openhook", "Connect Claude Code, Cursor, VS Code, or a local MCP client to Openhook. Create a webhook inbox and receive your first event."),
    "/docs": ("docs", "Webhook MCP tools and API documentation — Openhook", "Create webhook inboxes, inspect payloads, wait with a cursor, and forward events locally. Live MCP tool schemas and REST API documentation."),
    "/agents": ("agents", "Webhook testing and notifications for agents — Openhook", "A practical guide for AI agents: public webhook URLs, local testing, event waits, local notifications, private tokens, and resumable delivery."),
    "/privacy": ("privacy", "Privacy and event retention — Openhook", "How Openhook stores webhook events, private management tokens, browser bookmarks, and provider credentials. Understand retention and deletion."),
    "/app": ("app", "Your webhook inboxes — Openhook", "Create a webhook inbox and inspect captured events on this device."),
}
PUBLIC_PATHS = tuple(path for path in PAGES if path != "/app")


def template(path: str, values: dict[str, str]) -> str:
    text = (WEB_ROOT / path).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def tool_rows(tools) -> str:
    rows = []
    for tool in sorted(tools, key=lambda item: item.name):
        description = tool.description or ""
        schema = escape(json.dumps(tool.input_schema, indent=2))
        rows.append(f'<article class="tool-row" id="{escape(tool.name)}">'
                    f'<h3><code>{escape(tool.name)}</code></h3><p>{escape(description)}</p>'
                    f'<details><summary>Parameters</summary><pre>{schema}</pre></details></article>')
    return "\n".join(rows)


def render_page(path: str, settings, tools=()) -> HTMLResponse:
    name, title, description = PAGES[path]
    origin = settings.origin.rstrip("/")
    canonical = origin + path
    alternate = "/docs.md" if path == "/docs" else "/agents.md" if path == "/agents" else "/llms.txt"
    alternate_type = "text/markdown" if alternate.endswith(".md") else "text/plain"
    values = {"origin": escape(origin), "title": escape(title), "description": escape(description),
              "canonical": escape(canonical), "alternate": alternate, "alternate_type": alternate_type,
              "event_limit": str(settings.event_limit), "body_limit": str(settings.body_limit),
              "tool_count": str(len(tools)), "tools": tool_rows(tools)}
    values["content"] = template(f"pages/{name}.html", values)
    values["robots"] = "noindex, nofollow" if path == "/app" else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    values["structured_data"] = ""
    csp = CSP
    if path != "/app":
        graph = [
            {"@type": "Organization", "@id": origin + "/#organization", "name": "Openhook", "url": origin + "/",
             "logo": {"@type": "ImageObject", "url": origin + "/assets/organization-logo.png", "width": 460, "height": 460},
             "sameAs": ["https://github.com/openhook-dev"]},
            {"@type": "WebSite", "@id": origin + "/#website", "name": "Openhook", "url": origin + "/", "inLanguage": "en",
             "publisher": {"@id": origin + "/#organization"}},
            {"@type": "SoftwareApplication", "@id": origin + "/#software", "name": "Openhook", "url": origin + "/",
             "description": PAGES["/"][2], "applicationCategory": "DeveloperApplication", "operatingSystem": "Web, Linux, macOS, Windows",
             "license": "https://opensource.org/license/mit", "isAccessibleForFree": True,
             "publisher": {"@id": origin + "/#organization"}},
            {"@type": "SoftwareSourceCode", "@id": origin + "/#source", "name": "Openhook source code",
             "codeRepository": SOURCE, "programmingLanguage": "Python", "license": "https://opensource.org/license/mit",
             "targetProduct": {"@id": origin + "/#software"}},
            {"@type": "WebPage", "@id": canonical + "#page", "url": canonical, "name": title, "description": description,
             "inLanguage": "en", "isPartOf": {"@id": origin + "/#website"}, "about": {"@id": origin + "/#software"}},
        ]
        if path != "/":
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Openhook", "item": origin + "/"},
                {"@type": "ListItem", "position": 2, "name": title.split(" — ")[0], "item": canonical},
            ]})
        data = json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")).replace("<", "\\u003c")
        digest = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()
        csp = CSP.replace("script-src 'self'", f"script-src 'self' 'sha256-{digest}'")
        values["structured_data"] = f'<script type="application/ld+json">{data}</script>'
    headers = {"Content-Security-Policy": csp}
    if path != "/app":
        headers["Cache-Control"] = "no-cache"
        headers["Link"] = f'<{origin}{alternate}>; rel="alternate"; type="{alternate_type}", <{origin}/openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"'
    return HTMLResponse(template("index.html", values), headers=headers)
