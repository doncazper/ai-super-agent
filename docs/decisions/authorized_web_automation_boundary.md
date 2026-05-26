# Authorized Web Automation Boundary

Status: specified

## Decision

The agent may plan for future authorized browser automation and deep web scanning, but it must not implement browser automation or bypass behavior in this milestone.

Future automation is allowed only for explicitly authorized contexts, such as first-party staging app testing, official CAPTCHA/Turnstile/reCAPTCHA test keys, user-in-the-loop manual login, official APIs/OAuth, approved partner access, contracted security testing with written scope, user-provided exports, or browser selected-page handoff where the user controls the session.

For third-party or unauthorized sites, the following are forbidden:

- CAPTCHA bypass
- Cloudflare or anti-bot bypass
- proxy evasion
- rate-limit evasion
- login-wall bypass
- paywall bypass
- cookie/session scraping
- human impersonation
- stealth browser automation

Blocked sources must return blocked or unavailable status with a reason. They must not trigger bypass attempts.

## Deep Scan V1 Boundary

Deep scan v1 is a future planned workflow to gather publicly accessible linked resources from a user-provided URL within policy. It must respect robots/crawl policy, rate limits, domain allowlists, crawl budgets, content-type limits, and retention policy. It must not download binaries by default, bypass barriers, or treat web content as instructions.

All gathered content is `UNTRUSTED_WEB`, and all network domains must be audited.

## Rationale

The user eventually wants richer page/resource gathering. This decision keeps that path compatible with legality, provider terms, robots/crawl policy, and the agent safety control plane before runtime automation exists.

## Approval Gates

Future deep scan or browser automation requires explicit user approval, domain allowlist, crawl budget, rate limit, robots policy, legal/compliance note, data retention policy, no paid API unless allowed, no bypass/evasion, and dogfood/eval evidence.
