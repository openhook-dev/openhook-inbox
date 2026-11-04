"""Read-only public SEO checks. This checks discoverability, not search indexing."""

from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.title = []
        self.headings = []
        self.descriptions = []
        self.canonicals = []
        self.alternates = []
        self.links = []
        self.robots = []
        self._capture = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._capture = self.title
        elif tag == "h1":
            self.headings.append([])
            self._capture = self.headings[-1]
        elif tag == "meta":
            name = attrs.get("name", "").lower()
            if name == "description":
                self.descriptions.append(attrs.get("content", ""))
            elif name == "robots":
                self.robots.append(attrs.get("content", ""))
        elif tag == "link":
            relations = attrs.get("rel", "").split()
            if "canonical" in relations:
                self.canonicals.append(attrs.get("href", ""))
            if "alternate" in relations and attrs.get("type") == "text/markdown":
                self.alternates.append(attrs.get("href", ""))
        elif tag == "a":
            self.links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag in {"title", "h1"}:
            self._capture = None

    def handle_data(self, text):
        if self._capture is not None:
            self._capture.append(text)


def page_issues(document, canonical):
    issues = []
    if not "".join(document.title).strip():
        issues.append("missing title")
    if len(document.descriptions) != 1 or not document.descriptions[0].strip():
        issues.append("expected one nonempty description")
    if document.canonicals != [canonical]:
        issues.append("canonical differs from sitemap URL")
    if len(document.headings) != 1 or not "".join(document.headings[0]).strip():
        issues.append("expected one nonempty h1")
    if any("noindex" in value.lower() for value in document.robots):
        issues.append("public page is noindex")
    if document.alternates != [canonical]:
        issues.append("Markdown alternate does not point to this page")
    return issues


def fetch(url, accept="text/html"):
    request = Request(url, headers={"User-Agent": "Openhook-SEO-Audit/1.0", "Accept": accept, "DNT": "1"})
    with urlopen(request, timeout=20) as response:
        return response.status, response.headers, response.read().decode("utf-8")


def audit(origin):
    _, _, sitemap = fetch(origin + "/sitemap.xml", "application/xml")
    urls = [node.text for node in ElementTree.fromstring(sitemap).iter(
        "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if not urls or len(urls) != len(set(urls)):
        raise ValueError("Sitemap is empty or contains duplicate URLs")
    if any(urlsplit(url).netloc != urlsplit(origin).netloc or not url.startswith(origin + "/") for url in urls):
        raise ValueError("Sitemap contains URLs outside the requested origin")
    results, links, titles, descriptions = [], {}, {}, {}
    for url in urls:
        row = {"url": url, "issues": []}
        try:
            status, headers, html = fetch(url)
            document = Document(html)
            row.update(status=status, title="".join(document.title),
                h1=" ".join("".join(h) for h in document.headings))
            row["issues"].extend(page_issues(document, url))
            if "noindex" in headers.get("X-Robots-Tag", "").lower():
                row["issues"].append("HTTP header makes public page noindex")
            links[url] = {urljoin(url, href).split("#")[0].split("?")[0] for href in document.links}
            for value, seen, label in ((row["title"], titles, "title"),
                    ("".join(document.descriptions), descriptions, "description")):
                if value in seen:
                    row["issues"].append(f"duplicate {label}: {seen[value]}")
                seen[value] = url
            _, md_headers, markdown = fetch(url, "text/markdown")
            if md_headers.get_content_type() != "text/markdown" or f"Canonical: {url}" not in markdown:
                row["issues"].append("Markdown representation is missing or has the wrong canonical")
        except Exception as error:
            row["issues"].append(str(error))
        results.append(row)
    # A sitemap alone does not make an orphan page discoverable through navigation.
    public_urls = set(urls)
    reachable, pending = set(), [origin + "/"]
    while pending:
        url = pending.pop()
        if url in reachable:
            continue
        reachable.add(url)
        pending.extend((links.get(url, set()) & public_urls) - reachable)
    for row in results:
        if row["url"] not in reachable:
            row["issues"].append("no crawlable path from the homepage")
    return {"origin": origin, "pages": results, "issues": sum(len(row["issues"]) for row in results),
        "indexing_verified": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origin", help="Public HTTP(S) origin, without a path")
    args = parser.parse_args()
    origin = args.origin.rstrip("/")
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
        parser.error("Supply an HTTP(S) origin without credentials, path, query or fragment")
    try:
        report = audit(origin)
    except Exception as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
    print(json.dumps(report, indent=2))
    sys.exit(bool(report["issues"]))
