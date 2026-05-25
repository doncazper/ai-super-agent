# Web Cache Policy

The web cache reduces repeated network/provider calls while keeping public web data bounded, untrusted, and easy to delete.

## Scope

Web cache v1 stores public, unauthenticated web source metadata by default:

- normalized HTTP/S URL
- provider
- query hash, when a query-derived source is cached
- title and snippet
- stable `source_id`
- content hash
- retrieved and expiry timestamps
- source metadata
- `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT` labels

It does not store raw search history, personal/authenticated content, cookies, sessions, blocked page bodies, CAPTCHA pages, or full article text by default.

## Defaults

- `WEB_CACHE_ENABLED=true`
- `WEB_CACHE_TTL_SECONDS=3600`
- `WEB_CACHE_STORE_FULL_CONTENT=false`
- cache file: `data/web_cache/cache.json`
- index file: `data/web_cache/index.json`

Source-type TTLs can be overridden with variables like `WEB_CACHE_TTL_FEED_SECONDS`, `WEB_CACHE_TTL_SITEMAP_SECONDS`, `WEB_CACHE_TTL_FETCH_SECONDS`, and `WEB_CACHE_TTL_ARTICLE_SECONDS`.

## Cacheability Rules

The cache accepts public web/document data only. A source is denied when it is marked as personal, authenticated, private, login-required, cookie/session-derived, or outside HTTP/S public URL policy.

Blocked, CAPTCHA, login, forbidden, or unavailable pages may store status metadata only. Page bodies and extracted text are not retained for those cases.

## Query Handling

Raw search queries are not persisted by default. Cache keys use URL, provider, and query hash. Audit logs redact index/cache query arguments unless explicitly configured otherwise.

## Commands

```bash
python smart_agent.py web cache status
python smart_agent.py web cache clear
python smart_agent.py web cache show <source_id>
```

All cache commands run through ToolBroker and AuditLogger. They do not call providers or perform network refreshes.

## Refresh Policy

Cache refreshes must use the existing brokered search, feed, sitemap, or fetch paths. Future refresh automation must respect robots guidance, domain blocklists/allowlists, provider policy, rate limits, and paid-provider gates.
