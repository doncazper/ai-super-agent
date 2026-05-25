# Internet Provider Strategy

The agent uses a cache-first, free-first provider ladder. Provider selection should be predictable, auditable, and conservative.

## Web/Search Provider Ladder

1. Local cache.
2. User-provided public URL.
3. RSS/Atom feeds.
4. Sitemaps.
5. Official site APIs.
6. Self-hosted SearXNG, if configured.
7. Brave Search, if configured.
8. SerpAPI, if configured and allowed by cost policy.
9. Graceful unavailable response.

## Provider Requirements

Every provider integration must document:

- Provider name and command/capability surface.
- Whether it is free, paid, quota-limited, local, self-hosted, official, or third-party.
- Whether credentials are required.
- Whether it is eligible under `PROVIDER_COST_MODE=free_first`.
- Whether `ALLOW_PAID_APIS=true` is required.
- Audit domains and redaction behavior.
- Rate limits and cache TTL.
- Data retention behavior.
- Setup hints for missing configuration.
- Failure and fallback behavior.

## Planned Provider Registry Fields

| Field | Purpose |
|---|---|
| `provider_id` | Stable identifier such as `cache`, `url`, `feed`, `sitemap`, `official_api`, `searxng`, `brave`, or `serpapi`. |
| `cost_class` | `free`, `self_hosted`, `quota_limited`, `paid`, or `unknown`. |
| `default_eligible` | Whether provider may be auto-selected under safe defaults. |
| `requires_key` | Whether credentials are required. |
| `requires_paid_opt_in` | Whether `ALLOW_PAID_APIS=true` is required. |
| `audit_domains` | Domains recorded in audit metadata when used. |
| `stores_query_history` | Must be `false` unless a future explicit retention design is approved. |
| `trust_label` | Usually `UNTRUSTED_WEB`. |
| `setup_hint` | User-facing setup guidance for unavailable providers. |

## Current Status

| Provider path | Current status | Notes |
|---|---|---|
| Central Web Acquisition Layer | implemented for core v1 | `agent.web_acquisition` provides request/result/source/provider models, deterministic source planning, cost-policy wrapping, trust labels, and no-fetch `web.source_status` inspection. |
| Local cache | implemented for web acquisition v1 | Cache is operational TTL state, not memory. |
| RSS/Atom | implemented for web acquisition v1 | Content remains untrusted. |
| Sitemaps | implemented for web acquisition v1 | Sitemap documents are untrusted documents. |
| Direct public URL fetch | implemented | Robots and blocked-page behavior must remain conservative. |
| Official site APIs | planned | Prefer official APIs when available and no-key/user-configured. |
| Self-hosted SearXNG | planned | Must be explicit/self-hosted; no public instance default. |
| Brave Search | optional provider implemented | Requires `BRAVE_SEARCH_API_KEY`, `BRAVE_SEARCH_ENABLED=true`, and paid/quota policy opt-in; never default by key presence. |
| SerpAPI | explicit optional fallback implemented | Requires `SERPAPI_API_KEY`, `SERPAPI_ENABLED=true`, and paid/quota policy opt-in; never default under `free_first`. |
| Unavailable response | required | Do not hallucinate results when no provider can safely satisfy the request. |

## Policy Inspection

`web providers`, `web provider-policy`, `web provider-decision "<query>"`, and `web source-status "<url>"` expose current policy/source decisions without calling provider APIs or fetching page content where noted. Decision output includes selected/skipped providers, skip reasons, cost mode, paid API use, cache use, trust labels, and an audit summary. Query history remains off by default.

## Weather And Other Public APIs

Weather follows the same cost-aware principle but uses domain-specific provider order: Open-Meteo, NOAA/NWS for U.S. official data, optional WeatherAPI only when configured and allowed, then unavailable response.

## Personal Communications

Personal communications are not web acquisition. Gmail, Telegram, Messages, Calendar, Contacts, Tasks, and Lead Inbox adapters remain disabled by default and require selected-scope, approval-gated designs. Sends are CRITICAL.
