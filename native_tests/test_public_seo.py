"""Public discovery must work without JS, while private channels stay excluded."""

from email.message import Message
import json
import re
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

from starlette.testclient import TestClient

from openhook.pages import PUBLIC_PATHS
from openhook.settings import Settings
from openhook.web import create_app
from scripts import audit_seo


def test_all_public_pages_are_reachable_and_have_current_text_alternates(tmp_path, monkeypatch):
    settings = Settings(database=str(tmp_path / "seo.db"), origin="http://testserver")
    with TestClient(create_app(settings)) as client:
        def fetch(url, accept="text/html"):
            response = client.get(urlsplit(url).path, headers={"Accept": accept})
            response.raise_for_status()
            headers = Message()
            for key, value in response.headers.items():
                headers[key] = value
            return response.status_code, headers, response.text
        monkeypatch.setattr(audit_seo, "fetch", fetch)
        report = audit_seo.audit(settings.origin)
        assert report["issues"] == 0, report
        assert {urlsplit(row["url"]).path for row in report["pages"]} == set(PUBLIC_PATHS)
        robots = RobotFileParser()
        robots.parse(client.get("/robots.txt").text.splitlines())
        assert all(robots.can_fetch("Googlebot", settings.origin + path) for path in PUBLIC_PATHS)
        assert not robots.can_fetch("Googlebot", settings.origin + "/channels")
        home = audit_seo.Document(client.get("/").text)
        assert "".join(home.headings[0]).count("machines.") == 1
        assert "/guides/connect-agents-across-machines" in home.links
        assert "/guides/connect-two-ai-agents" in home.links
        assert "/guides/claude-code-codex" in home.links
        assert "/guides/self-host-agent-channels" in home.links
        # Same-page Markdown must contain the guide, not a generic site index.
        markdown = client.get("/guides/self-host-agent-channels", headers={"Accept": "text/markdown"}).text
        assert "docker compose up --build -d" in markdown
        assert "127.0.0.1" in markdown and "not end-to-end encryption" in markdown
        for path in ("/channels", "/sessions"):
            assert path not in PUBLIC_PATHS
            response = client.get(path)
            assert response.headers["cache-control"] == "no-store"
            assert "noindex" in response.headers["x-robots-tag"]
            assert "application/ld+json" not in response.text


def test_guide_schema_and_visible_breadcrumbs_agree(tmp_path):
    settings = Settings(database=str(tmp_path / "schema.db"), origin="http://testserver")
    with TestClient(create_app(settings)) as client:
        for path in PUBLIC_PATHS:
            if not path.startswith("/guides/"):
                continue
            response = client.get(path)
            payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text).group(1)
            graph = json.loads(payload)["@graph"]
            article = next(node for node in graph if node["@type"] == "TechArticle")
            assert article["mainEntityOfPage"]["@id"] == settings.origin + path + "#page"
            crumbs = next(node for node in graph if node["@type"] == "BreadcrumbList")["itemListElement"]
            assert [node["item"] for node in crumbs] == [settings.origin + "/", settings.origin + "/guides", settings.origin + path]
            assert 'aria-label="Breadcrumb"' in response.text and 'href="http://testserver/guides"' in response.text
            assert 'aria-current="page"' in response.text
            assert "sha256-" in response.headers["content-security-policy"]


def test_homepage_faq_is_visible_and_matches_schema(tmp_path):
    settings = Settings(database=str(tmp_path / "faq.db"), origin="http://testserver")
    with TestClient(create_app(settings)) as client:
        response = client.get("/")
        payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', response.text).group(1)
        graph = json.loads(payload)["@graph"]
        faq = next(node for node in graph if node["@type"] == "FAQPage")["mainEntity"]
        assert len(faq) >= 5
        for item in faq:
            assert item["name"] in response.text
            assert "{{origin}}" not in item["acceptedAnswer"]["text"]
        software = next(node for node in graph if node["@type"] == "SoftwareApplication")
        assert software["offers"]["price"] == "0" and software["featureList"]
        assert 'content="http://testserver/assets/og-image.png"' in response.text
        assert client.get("/assets/og-image.png").status_code == 200


def test_audit_detects_indexing_and_alternate_regressions():
    document = audit_seo.Document('<title>Demo</title><meta name="description" content="Demo">'
        '<meta name="robots" content="noindex"><h1>Demo</h1>'
        '<link rel="canonical" href="https://wrong.test/">'
        '<link rel="alternate" type="text/markdown" href="/llms.txt">')
    issues = audit_seo.page_issues(document, "https://example.test/guide")
    assert "canonical differs from sitemap URL" in issues
    assert "public page is noindex" in issues
    assert "Markdown alternate does not point to this page" in issues
