# Public search and agent discovery

## November 4, 2026 baseline

A fresh HTTP crawl found 12 public sitemap pages returning 200 with self-referencing
HTML canonicals and no public noindex directive. Robots and sitemap were accessible.
There was no demonstrated site-wide crawl block. `/guides` returned 404; `/agents`
and `/about` had no crawlable navigation path from the homepage. The server-rendered
homepage repeated its headline ending. Individual pages advertised a general site
index or tool/skill document as their text alternate instead of their own content.

A cold desktop DevTools trace, without CPU or network throttling, measured LCP
440 ms, TTFB 28 ms and CLS 0.00. CrUX field data was unavailable. This is one lab
observation, not a mobile or real-user performance guarantee.

Read-only Umami query at 16:00 UTC / 17:00 Europe/Berlin:

- November 4 to that time: 4 tracked visitors, 15 pageviews.
- October 12 to that time: 109 tracked visitors, 172 pageviews.
- October 29–November 4 referral pageviews: direct/unknown 73, X (`t.co`) 18,
  Google 1, Hacker News 1, self-referral 1.

These figures can include the owner and internal QA, including the live browser
checks in this audit. They are not external-user or adoption counts. Direct traffic
does not establish a source. Only production hostnames and old empty hostname values
were included; local previews are not tracked. No private channel content was read.

Search Console dashboard data could not be retrieved through the available browser
connection. Sitemap submission receipts from earlier releases are not proof of
indexing. No current impression, ranking or indexed-page count is claimed.

## Changes

- Concrete homepage, setup and API metadata without a hardcoded tool count.
- A guide index, two-person setup/troubleshooting guide and Docker self-hosting guide.
- Direct links from the homepage to the tested Claude Code/Codex exchange and setup
  guides, plus navigation to previously orphaned public pages.
- Same-page HTML/Markdown alternatives using `Accept: text/markdown` and `Vary: Accept`.
- Visible breadcrumbs matching schema; technical-article schema on actual guides.
- Current llms.txt links and accurate server-readable security limits.
- Public routes derive sitemap, route registration and analytics scope from the same
  catalog. Private channel screens remain no-store/noindex and have no analytics.

No fabricated ratings, search volumes, last-modified dates, reviews or customer
claims. No content farms, doorway pages or promise that metadata guarantees ranking.

## Verification

```sh
bun run build
bun run typecheck
uv run pytest -q
uv run python scripts/generate_docs.py --check
python3 scripts/audit_seo.py http://127.0.0.1:8788
python3 scripts/audit_seo.py https://openhook.dev
```

The read-only audit exits nonzero on missing metadata, wrong canonicals/text
alternates, duplicate titles/descriptions, public noindex directives, failed
requests or public pages unreachable through homepage links. It checks the actual
HTML without executing JavaScript and requests each page's Markdown representation.
It does not measure rankings, prove search-engine indexing or certify security.

Regression tests also check guide schema/breadcrumb agreement, crawler access and
private-page exclusion. Before rollout the local 15-page audit had no findings;
the previous live version had 14 discovery findings (12 wrong text alternates and
two orphan pages). These are checks we defined, not a Google SEO score.

## Next measurement

After deployment, verify live bytes and all 15 public URLs. Recheck the existing
Google/Bing properties when dashboard access works: separate submitted, discovered,
crawled and indexed. Do not reset site verification or repeatedly submit unchanged
URLs. Compare non-branded impressions/clicks, landing-page referrals and real first
exchanges over subsequent weeks; do not treat our QA, a copied prompt or a stored
message as customer activation.

Official references: [Google SEO starter guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide),
[canonical URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
and [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).

## November 7, 2026: remote-agent positioning

Primary positioning moved from "your agent ↔ another person's agent" to "connect
your AI agents across machines". Person-to-person channels remain a secondary use.

- Homepage H1, title, description, examples and setup prompt target multi-machine use.
- New guide `/guides/connect-agents-across-machines` (TechArticle, breadcrumbs, sitemap).
- Visible homepage FAQ and matching `FAQPage` schema, both from `web/faq.json`.
- `SoftwareApplication` gains `offers` (free), `featureList`, `keywords`, `sameAs`.
- 1200×630 `og-image.png` replaces the 460×460 logo for social cards.
- llms.txt, skill description, server.json and README lead with the same positioning.

Local audit: 0 issues across all public pages. No ranking or indexing claim.
