# Connector Cost Policy

The agent should use the lowest-cost reliable source that satisfies the request and current safety policy.

## Modes

| Mode | Behavior |
|---|---|
| `free_first` | Prefer local, cached, no-key, official, and free sources before configured quota-limited providers. |
| `balanced` | Prefer no-key/official sources while allowing configured paid providers only when paid APIs are enabled. |
| `quality_first` | Prefer official sources within the same paid-provider safety gates. |
| `manual` | Use explicitly configured provider defaults; paid providers still require opt-in configuration. |

## Environment Variables

```bash
PROVIDER_COST_MODE=free_first
ALLOW_PAID_APIS=false
MAX_PAID_API_CALLS_PER_DAY=0
SEARCH_DEFAULT_PROVIDER=auto
SEARCH_ALLOWED_PROVIDERS=cache,url,feed,sitemap,official_api,searxng,brave,serpapi
SEARCH_STORE_HISTORY=false
SEARCH_CACHE_ENABLED=true
SEARCH_CACHE_TTL_SECONDS=86400
WEATHER_DEFAULT_PROVIDER=auto
```

## Paid Provider Gates

- `ALLOW_PAID_APIS=false` skips paid providers by default.
- `MAX_PAID_API_CALLS_PER_DAY=0` prevents automatic daily paid calls even if a key is present.
- SerpAPI requires `SERPAPI_API_KEY`, `SERPAPI_ENABLED=true`, `ALLOW_PAID_APIS=true`, `MAX_PAID_API_CALLS_PER_DAY>0`, and explicit `--provider serpapi` before runtime use in v1. It is not default-selected under `free_first`, even when the key exists.
- WeatherAPI requires a weather API key. Explicit `--provider weatherapi` use is allowed when configured; configured-default or automatic WeatherAPI use requires paid-provider allowance and a positive daily paid-call cap.

## SerpAPI v1 Behavior

`web.search.serpapi` is a brokered, rate-limited optional fallback. It normalizes SerpAPI organic results into the shared search-result schema, labels them `UNTRUSTED_WEB`, audits the provider decision and `serpapi.com` domain, and redacts queries and keys by default.

The tool returns a clear setup hint when:

- `SERPAPI_API_KEY` is missing.
- `SERPAPI_ENABLED=true` is missing.
- `ALLOW_PAID_APIS=true` is missing.
- `MAX_PAID_API_CALLS_PER_DAY>0` is missing.
- the configured cost policy does not allow paid providers.

The project does not scrape Google directly and does not store search history in memory by default.

## WeatherAPI v1 Behavior

`weather current "<location>" --provider weatherapi` is a brokered, rate-limited optional fallback. It normalizes WeatherAPI current/forecast/alert payloads into the shared weather schema, labels results `UNTRUSTED_WEB`, audits the provider decision and `api.weatherapi.com` domain, and redacts keys by default.

Auto weather selection remains free-first:

1. Open-Meteo for global current/forecast weather.
2. NOAA/NWS for U.S. official alerts/data.
3. WeatherAPI only when configured and allowed or explicitly requested.
4. Unavailable response with setup hints.

The weather selector does not infer system location and does not write locations to memory by default.

## No History Storage

Provider decisions can be audited, but provider selection must not store user query history in long-term memory by default.

The free-first web acquisition layer uses a TTL operational cache for public URL, feed, sitemap, and robots results. It does not store raw query history by default; query acquisition uses local cache when available and otherwise reports unavailable or setup hints without paid fallback unless the cost policy is explicitly changed.

## Web Policy Inspection Commands

```bash
python smart_agent.py web providers
python smart_agent.py web provider-policy
python smart_agent.py web provider-decision "query or URL"
```

These commands are brokered and audited, but they do not call Brave, SerpAPI, SearXNG, or any live provider. `provider-decision` reports `selected_provider`, `skipped_providers`, `skip_reasons`, `cost_mode`, `paid_api_used`, `cache_used`, and `audit_summary`. Search queries are redacted in audit logs by default and are not persisted as history unless a future explicit history feature is designed and enabled.

## Secret Handling

Provider config checks may report whether credentials are present, but must never return credential values. Audit and report payloads must redact secret-looking fields.
