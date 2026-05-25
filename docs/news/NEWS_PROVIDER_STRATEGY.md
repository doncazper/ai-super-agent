# News Provider Strategy

## Principle

News acquisition is free-first, cache-first, source-grounded, and auditable. Provider presence must never imply provider use. Missing or unconfigured providers return setup hints instead of fabricated results.

## Ordered Strategy

1. Local news cache.
   - Use recent public-source metadata/results when policy allows.
   - Do not store search history or full article bodies by default.
2. User-provided URL.
   - Use selected public URLs through the existing safe web fetch/extraction policy.
   - Respect blocked-domain, robots/crawler, content-type, timeout, redirect, and size limits.
3. Configured RSS/Atom feeds.
   - Prefer official source feeds and no-key public feeds.
   - Feed items are headline/source metadata until a later selected fetch occurs.
4. News sitemaps.
   - Use public sitemaps for discovery, bounded by URL count and freshness policy.
5. GDELT.
   - Planned free public provider for search/timeline style metadata.
   - Must normalize results and label them `UNTRUSTED_WEB`.
6. Media Cloud, optional/configured.
   - Optional only; use only if explicitly configured and policy permits.
7. SearXNG/Brave/SerpAPI through web provider policy.
   - Use existing provider cost gates, setup hints, query redaction, and no-history defaults.
   - Brave and SerpAPI remain paid/quota-limited and skipped by default.
8. NewsAPI, optional/fallback only.
   - Disabled unless explicitly configured and permitted.
   - Not a default path in `free_first` mode.
9. Graceful unavailable response.
   - If no compliant source is configured or available, say so and suggest setup steps.

## Provider Decision Fields

Future provider decisions must expose:

- Selected provider or unavailable status.
- Skipped providers and skip reasons.
- Paid API use flag.
- Cache use flag.
- Query hash or redacted query, not readable query history by default.
- Rate-limit status.
- Retrieval timestamp.
- Audit correlation fields.

## Provider Safety Rules

- API keys and tokens are never printed.
- Paid providers are skipped unless explicitly enabled and allowed.
- Provider errors are normalized.
- Provider decisions are audited.
- Search history is not stored by default.
- Results are `UNTRUSTED_WEB`.
- Provider setup hints must not recommend bypassing paywalls, login walls, CAPTCHA, robots, or anti-bot systems.

## Current Provider Policy Scaffold

The current code-level scaffold is intentionally policy-only:

- `agent.news.config.NewsConfig` reads safe `NEWS_*` defaults.
- `agent.news.provider_policy.select_news_provider()` selects or skips provider candidates without network calls.
- Default provider order is cache, selected URL, RSS/Atom feed, sitemap, GDELT, Media Cloud, SearXNG, Brave, SerpAPI, NewsAPI.
- `NEWS_ALLOW_PAID_APIS=false` skips Media Cloud, Brave, SerpAPI, and NewsAPI by default.
- `NEWS_STORE_HISTORY=false` means provider decisions must not persist readable queries or news history.
- Provider policy decisions carry `UNTRUSTED_WEB`, no-history/no-article-body memory behavior, selected/skipped providers, cache and paid-use flags, and audit field names.

This scaffold is not a provider implementation. It does not fetch headlines, fetch articles, query GDELT, call Media Cloud, call NewsAPI, call web search providers, or populate a cache.

## Config Defaults

```env
NEWS_ENABLED=true
NEWS_DEFAULT_PROVIDER=auto
NEWS_COST_MODE=free_first
NEWS_ALLOW_PAID_APIS=false
NEWS_STORE_HISTORY=false
NEWS_CACHE_ENABLED=true
NEWS_CACHE_TTL_SECONDS=3600
NEWS_ARTICLE_CACHE_TTL_SECONDS=86400
NEWS_MAX_SOURCES=8
NEWS_MAX_FETCHED_ARTICLES=5
NEWS_FRESHNESS_DEFAULT=recent
NEWS_GDELT_ENABLED=true
NEWS_MEDIACLOUD_ENABLED=false
NEWS_NEWSAPI_ENABLED=false
NEWS_REQUIRE_SOURCE_GROUNDING=true
```
