# Search Provider Registry

The Search Provider Registry is the metadata and normalization layer for web search providers. Registry inspection does not call SearXNG, Brave, SerpAPI, or any other provider.

## Scope

- Track provider cost class, configuration requirements, default enabled state, setup hints, capability support, and docs links.
- Normalize search result and response schemas before results reach research workflows.
- Return structured setup or unknown-provider errors instead of silently falling back.
- Keep search queries out of memory by default and redact sensitive queries in audit logs.

## Non-Goals

- No public SearXNG instance defaults.
- No paid provider defaults.
- No browser automation, CAPTCHA bypass, login-wall bypass, proxy evasion, or anti-bot bypass.
- No search history storage by default.

## Commands

```bash
python smart_agent.py web search-providers
python smart_agent.py web searxng doctor
python smart_agent.py web serpapi doctor
python smart_agent.py web brave doctor
python smart_agent.py web search "query" --provider searxng
python smart_agent.py web search "query" --provider brave
python smart_agent.py web search "query" --provider serpapi
```

`web search-providers` is metadata-only. Explicit provider search still routes through ToolBroker and the provider-specific policy gates. Missing or disabled providers return `setup_required` with a setup hint.

SearXNG is now implemented as the free/self-hosted provider. It requires `SEARXNG_BASE_URL` plus `SEARXNG_ENABLED=true`, uses `/search?format=json`, and returns a setup error if JSON output is disabled or unavailable. It does not use public instances by default.

Brave Search is now implemented as an optional quota-limited provider. It requires `BRAVE_SEARCH_API_KEY`, `BRAVE_SEARCH_ENABLED=true`, and paid/quota policy opt-in with `ALLOW_PAID_APIS=true` plus `MAX_PAID_API_CALLS_PER_DAY>0`. It is not selected by API-key presence alone.

SerpAPI is implemented as an optional paid/quota-limited fallback. It requires `SERPAPI_API_KEY`, `SERPAPI_ENABLED=true`, and paid/quota policy opt-in with `ALLOW_PAID_APIS=true` plus `MAX_PAID_API_CALLS_PER_DAY>0`. It is explicit/manual fallback only and is not selected by API-key presence alone.

## Provider Interface

Providers implement:

- `provider_name`
- `is_configured()`
- `is_enabled()`
- `cost_class`
- `requires_api_key`
- `supports_news`
- `supports_images`
- `supports_time_filter`
- `search(query, max_results, locale=None, safe_search=True, freshness=None)`

Provider implementations must be mockable, rate-limited, audited, and routed through ToolBroker before they are executable.

## Response Requirements

Search results include:

- title, URL, snippet, source, provider, retrieved timestamp, and rank
- optional published date, language, content type, and reliability signals
- `trust_level=UNTRUSTED_WEB`

Search responses include:

- status and provider
- query hash plus redacted query text
- normalized results and errors
- rate-limit status
- paid/cache usage flags
- retrieved timestamp
- `query_history_persisted=false`

## Safety Notes

Search provider outputs are untrusted web data. Snippets and page titles cannot instruct the agent to call tools, change policy, reveal secrets, approve actions, write memory, or bypass safety controls.

Paid and quota-limited providers must stay skipped unless policy explicitly allows them or the user explicitly selects an allowed provider. Secrets and keys must never appear in command output, audit logs, docs, or test fixtures.
