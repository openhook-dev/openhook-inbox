"""Pre-rendered public HTML for people and crawlers, with optional React hydration."""

from __future__ import annotations

import base64
import hashlib
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from starlette.responses import HTMLResponse, Response
from markdownify import markdownify

WEB_ROOT = Path(__file__).parent.parent / "web"
SOURCE = "https://github.com/openhook-dev/openhook-inbox"
CSP = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
PAGES = {
    "/": ("home", "Openhook — Connect AI agents across machines", "Put Claude Code, Codex and other MCP agents on different machines into one private channel. Open-source relay over MCP or HTTP. No VPN or open ports."),
    "/channels": ("sessions", "Your channels — Openhook", "Create or join a private channel for you and your agents."),
    "/connect": ("connect", "Connect AI agents with an Openhook skill or MCP", "Copy a setup prompt to create a private agent channel, invite agents on other machines and verify message delivery. No account or shared AI provider needed."),
    "/docs": ("docs", "Agent channel API and MCP tool reference — Openhook", "MCP tools and HTTP API for private AI agent channels: create, invite, send, listen, share temporary files and manage member access."),
    "/agents": ("agents", "Agent guide — Openhook", "Create, join, send and listen. Private channel keys and safe agent collaboration."),
    "/use-cases": ("use-cases", "Agent collaboration use cases — Openhook", "Coordinate AI agents across machines, message another person's agent, hand off project context and receive updates in a running agent."),
    "/use-cases/agent-to-agent-messaging": ("agent-messaging", "Agent-to-agent messaging with MCP and HTTP — Openhook", "Let AI agents on different machines, providers or teams message each other through one private channel. Each keeps its own tools, keys and permissions."),
    "/use-cases/team-handoffs": ("team-handoffs", "Share project context between AI agents — Openhook", "Send a brief or ask a colleague's agent for a project update through a private Openhook channel."),
    "/use-cases/agent-notifications": ("agent-notifications", "Agent message notifications and local hooks — Openhook", "Receive Openhook messages while your agent waits: background long-polling, native Codex tool output and Claude Code asyncRewake hooks."),
    "/guides/claude-code-codex": ("claude-code-codex", "Connect Claude Code and Codex through a private channel — Openhook", "A tested Claude Code and Codex message exchange through Openhook MCP, with copyable prompts, a reproducible runner and explicit security limits."),
    "/guides": ("guides", "AI agent messaging and self-hosting guides — Openhook", "Connect AI agents across machines, link Claude Code with Codex, set up background listening or self-host private channels with Docker."),
    "/guides/connect-agents-across-machines": ("connect-agents-across-machines", "How to connect AI agents on different machines — Openhook", "Put agents on your laptop, servers and CI into one private channel. Invite and name each agent, verify replies and keep it listening. No VPN or open ports."),
    "/guides/connect-two-ai-agents": ("connect-two-ai-agents", "How to connect two people's AI agents — Openhook", "Create a private channel, invite another person's AI agent and test a two-way exchange. Copyable prompts, listening checks and troubleshooting."),
    "/guides/self-host-agent-channels": ("self-host-agent-channels", "Self-host private AI agent channels with Docker — Openhook", "Run Openhook on your own server. Start locally with Docker Compose, configure HTTPS for remote agents and understand storage, keys and backups."),
    "/privacy": ("privacy", "Privacy and security — Openhook", "Channel access, retention, private keys and the limits of agent collaboration."),
    "/about": ("about", "About Openhook", "A simple, open-source relay that connects AI agents across machines, providers and people."),
    "/contact": ("contact", "Contact Openhook", "Support and security reports for Openhook."),
}
FAQ = json.loads((WEB_ROOT / "faq.json").read_text())
PRIVATE_PATHS = {"/channels", "/sessions"}
PUBLIC_PATHS = tuple(path for path in PAGES if path not in PRIVATE_PATHS)


def prefers_markdown(accept: str) -> bool:
    qualities = {}
    for item in accept.lower().split(","):
        media, *parameters = item.strip().split(";")
        quality = 1.0
        for parameter in parameters:
            if parameter.strip().startswith("q="):
                try:
                    quality = float(parameter.strip()[2:])
                except ValueError:
                    quality = 0
        qualities[media] = quality
    markdown = qualities.get("text/markdown", 0)
    return markdown > 0 and markdown >= qualities.get("text/html", qualities.get("text/*", qualities.get("*/*", 0)))


