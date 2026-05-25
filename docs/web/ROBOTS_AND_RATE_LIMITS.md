# Robots And Rate Limits

Robots support is part of the free-first Web Acquisition Layer. It is crawler guidance, not authentication, but the agent respects it for crawler-style public fetches.

## Behavior

- `python smart_agent.py web robots "<domain_or_url>"` fetches only the target site's public `robots.txt`.
- Results are labeled `UNTRUSTED_WEB`; the fetched document is treated as `UNTRUSTED_DOCUMENT`.
- `Allow`, `Disallow`, and `Sitemap` directives for `*` and `LocalMacAIAgent` are parsed.
- Malformed lines are ignored safely.
- Missing, blocked, or unavailable robots files return structured unavailable metadata rather than a bypass attempt.
- Direct URL acquisition checks robots guidance before crawler-style page fetches unless a command explicitly documents selected-URL behavior. Selected-URL `web fetch`, `web extract`, and `web metadata` still enforce URL/domain/content bounds and never bypass CAPTCHA, login, paywall, or anti-bot barriers.

## Limits

- Default timeout: 10 seconds.
- Redirects are limited by the shared web fetcher.
- Binary downloads are disabled by default.
- Domain blocklists and allowlists are enforced before network access.
- The `web.robots` capability is rate-limited in `config/capabilities.yaml`.
- Robots, sitemap, and feed fetches share the Web Acquisition Layer TTL cache; cache entries are operational source metadata, not long-term memory.

## Non-Goals

- No CAPTCHA, anti-bot, login-wall, paywall, browser-cookie, session, or proxy bypass.
- No private browser profile or app database access.
- No search history or fetched web content memory write by default.

## Audit

Robots checks execute through `ToolBroker` as `web.robots` and the `web.robots.check` alias. Audit events include the tool name, policy decision, result summary, and network domain. Raw page content is not written to memory.
