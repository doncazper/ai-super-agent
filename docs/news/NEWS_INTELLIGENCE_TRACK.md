# News Intelligence Track

## Scope

News Intelligence is a dedicated future module for current public news workflows. It graduates generic web and research capabilities into a source-grounded, freshness-aware news lane without adding runtime provider calls in this milestone.

This milestone is documentation, roadmap, source policy, risk model, and tracking only. It does not implement commands, providers, browser automation, article fetching, storage, or summarization behavior.

## Goals

- Inspect configured news provider readiness without provider calls.
- Support future current headlines, topic search, source pages, briefs, timelines, source comparison, multilingual summaries, freshness controls, citations, and dogfood/eval coverage.
- Keep news acquisition free-first, source-grounded, auditable, and safe by default.
- Treat every headline, article, snippet, feed item, sitemap URL, and downloaded document as `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
- Return clear unavailable/setup responses when no compliant source is available.

## Non-Goals

- No provider API calls in this milestone.
- No paid API usage by default.
- No scraping paywalled, login-protected, CAPTCHA-protected, anti-bot-protected, or robots-disallowed content.
- No search-history, news-history, or full article-body storage by default.
- No browser automation.
- No fabricated sources, headlines, publication dates, retrieval dates, or citations.
- No current factual claims without returned source data.

## Provider Ladder

Future implementations must attempt sources in this order:

1. Local news cache.
2. User-provided URL.
3. Configured RSS/Atom feeds.
4. News sitemaps.
5. GDELT.
6. Media Cloud, optional and configured.
7. SearXNG, Brave, or SerpAPI through the existing web provider policy.
8. NewsAPI, optional/fallback only.
9. Graceful unavailable response.

Paid, quota-limited, or credentialed providers stay skipped unless explicitly configured and allowed by provider policy.

## Future Commands

| Command | Status | Purpose | Risk |
|---|---|---|---|
| `python smart_agent.py news providers` | planned | Show configured provider readiness without provider calls. | SAFE |
| `python smart_agent.py news top` | planned | Return source-grounded top headlines from compliant configured sources. | LOW |
| `python smart_agent.py news search "query"` | planned | Search public headlines/articles with freshness and source controls. | LOW |
| `python smart_agent.py news topic "topic"` | planned | Gather topic-oriented source candidates. | MEDIUM |
| `python smart_agent.py news source "source"` | planned | Inspect one public source/feed/provider setup. | LOW |
| `python smart_agent.py news brief "topic"` | planned | Produce a source-grounded brief with citations and limits. | MEDIUM |
| `python smart_agent.py news timeline "topic"` | planned | Build dated event timelines only from returned sources. | MEDIUM |
| `python smart_agent.py news compare "topic"` | planned | Compare coverage across sources with caveats. | MEDIUM |
| `python smart_agent.py news multilingual "topic"` | planned | Summarize multilingual public news sources with generated translation labels. | MEDIUM |
| `python smart_agent.py news cache status` | planned | Inspect metadata-only news cache/retention state. | SAFE |
| `python smart_agent.py news dogfood` | planned | Run mock-first news dogfood/eval checks. | SAFE |

## Rollout

1. News Intelligence roadmap and source policy. Complete.
2. News capability manifest entries and provider policy. Complete for disabled/planned manifest entries, safe config defaults, and provider-policy selection/skipping with no provider calls.
3. News provider registry/status commands.
4. News cache and retention scaffolding.
5. RSS/Atom and news sitemap headline acquisition.
6. GDELT provider.
7. Optional Media Cloud and NewsAPI setup-gated providers.
8. Source-grounded `news top`, `news search`, `news topic`, and `news source`.
9. News brief, timeline, compare, and multilingual workflows.
10. News dogfood/eval suite.
11. News release gate and maturity review.

## Acceptance Criteria For Future Runtime Work

- Every executable news capability is declared in `config/capabilities.yaml`.
- Every network/provider action routes through ToolBroker, PolicyEngine, and AuditLogger.
- Provider decisions are auditable and explain skipped paid or unavailable providers.
- Freshness, retrieval timestamps, publication dates, source URLs, provider names, and citation coverage are visible in output.
- Snippet-only, fetched, blocked, failed, and unavailable sources are clearly distinguished.
- Full article text and readable query history are not stored by default.
- Paywall/login/CAPTCHA/anti-bot bypass remains forbidden.

## Current Manifest Entries

The current milestone declares these disabled/planned capabilities in `config/capabilities.yaml`:

- `news.providers.status`
- `news.search`
- `news.top`
- `news.feed.fetch`
- `news.sitemap.fetch`
- `news.gdelt.search`
- `news.gdelt.timeline`
- `news.mediacloud.search`
- `news.newsapi.search`
- `news.article.fetch`
- `news.article.extract`
- `news.brief`
- `news.timeline`
- `news.compare`
- `news.multilingual`
- `news.cache.status`
- `news.cache.clear`
- `news.dogfood`

All are `default_enabled=false` and `status=planned`; the manifest declarations do not make runtime news actions executable. Future implementation must update the manifest deliberately, add ToolBroker tool specs, preserve PolicyEngine and AuditLogger coverage, and add tests before any capability can execute.
