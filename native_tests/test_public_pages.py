"""Crawlers and agents receive real content before any JavaScript runs."""

import base64
import hashlib
import json
import re
from xml.etree import ElementTree

from starlette.testclient import TestClient

from openhook.pages import PUBLIC_PATHS
from openhook.settings import Settings
from openhook.web import WebCall, WaitCall, create_app


def test_public_html_metadata_and_schema(tmp_path):
    settings = Settings(database=str(tmp_path / "pages.sqlite3"), origin="http://testserver")
    with TestClient(create_app(settings)) as client:
        titles = set()
        for path in PUBLIC_PATHS:
            response = client.get(path)
            assert response.status_code == 200
            html = response.text
            assert "{{" not in html
            assert re.search(r'<main[^>]*>\s*<div', html)
            assert html.count("<h1") == 1
            assert 'class="brand-logo"' in html
            assert f'<link rel="canonical" href="http://testserver{path}">' in html
            assert f'<meta property="og:url" content="http://testserver{path}">' in html
            title = re.search(r"<title>(.*?)</title>", html).group(1)
            assert title not in titles
            titles.add(title)
            data = re.search(r'<script type="application/ld\+json">(.*?)</script>', html).group(1)
            assert json.loads(data)["@context"] == "https://schema.org"
            digest = base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()
            assert f"'sha256-{digest}'" in response.headers["content-security-policy"]
            assert "unsafe-inline" not in response.headers["content-security-policy"]
        docs = client.get("/docs").text
        names = [tool["name"] for tool in client.get("/api/tools").json()["tools"]]
        assert all(f'id="{name}"' in docs for name in names)
        assert "get_webhook_activity" in names
        assert client.get("/not-a-page").status_code == 404
        assert client.get("/app").headers["x-robots-tag"] == "noindex, nofollow"


def test_agent_discovery_is_consistent_with_runtime(tmp_path):
    with TestClient(create_app(Settings(database=str(tmp_path / "agent.sqlite3"), origin="http://testserver"))) as client:
        for path in ("/llms.txt", "/llms-full.txt", "/agents.md", "/skill.md", "/docs.md"):
            response = client.get(path)
            assert response.status_code == 200
            assert "{{" not in response.text
            assert "ohk_" not in response.text or "private" in response.text
        assert "http://testserver/mcp" in client.get("/llms.txt").text
        assert "get_webhook_activity" in client.get("/llms-full.txt").text
        skill = client.get("/skill.md").text
        assert skill.startswith("---\nname: openhook\ndescription:")
        schema = client.get("/openapi.json").json()
        assert schema["openapi"] == "3.1.1"
        assert schema["servers"] == [{"url": "http://testserver"}]
        assert schema["components"]["schemas"]["WebCall"] == WebCall.model_json_schema()
        assert schema["components"]["schemas"]["WaitCall"] == WaitCall.model_json_schema()
        assert "/api/wait" in schema["paths"] and "/h/{identifier}" in schema["paths"]
        robots = client.get("/robots.txt").text
        assert "Allow: /api/tools" in robots
        for path in ("/app", "/mcp", "/h/", "/api/"):
            assert f"Disallow: {path}" in robots
        sitemap = ElementTree.fromstring(client.get("/sitemap.xml").text)
        urls = [node.text for node in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        assert urls == ["http://testserver" + path for path in PUBLIC_PATHS]
