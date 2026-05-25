# Reddit Access Policy

Status: planning policy

## Access Priority

1. Reddit official Data API, read-only and configuration-gated.
2. Reddit search through approved search providers, only as fallback discovery.
3. User-provided Reddit URLs, handled through safe selected-source workflows.
4. Unavailable response when access requires login scraping, CAPTCHA/anti-bot bypass, or disallowed web scraping.

## Required Defaults

- `REDDIT_ENABLED=false` until a future policy/config prompt adds safe defaults.
- OAuth/configuration required before any live Reddit API call.
- No unauthenticated Reddit web scraping as an API substitute.
- No posting, commenting, voting, direct messages, chat, moderation, or account mutation.
- No Reddit content training.
- No permanent Reddit content storage by default.
- No author metadata storage by default.
- Deleted or removed content must not be retained as evidence.

## Safety Requirements

Any future Reddit connector must:

- execute through ToolBroker,
- declare capabilities in the capability manifest,
- respect PolicyEngine decisions,
- use ApprovalManager for HIGH/CRITICAL future actions,
- write AuditLogger entries for provider/domain/status/rate-limit results,
- respect API rate-limit headers,
- label all post/comment/thread text as `UNTRUSTED_WEB`,
- redact tokens and secrets,
- avoid storing query history by default,
- and report setup, disabled, unavailable, blocked, and rate-limited states clearly.

## Search And URL Fallback

Search-provider discovery may surface Reddit URLs or snippets when provider policy allows it. Snippet-only results must be labeled as such and cannot be cited as full-thread evidence. User-provided Reddit URLs may be normalized in future work, but fetch/read behavior must still honor public access, safe fetch policy, retention policy, and source attribution rules.

## Compliance Gate

Before any live Reddit read is implemented, the project must add config, capability manifest placeholders, retention defaults, rate-limit policy, command registry rows for any CLI commands, and tests proving disabled-by-default behavior.
