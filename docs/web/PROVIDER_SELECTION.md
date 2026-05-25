# Web Provider Selection

Web provider selection is free-first and cache-first. Paid or quota-limited providers are fallback/manual options only.

## Default Ladder

1. local cache
2. user-provided URL
3. RSS/Atom feed
4. sitemap
5. official site API
6. self-hosted SearXNG
7. Brave Search, if configured and allowed
8. SerpAPI, if configured and allowed
9. graceful unavailable response

## SerpAPI Fallback

SerpAPI is implemented as an explicit optional fallback through:

```bash
python smart_agent.py web serpapi doctor
python smart_agent.py connectors status serpapi
python smart_agent.py web search "query" --provider serpapi
python smart_agent.py research "query" --provider serpapi
```

Runtime use requires all of:

- `SERPAPI_API_KEY`
- `SERPAPI_ENABLED=true`
- `ALLOW_PAID_APIS=true`
- `MAX_PAID_API_CALLS_PER_DAY>0`
- explicit `--provider serpapi`

SerpAPI is not selected automatically under `free_first`, including when the API key exists.

## Audit And Memory

Provider decisions include selected provider, skipped providers, skip reasons, cost mode, paid API usage, cache usage, and a redacted audit summary. Search query history and full web content are not persisted by default.

## Forbidden Behavior

The provider ladder must not be used to bypass CAPTCHA, paywalls, login walls, robots guidance, API limits, anti-bot systems, or human-review requirements. Blocked pages return blocked or unavailable status instead of bypass attempts.
