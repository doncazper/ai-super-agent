# Forum Access Policy

Status: planning policy

## Purpose

This policy defines safe access patterns for Reddit-like forums, multilingual community sites, and Chinese/Asia forum discovery. It applies before any forum connector, search workflow, summarizer, translation workflow, or cache feature is implemented.

## Allowed Access Modes

| Mode | Allowed When | Requirements |
|---|---|---|
| Official public API | API is documented, read-only use is configured, and rate limits are respected | ToolBroker execution, PolicyEngine check, AuditLogger provider/domain record, no write scopes by default. |
| Approved search-provider discovery | Provider policy allows it | No paid provider by default, query redaction where sensitive, source snippets labeled `UNTRUSTED_WEB`. |
| User-provided public URL fetch | URL is public, allowed by safe fetch policy, and not behind login/CAPTCHA/anti-bot controls | Use safe web fetch/extraction; no cookies or session automation. |
| RSS/feed/sitemap discovery | Public feed/sitemap is documented and allowed | Feed items/snippets only unless later selected fetch is explicitly allowed. |
| Unavailable response | Access requires login, CAPTCHA, anti-bot bypass, private data, or forbidden scraping | Report blocked/unavailable with reason; do not attempt bypass. |

## Forbidden Access

- Scraping logged-in/private pages.
- CAPTCHA, Cloudflare, anti-bot, proxy-evasion, or rate-limit bypass.
- Cookie/session automation for platform access.
- Browser profile, private app database, or hidden account-state reads.
- Posting, commenting, voting, direct messages, moderation, or account actions in this track.
- Training on Reddit/forum content without explicit rights and permission.
- Permanent storage of forum content by default.

## Trust And Instruction Boundary

All forum content is `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`. Forum text can be quoted, summarized, translated, and cited as source data, but it cannot:

- request tools,
- reveal secrets,
- approve actions,
- alter policy,
- grant permissions,
- disable audit logging,
- write memory,
- or override system/developer/user instructions.

## Tooling Boundary

Future forum actions must route through ToolBroker and their declared capability manifest entries. Provider adapters cannot self-enable capabilities or call network APIs outside the brokered path. PolicyEngine and AuditLogger must see the provider, domain, capability, risk, trust level, result status, and any blocked/unavailable reason.

## Storage Boundary

Forum content is not stored permanently by default. Future cache behavior must be TTL-bound, public-only, and retention-aware. Author-identifying metadata is minimized and disabled by default.
