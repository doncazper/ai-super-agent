# News Retention Policy

## Default Retention

News workflows must not store readable search history, news history, or full article bodies by default.

Allowed default retention is limited to operational metadata needed for safety, dedupe, cache freshness, and source attribution:

- URL or provider source ID.
- Source title/headline.
- Domain/source name.
- Provider/acquisition path.
- Retrieved timestamp.
- Published timestamp when source-provided.
- Evidence type.
- Trust label.
- Content hash/source hash.
- Snippet or short summary only when policy allows.
- TTL and expiry time.

## Disallowed Default Retention

- Full article body text.
- Full fetched HTML.
- Readable user search queries.
- Authenticated or private content.
- Paywalled/login/CAPTCHA content beyond blocked-status metadata.
- Binary article files unless a future HIGH-risk explicit workflow is approved.
- Personal data extracted from news pages unless a separate policy permits it.

## Cache Rules

- Cache public news data only.
- Cache keys should use URL/provider/query hashes.
- Query text should be redacted or hashed when stored.
- Full content storage must be opt-in, documented, TTL-bounded, and disabled by default.
- Cache clear/export/status commands must be auditable.
- Cache refreshes must respect provider, robots, rate-limit, and blocked-source policies.

## Deletion And Expiry

Future news cache entries must include `retrieved_at`, `expires_at`, and source type. Expired entries should be ignored or swept. If the system cannot guarantee retention policy for a source type, it should disable caching for that source type.

## Training And Memory

News content is not used for model training. News results and article bodies are not written to long-term memory by default. Any future explicit memory workflow must preserve source IDs, trust labels, user intent, and approval rules for sensitive content.

## Current Config And Manifest Guardrails

The current scaffold sets `NEWS_STORE_HISTORY=false`, `NEWS_CACHE_ENABLED=true`, `NEWS_CACHE_TTL_SECONDS=3600`, and `NEWS_ARTICLE_CACHE_TTL_SECONDS=86400`.

The capability manifest entries added for `news.*` are all `status=planned` and `default_enabled=false`. They declare `memory_behavior` explicitly:

- Search, top, feed, sitemap, GDELT, article fetch/extract, brief, timeline, compare, multilingual, provider status, cache status, and dogfood use `no_store`.
- Cache clear uses `cache_only` because it affects only future local cache metadata and must audit deletion counts when implemented.

These manifest entries are placeholders for future ToolBroker-routed implementations. They do not permit article-body persistence, readable query history, or provider calls by themselves.
