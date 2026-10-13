"""Crawl public content and verify caching never reaches private inbox data."""

import json
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from starlette.testclient import TestClient

from openhook.pages import PUBLIC_PATHS
from openhook_hosted.settings import HostedSettings as Settings
from openhook_hosted.app import create_app


def test_public_links_and_guide_schema(tmp_path):
    with TestClient(create_app(Settings(database=str(tmp_path / "seo.db"), hosted_enabled=True))) as client:
        pages = {path: BeautifulSoup(client.get(path).text, "html.parser") for path in PUBLIC_PATHS}
        for path, soup in pages.items():
            assert len(soup.select('h1')) == 1
            assert soup.select_one('meta[name="description"]')['content']
            for link in soup.select('a[href]'):
                target = urlsplit(link['href'])
                if target.netloc or target.scheme:
                    continue
                if target.path in pages and target.fragment:
                    assert pages[target.path].find(id=target.fragment), (path, link['href'])
                elif target.path.startswith('/'):
                    assert client.get(target.path).status_code == 200, (path, link['href'])
            if path.startswith('/guides/'):
                assert len(soup.select_one('main').get_text().split()) > 250
                graph = json.loads(soup.select_one('script[type="application/ld+json"]').string)['@graph']
                assert any(node['@type'] == 'TechArticle' for node in graph)
                crumbs = next(node for node in graph if node['@type'] == 'BreadcrumbList')['itemListElement']
                assert [item['name'] for item in crumbs[:2]] == ['Openhook', 'Guides']
                assert soup.select_one('a[href="/guides"]')


def test_public_redirects_compression_and_private_cache_boundary(tmp_path):
    with TestClient(create_app(Settings(database=str(tmp_path / "cache.db"), hosted_enabled=True))) as client:
        for path in ['/signup', '/login', '/dashboard', '/settings', '/settings/api-keys']:
            response = client.get(path + '?key=do-not-forward', follow_redirects=False)
            assert response.status_code == 308 and response.headers['location'] == '/account'
        slash = client.get('/guides/webhook-testing/?ref=docs', follow_redirects=False)
        assert slash.status_code == 308 and slash.headers['location'] == '/guides/webhook-testing?ref=docs'
        for accept in ['text/html', 'text/markdown']:
            response = client.get('/guides/webhook-testing', headers={'Accept': accept, 'Accept-Encoding': 'gzip'})
            assert response.headers['content-encoding'] == 'gzip'
            assert {'accept', 'accept-encoding'} <= {v.strip().lower() for v in response.headers['vary'].split(',')}
        for path in ['/app', '/account']:
            response = client.get(path, headers={'Accept-Encoding': 'gzip'})
            assert 'content-encoding' not in response.headers
            assert 'no-store' in response.headers['cache-control']
            assert 'noindex' in response.headers['x-robots-tag']
        assert 'immutable' in client.get('/assets/style.css?v=123456abcdef').headers['cache-control']
        assert 'immutable' not in client.get('/assets/style.css').headers['cache-control']
        assert client.post('/api/v1/call', json={'action': 'create'}).status_code == 200
