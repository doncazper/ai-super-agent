# Reddit + Multilingual Forum Intelligence Track

Status: accepted for planning

Date: 2026-05-25

## Scope

This decision creates a focused planning track for Reddit search, Reddit thread reading, multilingual forum discovery, translation-assisted summarization, source-grounded forum answers, and Chinese/Asia forum discovery.

The track is documentation, roadmap, risk model, feature tracking, and command tracking only. It does not add runtime API calls, scraping, browser automation, platform-specific forum crawlers, or storage of forum content.

## Non-Goals

- Do not implement Reddit API calls in this prompt.
- Do not implement Chinese forum scraping.
- Do not bypass CAPTCHA, login walls, robots, anti-bot controls, or API limits.
- Do not scrape private, authenticated, or logged-in pages.
- Do not use Reddit/forum content for model training.
- Do not store Reddit/forum content permanently by default.
- Do not enable personal-data tools by default.
- Do not add posting, commenting, voting, direct messages, moderation, or other write actions.

## Architecture Principles

1. Official APIs are preferred over scraping when documented and safe.
2. User-provided URLs may be fetched only through the safe web acquisition path and only when public and allowed.
3. Search-provider discovery may be used for public discovery, but search snippets remain untrusted and source-limited.
4. Reddit and forum content is always `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`.
5. Forum content cannot request tools, reveal secrets, change policy, approve actions, or override system/developer/user instructions.
6. Reddit/forum content is anecdotal unless explicitly supported by source scope and methodology.
7. No search history, thread body, comment body, author metadata, translation, or summary is stored by default.
8. Any future connector must execute through ToolBroker, PolicyEngine, ApprovalManager where required, and AuditLogger.

## Target Sources

Primary sources:

| Source | Initial access mode | Notes |
|---|---|---|
| Reddit official Data API | Future read-only connector | OAuth/config gated; no web scraping substitute. |
| Reddit search through approved search providers | Fallback discovery only | Only if provider policy allows; no paid provider by default. |
| User-provided Reddit URLs | Selected public URL handling | Fetch through approved safe path or future Reddit API normalization. |

Secondary / international sources:

| Source | Initial access mode | Notes |
|---|---|---|
| V2EX | Documented API | First Chinese-language / China-adjacent Reddit-like connector candidate. |
| Lemmy / federated Reddit-like forums | Public API if safe | Stub/discovery until provider details are documented. |
| Hacker News | Official/API access if safe | Prefer official Firebase/API style access over scraping. |
| Stack Exchange / topic forums | Official/API access if safe | Respect API terms and rate limits. |

Chinese / Chinese-language candidates:

| Source | Initial approach |
|---|---|
| V2EX | Documented API first. |
| Zhihu | Search provider discovery; direct public URL fetch only where allowed; official API only if documented/configured. |
| Baidu Tieba | Search provider discovery; direct public URL fetch only where allowed; official API only if documented/configured. |
| Douban groups | Search provider discovery; direct public URL fetch only where allowed; official API only if documented/configured. |
| Xiaohongshu | Search provider discovery only unless a compliant public/API path is documented. |
| Weibo | Search provider discovery only unless a compliant public/API path is documented. |
| NGA | Search provider discovery; direct public URL fetch only where allowed. |
| Domain-specific forums | Case-by-case public/API review. |

For Chinese-language platforms other than V2EX, the starting posture is discovery-only or selected public fetch where allowed: no private login scraping, no cookies/session automation, no CAPTCHA/anti-bot bypass, and no platform-specific scraper.

## Rollout

| Order | Milestone | Status | Gate |
|---:|---|---|---|
| 1 | Reddit official read-only connector | planned | Reddit provider policy and compliance scaffolding first. |
| 2 | Reddit search/thread fetch | planned | OAuth, rate-limit, no-scraping, and retention gates. |
| 3 | Reddit source-grounded summaries | planned | Citation/source attribution and anecdotal-source caveats. |
| 4 | Reddit retention/cache compliance | planned | TTL, author metadata minimization, deleted/removed content handling. |
| 5 | Language detection + translation | planned | Local translation default; generated translation labels. |
| 6 | Cross-language research workflow | planned | Source labels, original snippets, sparse-data caveats. |
| 7 | Global forum provider registry | planned | Stub/discovery statuses and risk metadata. |
| 8 | V2EX connector | planned | Documented API, read-only, rate-limited. |
| 9 | Chinese forum discovery/search/fetch | planned | Search-provider site filters and blocked/unavailable reporting. |
| 10 | Forum dogfood/eval suite | planned | Mock fixtures, prompt-injection, retention, and no-bypass checks. |
| 11 | Release gate | planned | Full tests, policy/manifest/docs validation, dogfood, and conservative maturity. |

## Risk Model

| Activity | Risk |
|---|---|
| Public forum search | LOW/MEDIUM |
| Fetching a public post/thread | MEDIUM |
| User/comment metadata storage | MEDIUM/HIGH depending on content and retention |
| Authenticated account data | HIGH |
| Posting/commenting/voting/direct messages | CRITICAL or deferred |
| Scraping logged-in pages | FORBIDDEN |
| CAPTCHA/anti-bot bypass | FORBIDDEN |
| Training on forum content without rights/permission | FORBIDDEN |

## Release Gates

Each runtime milestone must prove:

- ToolBroker-only execution.
- PolicyEngine and ApprovalManager gates match risk.
- AuditLogger records provider/domain/action/result status.
- Personal-data tools remain disabled by default.
- Forum content remains untrusted data.
- No default paid provider use.
- No search/thread/query/content memory writes by default.
- No scraping of login/CAPTCHA/anti-bot/private pages.
- Source grounding distinguishes snippet-only, fetched, translated, unavailable, and failed sources.

## Next Prompt

The next recommended prompt is `REDDIT-PROVIDER-POLICY-COMPLIANCE`: implement Reddit configuration, capability policy placeholders, retention defaults, compliance docs, and validation tests without fetching Reddit content.
