# Internet Access Graduation Track

Status: accepted
Date: 2026-05-23
Scope: roadmap, policy, risk model, feature tracking, and release-gate reset only.

## Decision

Internet access will graduate through a staged, free-first track before it is treated as a mature source-grounded research system. Existing web/search/fetch capabilities remain available under their current ToolBroker, PolicyEngine, AuditLogger, cost-policy, cache, and rate-limit gates. Future provider work must follow this track instead of adding ad hoc search or scraping paths.

This reset does not add provider calls, enable paid APIs, run live web requests, add browser automation, or store query history.

## Non-Goals

- Do not add new search providers in this release gate.
- Do not run live web calls.
- Do not use paid APIs.
- Do not bypass CAPTCHA, Cloudflare, robots.txt, login walls, or anti-bot protections.
- Do not scrape logged-in pages or browser profiles.
- Do not add browser automation beyond explicit selected-URL workflows.
- Do not store web queries or fetched content in memory by default.

## Graduation Track

| Step | Track item | Status after reset | Gate before next level |
|---:|---|---|---|
| 1 | Cost-aware provider policy | complete | Cost policy defaults remain `free_first`, `ALLOW_PAID_APIS=false`, and provider decisions are auditable. |
| 2 | Web Acquisition Layer core | complete for local v1 | No paid provider default, no bypass attempts, and brokered cache/feed/sitemap/direct URL paths tested. |
| 3 | Robots/sitemap/feed support | complete for local v1 | Robots and blocked pages return blocked/unavailable rather than bypass attempts. |
| 4 | Search provider registry | complete for local v1 | Registry lists provider cost, auth, default state, privacy behavior, setup hints, and normalized result/error schemas without provider calls. |
| 5 | SearXNG provider | planned | Self-hosted provider only; no hosted instance becomes default without explicit config. |
| 6 | Brave provider | planned hardening | Existing optional provider needs explicit provider registry metadata and source-grounding eval coverage. |
| 7 | SerpAPI optional fallback | complete for explicit fallback | Must remain non-default under `free_first`; requires key and paid-API allowance. |
| 8 | Safe fetch/extraction hardening | planned | Add extraction diagnostics, redirect reporting, content-type handling, and binary download gates. |
| 9 | Source-grounded research workflow | planned hardening | Require source evidence, fetch-failure reporting, citations, and conflict handling. |
| 10 | Router: internet only when needed | planned | Router must avoid web for stable/no-tool prompts and explain when current info is required. |
| 11 | Citation/source attribution | planned | Every factual current claim must link to source URLs or state the limitation. |
| 12 | Cache/dedupe/local lightweight index | planned | Cache must be TTL-bounded and must not become query-history memory. |
| 13 | Official API connector framework | planned | Prefer official no-key or user-configured APIs over scraping when available. |
| 14 | Dogfood/eval suite | planned | Add safe web acquisition and source-grounding evals with mocks by default. |
| 15 | Internet Access release gate | planned final gate | Full tests, docs validation, startup policy, manifest validation, provider-cost checks, and no-bypass scans. |

## Risk Model

| Activity | Risk | Notes |
|---|---|---|
| Public search query | LOW/MEDIUM | MEDIUM when the query contains sensitive intent, names, locations, or business/customer context. |
| Direct public URL fetch | LOW/MEDIUM | MEDIUM for user-provided URLs, redirects, unknown domains, or pages with executable-looking instructions. |
| Fetching user-provided URL | MEDIUM | Content is `UNTRUSTED_WEB`; no login, cookies, or browser profile data. |
| Crawling multiple URLs | MEDIUM | Requires explicit limits, robots awareness, rate limits, cache use, and audit domains. |
| Downloading binary files | HIGH or disabled by default | Requires a separate approval-gated design before enabling. |
| Login/cookie/session access | FORBIDDEN in this track | Do not scrape logged-in pages or browser profiles. |
| CAPTCHA/anti-bot bypass | FORBIDDEN | Return blocked/unavailable. |
| Browser automation | deferred | URL-based selected-source workflows only. |
| Paid API use | approval/config-gated | Never default under `free_first`. |

## Required Behavior

- Web content is always `UNTRUSTED_WEB`; stored/extracted documents are `UNTRUSTED_DOCUMENT`.
- Webpage text cannot instruct the agent to call tools, reveal secrets, alter policy, grant approvals, write memory, or ignore system rules.
- Provider selection is cache-first and free-first.
- Paid/quota-limited providers are optional fallback only.
- Blocked pages return `blocked` or `unavailable`, not bypass attempts.
- Provider decisions must explain why a provider was selected or skipped.
- Query history and fetched content are not stored in memory by default.
- All runtime acquisition must execute through ToolBroker and be audited when a tool runs.

## Release-Gate Result

This decision record resets the roadmap and tracking state. It does not mark future internet access work as mature. Existing implemented web commands remain covered by their prior tests, while the broader mature internet access system remains a staged track.
