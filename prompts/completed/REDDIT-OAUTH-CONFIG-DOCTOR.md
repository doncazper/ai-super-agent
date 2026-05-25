# REDDIT-OAUTH-CONFIG-DOCTOR

status: completed
completed_at: 2026-05-25
category: forums
trust_level: TRUSTED_USER

## Scope

Build safe Reddit OAuth/config doctor and status commands before adding any Reddit content access.

## Non-goals

- No Reddit read-only content connector.
- No Reddit post, comment, thread, subreddit, or user-content fetch.
- No Reddit web scraping or unauthenticated web fallback.
- No posting, commenting, voting, DMs, chat, or moderation actions.
- No CAPTCHA, login-wall, anti-bot, robots, or API-limit bypass.
- No permanent Reddit user-content storage.
- No Reddit content use for model training.

## Evidence

- Added `agent.forums.reddit.doctor` for redacted metadata-only `reddit_status`, `reddit_doctor`, and explicit `reddit_auth_check`.
- Added brokered `reddit.status` and `reddit.auth_check` tools and CLI commands `reddit doctor`, `reddit status`, and `reddit auth-check`.
- Added `connectors status reddit` metadata with setup hints and no content fetch.
- Added warnings for disabled Reddit config, missing OAuth fields, tracked `.env`, repo-local token-file paths, missing/generic user agent, denied web fallback, and hard-false training policy.
- Added mocked auth-check success/failure tests, redaction tests, audit tests, disabled status tests, and no-content-fetch assertions.
- Updated README, Reddit compliance docs, command registry, command test matrix, changelog, feature registry, maturity tracker, risk/threat docs, project state, prompt tracking, and completion report.

## Validation

Validation results are recorded in `docs/COMPLETION_REPORT.md`.

## Next Prompt

`REDDIT-READ-ONLY-CONNECTOR`
