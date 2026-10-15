"""Public HTML for people and crawlers; JavaScript only adds interactions."""

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
    "/about": ("about", "About Openhook — Open-source webhook service for AI agents", "Learn what Openhook does, who it serves, how the open-source project and hosted service work, and their limits."),
    "/contact": ("contact", "Contact Openhook — Support and project links", "Contact Openhook support, report a bug, find the source code, or ask about hosted accounts without sharing secrets."),
    "/": ("home", "Openhook — Webhook testing and MCP inbox for AI agents", "Test webhooks with a free public URL. Inspect requests, receive callbacks through MCP, and forward events to localhost. Open source and self-hostable."),
    "/connect": ("connect", "Connect your AI agent — Openhook", "Connect Claude Code, Cursor, VS Code, or a local MCP client to Openhook. Create a webhook inbox and receive your first event."),
    "/docs": ("docs", "Webhook MCP tools and API documentation — Openhook", "Create webhook inboxes, inspect payloads, wait with a cursor, and forward events locally. Live MCP tool schemas and REST API documentation."),
    "/agents": ("agents", "Webhook testing and notifications for agents — Openhook", "A practical guide for AI agents: public webhook URLs, local testing, event waits, local notifications, private tokens, and resumable delivery."),
    "/privacy": ("privacy", "Privacy and event retention — Openhook", "How Openhook stores webhook events, private management tokens, browser bookmarks, and provider credentials. Understand retention and deletion."),
    "/app": ("app", "Your webhook inboxes — Openhook", "Create a webhook inbox and inspect captured events on this device."),
    "/account": ("account", "Your hosted account — Openhook", "Manage your Openhook hosted account and agent access."),
    "/pricing": ("pricing", "Hosted plans and self-hosting — Openhook", "Try a free webhook inbox, run Openhook yourself, or explore persistent hosted inboxes for your agent."),
    "/guides": ("guides", "Webhook testing guides — Openhook", "Practical guides to testing webhooks, forwarding events to localhost, verifying GitHub deliveries, and self-hosting an MCP inbox with Openhook."),
    "/guides/callback-proof": ("callback-proof", "Prove a webhook arrived before your agent continues — Openhook", "Run a reproducible callback test, compare original payload bytes, and use MCP cursors to give your coding agent evidence of webhook receipt."),
    "/guides/webhook-testing": ("webhook-testing", "Test webhooks with curl and an AI agent — Openhook", "Create a free webhook URL, send a JSON request, inspect its body and headers, and clean up. A working curl and MCP walkthrough using Openhook."),
    "/guides/local-webhooks": ("local-webhooks", "Receive webhooks on localhost without a tunnel — Openhook", "Forward captured webhook requests to a local HTTP handler with Openhook. Understand retries, signing secrets, cursors, and the limits of queued delivery."),
    "/guides/github-webhooks": ("github-webhooks", "Test GitHub webhooks with an MCP inbox — Openhook", "Receive GitHub push events in Openhook, verify webhook signatures, inspect delivery IDs, and clean up a test subscription from your AI agent."),
    "/guides/self-hosting": ("self-hosting", "Self-host a webhook receiver and MCP server — Openhook", "Run Openhook with Python and uv, persist webhook events in SQLite, connect an MCP client, and configure public HTTPS routing for external callbacks."),
}
PRIVATE_PATHS = {"/app", "/account"}
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
    alternate = "/docs.md" if path == "/docs" else "/agents.md" if path == "/agents" else "/llms.txt"
    alternate_type = "text/markdown" if alternate.endswith(".md") else "text/plain"
    values = {"origin": escape(origin), "title": escape(title), "description": escape(description),
              "canonical": escape(canonical), "alternate": alternate, "alternate_type": alternate_type,
              "event_limit": str(settings.event_limit), "body_limit": str(settings.body_limit),
              "tool_count": str(len(tools)), "tools": tool_rows(tools)}
    values["guide_links"] = "\n".join(
        f'<li><a href="{url}">{escape(meta[1].split(" — ")[0])}</a><p>{escape(meta[2])}</p></li>'
        for url, meta in PAGES.items() if url.startswith("/guides/"))
    billing_ready = settings.billing_ready
    values["billing_provider"] = settings.billing_provider_label
    values["support_link"] = (f'<a href="mailto:{escape(settings.support_email, quote=True)}">Support</a>'
                              if settings.support_email else '')
    values["support_contact"] = (f'Email <a href="mailto:{escape(settings.support_email, quote=True)}">{escape(settings.support_email)}</a> for hosted service questions or private reports.'
                                  if settings.support_email else 'This deployment has not configured a private support address. For public project questions, use the source repository issue tracker.')
    values["account_link"] = '<a href="/account">Account</a>' if settings.hosted_enabled else ''
    values["pro_price"] = '$19 USD / month' if billing_ready else 'Planned: $19 USD / month'
    values["pro_action"] = ('<p>Plus applicable tax. Renews monthly until canceled.</p><p><a href="/account" data-analytics-event="pro-click">Get started with Pro →</a></p>'
                            if billing_ready else '<p>Coming soon. Paid checkout is not available yet.</p><p><a href="/app">Try a free inbox →</a></p>')
    values["content"] = template(f"pages/{name}.html", values)
    values["robots"] = "noindex, nofollow" if path in PRIVATE_PATHS else "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
    values["structured_data"] = ""
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
             "publisher": {"@id": origin + "/#organization"}},
            {"@type": "SoftwareSourceCode", "@id": origin + "/#source", "name": "Openhook source code",
             "codeRepository": SOURCE, "programmingLanguage": "Python", "license": "https://opensource.org/license/mit",
             "targetProduct": {"@id": origin + "/#software"}},
            {"@type": "WebPage", "@id": canonical + "#page", "url": canonical, "name": title, "description": description,
             "inLanguage": "en", "isPartOf": {"@id": origin + "/#website"}, "about": {"@id": origin + "/#software"}},
        ]
        if path != "/":
            crumbs = [("Openhook", origin + "/")]
            if path.startswith("/guides/"):
                crumbs.append(("Guides", origin + "/guides"))
            crumbs.append((title.split(" — ")[0], canonical))
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": i, "name": label, "item": url}
                for i, (label, url) in enumerate(crumbs, 1)]})
        if path.startswith("/guides/"):
            graph.append({"@type": "TechArticle", "@id": canonical + "#article", "headline": title.split(" — ")[0],
                          "description": description, "inLanguage": "en", "url": canonical,
                          "mainEntityOfPage": {"@id": canonical + "#page"}, "about": {"@id": origin + "/#software"},
                          "author": {"@id": origin + "/#organization"}, "publisher": {"@id": origin + "/#organization"}})
        if path in {"/", "/pricing"}:
            graph[2]["offers"] = [{"@type": "Offer", "name": "Free hosted inbox", "price": "0", "priceCurrency": "USD", "url": origin + "/pricing"}]
            if billing_ready:
                graph[2]["offers"].append({"@type": "Offer", "name": "Hosted Pro monthly subscription", "url": origin + "/pricing",
                    "priceSpecification": {"@type": "UnitPriceSpecification", "price": "19", "priceCurrency": "USD",
                                           "billingDuration": "P1M", "valueAddedTaxIncluded": False}})
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
            "We strip URL queries, fragments and referrer paths and do not send account identities, inbox tokens or event content. "
            "Do Not Track and Global Privacy Control are respected. Analytics scripts do not load on account or inbox screens. "
            "The analytics server receives your IP address to process the request; page analytics are separate from captured webhook data.")
        if path not in PRIVATE_PATHS:
            values["analytics"] = (f'<script src="/assets/analytics.js" defer></script>'
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
        headers["Link"] = f'<{origin}{alternate}>; rel="alternate"; type="{alternate_type}", <{origin}/openapi.json>; rel="service-desc"; type="application/vnd.oai.openapi+json"'
    return HTMLResponse(template("index.html", values), headers=headers)
