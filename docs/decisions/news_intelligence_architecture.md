# Decision: News Intelligence Architecture

Date: 2026-05-25

Status: Specified

## Context

The repo already has web acquisition, safe fetch/extraction, search provider policy, source-grounded research, citations, cache/index, official API stubs, internet dogfood/evals, and forum intelligence. News needs a dedicated track because current events require stronger freshness, source, citation, retention, and provider-policy discipline than generic web search.

## Decision

Create a News Intelligence track as a docs-first module built on existing web/research foundations. The module will remain future work until capabilities, provider policy, ToolBroker mappings, tests, and release gates are added.

The first milestone creates:

- Track roadmap.
- Source policy.
- Provider strategy.
- Freshness policy.
- Source-grounding policy.
- Retention policy.
- Planned command registry entries.
- Risk and threat model updates.

## Provider Order

Future implementations must prefer:

1. Local news cache.
2. User-provided URL.
3. Configured RSS/Atom feeds.
4. News sitemaps.
5. GDELT.
6. Media Cloud, optional/configured.
7. SearXNG/Brave/SerpAPI via web provider policy.
8. NewsAPI, optional/fallback only.
9. Graceful unavailable response.

## Risk Model

| Activity | Risk |
|---|---|
| News provider status | SAFE |
| Public headline search | LOW |
| Article fetch | MEDIUM |
| Source comparison/research | MEDIUM |
| Binary/downloaded article files | HIGH or disabled |
| Paid provider usage | Config/approval-gated |
| Login/paywall/CAPTCHA bypass | FORBIDDEN |

## Safety Requirements

- No provider API calls in this milestone.
- No paid providers by default.
- No search-history or full article-body storage by default.
- All news content is `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
- News content cannot instruct tool calls, policy changes, approval, memory writes, secret disclosure, or citation fabrication.
- Current facts require source data.
- Future execution must route through ToolBroker, PolicyEngine, and AuditLogger.
- Future HIGH or CRITICAL actions require ApprovalManager according to risk.
- Provider decisions must be audited and secret-redacted.

## Consequences

News work can now proceed in smaller, auditable milestones without inventing a side-channel around web provider policy. The cost is that no runtime news command exists yet; command registry entries are planned only and must not be presented as user-ready.

