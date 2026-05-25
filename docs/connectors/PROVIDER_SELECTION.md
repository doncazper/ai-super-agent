# Provider Selection

Provider selection is a policy decision, not a direct provider execution path. Tools and connector actions must still execute through `ToolBroker`, `PolicyEngine`, `ApprovalManager` where required, and `AuditLogger`.

## Defaults

- Web/search defaults to `auto` and should prefer local cache, user-provided URL, RSS/Atom feed, sitemap, official API, self-hosted SearXNG, Brave, then SerpAPI.
- Weather defaults to `auto` and prefers Open-Meteo for current/forecast weather, NOAA/NWS for U.S. official alerts/data, then WeatherAPI only when explicitly selected or configured and allowed by cost policy.
- Personal communications default to drafts, handoff, and config doctors. Sends require Action Center approval and never become automatic provider fallbacks.

## Free-First Web Acquisition

`web.robots`, `web.sitemap`, `web.feed`, `web.acquire_url`, and `web.acquire` are the first runtime consumers of the web provider ladder. They use cache, explicit public feeds, public sitemaps, and direct URL fetch before any paid or quota-limited search provider. Query acquisition does not store raw query history by default; when no free source is available it returns a clear unavailable result with skipped-provider reasons instead of silently calling paid APIs.

## Optional SerpAPI Fallback

SerpAPI is implemented as an explicit fallback provider through `web.search.serpapi`, `python smart_agent.py web search "<query>" --provider serpapi`, and `python smart_agent.py research "<query>" --provider serpapi`.

It is not selected by the default `web.search` path under `free_first` merely because `SERPAPI_API_KEY` exists. Runtime use requires:

- `SERPAPI_API_KEY`
- `SERPAPI_ENABLED=true`
- `ALLOW_PAID_APIS=true`
- `MAX_PAID_API_CALLS_PER_DAY>0`
- explicit `--provider serpapi` or an intentionally configured SerpAPI default

Results are normalized into the same search-result shape as other providers, labeled `UNTRUSTED_WEB`, query arguments are redacted in audit logs by default, and provider decisions are included in tool results and audit summaries. Missing keys, disabled provider config, or disabled paid/quota policy return setup hints instead of silent fallback or direct Google scraping.

## Weather Provider Selector

Weather auto-selection is implemented for the brokered weather tools:

- `weather.current` and `weather.forecast` select Open-Meteo first under `free_first`.
- `weather.alerts` skips Open-Meteo because it does not provide active alerts and selects NOAA/NWS for U.S. official alert data.
- `weatherapi` is available through explicit `--provider weatherapi` when `WEATHERAPI_API_KEY` or `WEATHER_API_KEY` is configured.
- WeatherAPI is not promoted to the default path merely because a key exists. Configured-default WeatherAPI use requires paid-provider allowance.

The CLI exposes:

```bash
python smart_agent.py weather providers
python smart_agent.py weather provider auto "Phoenix, AZ"
python smart_agent.py weather current "Phoenix, AZ" --provider auto
python smart_agent.py weather current "Phoenix, AZ" --provider weatherapi
```

Weather provider decisions are included in structured tool results as `provider_decision` and in audit result summaries. API keys are never included in tool output or audit payloads.

## Provider Decision Fields

The reusable policy layer returns:

- selected provider or unavailable status
- skipped providers with reasons
- `skip_reasons` keyed by provider id
- cost mode
- `paid_api_used`
- `cache_used`
- `audit_summary`
- configured state
- reason for selection or denial
- setup hint
- explicit provider request, if any
- redacted metadata

## Inspection Commands

```bash
python smart_agent.py web providers
python smart_agent.py web provider-policy
python smart_agent.py web provider-decision "https://example.com/source"
```

These commands execute through `ToolBroker`, are audited, and make no live provider calls. They are intended for setup/debugging and release-gate evidence before new provider implementations are added. `provider-decision` redacts query text in audit logs by default and does not persist query history.

## Auditing

Provider decisions should be logged as `provider.select` with the domain, selected/skipped providers, cost mode, and setup hint. Audit payloads must not include API keys, tokens, credentials, full query history, or raw personal content.

## Unsupported Providers

Unsupported, unconfigured, paid, or quota-limited providers must return clear setup hints instead of silently falling back to paid APIs or fabricating results.

## Current Limitations

The current implementation includes no-key RSS/Atom, sitemap, robots.txt, direct URL, local-cache acquisition, optional explicit SerpAPI search, and optional explicit WeatherAPI weather calls. It does not add SearXNG or other new paid/quota-limited provider network implementations.