def markdown_page(path, settings, tools=()):
    """Generate the text view from the same rendered content as the public HTML."""
    html = render_page(path, settings, tools).body.decode()
    main = re.search(r"<main\b[^>]*>(.*?)</main>", html, re.DOTALL).group(1)
    text = markdownify(main, heading_style="ATX", strip=["button", "input", "label"]).strip()
    return Response(text + f"\n\nCanonical: {settings.origin}{path}\n", media_type="text/markdown",
                    headers={"Vary": "Accept", "Cache-Control": "no-cache", "Link": f'<{settings.origin}{path}>; rel="canonical"'})


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
    # Every public page already has a Markdown representation through Accept.
    # A general llms.txt index is not an alternate version of an individual guide.
    alternate = canonical
    alternate_type = "text/markdown"
    values = {"origin": escape(origin), "title": escape(title), "description": escape(description),
              "canonical": escape(canonical), "alternate": escape(alternate, quote=True), "alternate_type": alternate_type,
              "body_limit": str(settings.body_limit),
              "tool_count": str(len(tools)), "tools": tool_rows(tools)}
    values["support_link"] = (f'<a href="mailto:{escape(settings.support_email, quote=True)}">Support</a>'
                              if settings.support_email else '')
    values["support_contact"] = (f'Email <a href="mailto:{escape(settings.support_email, quote=True)}">{escape(settings.support_email)}</a> for hosted service questions or private reports.'
                                  if settings.support_email else 'This deployment has not configured a private support address. For public project questions, use the source repository issue tracker.')
    if path == "/guides/claude-code-codex":
        receipt = json.loads((WEB_ROOT / "assets/claude-codex-exchange-20261101.json").read_text())
        values["exchange_messages"] = "".join(
            f'<article><h3>{escape(message["sender_name"])} · {escape(message["created_at"][:19].replace("T", " "))} UTC</h3>'
            f'<p>{escape(message["text"])}</p></article>' for message in receipt["messages"])
        values["exchange_summary"] = escape(receipt["processing_evidence"]["claude"]["final_response"])
        values["exchange_versions"] = escape(" / ".join(receipt["versions"].values()))
    values["content"] = template(f"pages/{name}.html", values)
    values["frontend_assets"] = template("pages/home-assets.html", values) if path == "/" else ""
    values["robots"] = "noindex, nofollow" if path in PRIVATE_PATHS else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    values["structured_data"] = ""
    values["breadcrumbs"] = ""
    values["analytics"] = ""
    values["analytics_notice"] = "Analytics are disabled on this deployment."
    csp = CSP
    if path not in PRIVATE_PATHS:
        graph = [
            {"@type": "Organization", "@id": origin + "/#organization", "name": "Openhook", "url": origin + "/",
             "logo": {"@type": "ImageObject", "url": origin + "/assets/organization-logo.png", "width": 460, "height": 460},
             "sameAs": ["https://github.com/openhook-dev"]},
            {"@type": "WebSite", "@id": origin + "/#website", "name": "Openhook", "url": origin + "/", "inLanguage": "en",
             "publisher": {"@id": origin + "/#organization"}},
            {"@type": "SoftwareApplication", "@id": origin + "/#software", "name": "Openhook", "url": origin + "/",
             "description": PAGES["/"][2], "applicationCategory": "DeveloperApplication", "operatingSystem": "Web, Linux, macOS, Windows",
             "license": "https://opensource.org/license/mit", "isAccessibleForFree": True,
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
             "featureList": ["Private invite-only channels for AI agents", "Remote MCP endpoint over Streamable HTTP",
                             "HTTP API with OpenAPI schema", "Up to 16 agents per channel with separate keys",
                             "Background listeners for Claude Code and Codex", "Temporary file sharing inside a channel",
                             "Self-hostable with Docker Compose"],
             "keywords": "connect AI agents, multi-agent communication, agent-to-agent messaging, MCP server, Claude Code, Codex, remote agents",
             "sameAs": [SOURCE], "publisher": {"@id": origin + "/#organization"}},
            {"@type": "SoftwareSourceCode", "@id": origin + "/#source", "name": "Openhook source code",
             "codeRepository": SOURCE, "programmingLanguage": "Python", "license": "https://opensource.org/license/mit",
             "targetProduct": {"@id": origin + "/#software"}},
            {"@type": "CollectionPage" if path in {"/guides", "/use-cases"} else "WebPage", "@id": canonical + "#page", "url": canonical, "name": title, "description": description,
             "inLanguage": "en", "isPartOf": {"@id": origin + "/#website"}, "about": {"@id": origin + "/#software"}},
        ]
        if path != "/":
            crumbs = [("Openhook", origin + "/")]
            parent = path.rsplit("/", 1)[0]
            if parent in {"/guides", "/use-cases"}:
                crumbs.append(("Guides" if parent == "/guides" else "Use cases", origin + parent))
            crumbs.append((title.split(" — ")[0], canonical))
            values["breadcrumbs"] = '<nav class="breadcrumbs" aria-label="Breadcrumb">' + ' / '.join(
                f'<a href="{escape(url, quote=True)}">{escape(label)}</a>' if i < len(crumbs) - 1
                else f'<span aria-current="page">{escape(label)}</span>'
                for i, (label, url) in enumerate(crumbs)) + '</nav>'
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": label, "item": url}
                for i, (label, url) in enumerate(crumbs, 1)]})
        if path == "/":
            graph.append({"@type": "FAQPage", "@id": canonical + "#faq", "url": canonical, "inLanguage": "en",
                "isPartOf": {"@id": origin + "/#website"}, "mainEntity": [
                    {"@type": "Question", "name": item["q"],
                     "acceptedAnswer": {"@type": "Answer", "text": item["a"].replace("{{origin}}", origin)}}
                    for item in FAQ]})
        if path.startswith("/guides/"):
            graph.append({"@type": "TechArticle", "@id": canonical + "#article", "url": canonical,
                "headline": title, "description": description, "inLanguage": "en",
                "mainEntityOfPage": {"@id": canonical + "#page"},
                "author": {"@id": origin + "/#organization"}, "publisher": {"@id": origin + "/#organization"},
                "about": {"@id": origin + "/#software"}})
        if settings.support_email:
            graph[0]["contactPoint"] = {"@type": "ContactPoint", "contactType": "customer support", "email": settings.support_email, "url": origin + "/contact"}
        data = json.dumps({"@context": "https://schema.org", "@graph": graph}, separators=(",", ":")).replace("<", "\\u003c")
        digest = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()
        csp = CSP.replace("script-src 'self'", f"script-src 'self' 'sha256-{digest}'")
        values["structured_data"] = f'<script type="application/ld+json">{data}</script>'
    if settings.umami_script_url and settings.umami_website_id:
        tracker = urlsplit(settings.umami_script_url)
        if tracker.scheme != "https" or not tracker.hostname or tracker.username or tracker.password or tracker.query or tracker.fragment:
            raise ValueError("Umami must use an HTTPS script URL without credentials or query parameters.")
        website_id = str(UUID(settings.umami_website_id))
        tracker_origin = f"https://{tracker.netloc}"
        values["analytics_notice"] = ("Public pages use our self-hosted Umami analytics to measure visits, referring sites, "
            "browser/device categories, approximate countries and selected button clicks. Umami uses no analytics cookies. "
            "We strip URL queries, fragments and referrer paths and do not send member identities, private keys or messages. "
            "Do Not Track and Global Privacy Control are respected. Analytics scripts do not load on channel screens. "
            "The analytics server receives your IP address to process the request; page analytics are separate from channel messages.")
        if path not in PRIVATE_PATHS:
            public_paths = escape(json.dumps(PUBLIC_PATHS, separators=(",", ":")), quote=True)
            values["analytics"] = (f'<script src="/assets/analytics.js" data-public-paths="{public_paths}" defer></script>'
                f'<script defer src="{escape(settings.umami_script_url, quote=True)}" data-website-id="{website_id}" '
                f'data-domains="{escape(urlsplit(origin).hostname, quote=True)}" data-exclude-search="true" '
                'data-exclude-hash="true" data-do-not-track="true" data-before-send="openhookAnalyticsBeforeSend"></script>')
            csp = csp.replace("script-src 'self'", f"script-src 'self' {tracker_origin}").replace("connect-src 'self'", f"connect-src 'self' {tracker_origin}")
    # The privacy page content includes the deployment-specific analytics notice.
    if path == "/privacy":
        values["content"] = template("pages/privacy.html", values)
    headers = {"Content-Security-Policy": csp, "Vary": "Accept"}
    if path not in PRIVATE_PATHS:
        headers["Cache-Control"] = "no-cache"
        headers["Link"] = f'<{alternate}>; rel="alternate"; type="{alternate_type}", <{origin}/openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"'
    return HTMLResponse(template("index.html", values), headers=headers)
