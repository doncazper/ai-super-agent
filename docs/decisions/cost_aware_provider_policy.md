# Cost-Aware Provider Policy Decision

Date: 2026-05-23

Status: accepted for local policy scaffolding; new paid provider API calls remain out of scope.

## Decision

Provider selection must prefer free, local, no-key, official, cached, or explicitly user-provided sources before paid or quota-limited APIs. Paid providers are never selected as defaults unless the user explicitly enables paid APIs with configuration.

## Selection Order

Web/search:

1. local cache
2. RSS/Atom feeds
3. sitemaps
4. direct public URL fetch
5. official site APIs
6. self-hosted SearXNG
7. Brave Search, if configured
8. SerpAPI, if configured and paid APIs are allowed
9. graceful unavailable response

Weather:

1. Open-Meteo
2. NOAA/NWS for U.S. official data
3. WeatherAPI if configured and selected/allowed
4. graceful unavailable response

Personal communications:

1. local drafts and handoff
2. Gmail/Telegram config doctor
3. draft-only workflows
4. approved-send workflows only after Action Center approval

## Config

- `PROVIDER_COST_MODE=free_first|balanced|quality_first|manual`
- `ALLOW_PAID_APIS=false`
- `MAX_PAID_API_CALLS_PER_DAY=0`
- `SEARCH_DEFAULT_PROVIDER=auto`
- `WEATHER_DEFAULT_PROVIDER=auto`

## Safety Rules

- Provider decisions are auditable with provider, domain, cost mode, skipped providers, and setup hints.
- Provider decision payloads must redact secret-looking fields.
- Provider selection must not store user query history by default.
- Prompt text, web content, or provider responses cannot change cost policy or grant paid-provider permission.
- This decision does not implement SerpAPI, WeatherAPI, or any new paid API call path.

## Rationale

This keeps normal agent usage predictable and low-cost while preserving an explicit path for user-configured paid providers later. It also gives future provider work a reusable policy shape before adding more acquisition modules.

## Follow-Ups

- Wire future web acquisition providers through this policy before adding live API calls.
- Add config-doctor checks for paid-provider settings and daily call budgets.
- Keep provider selection evidence in audit events and release-gate docs.
