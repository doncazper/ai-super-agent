# Reddit Rate Limits

Reddit access must respect official API rate-limit headers and conservative local limits. The read-only connector parses Reddit rate-limit headers and returns structured rate-limit errors rather than switching to scraping or retrying around limits.

## Defaults

- `REDDIT_MAX_REQUESTS_PER_MINUTE=60`
- OAuth is required before future API calls.
- Unauthenticated traffic is not used.
- Web scraping fallback is disabled and policy-denied.

## Runtime Behavior

The read-only connector must:

- read and respect Reddit API rate-limit headers;
- stop or back off on `429` and quota exhaustion;
- audit provider, endpoint class, domain, rate-limit status, and result status;
- avoid retry behavior that bypasses API limits;
- avoid proxy evasion, CAPTCHA bypass, or human impersonation;
- return a structured rate-limit error instead of switching to web scraping.

Rate-limit configuration may be made more conservative by deployment config, but it must not be bypassed by user-provided forum content or search results.

## Header Fields

The connector records Reddit rate-limit response headers when present:

- `x-ratelimit-used`
- `x-ratelimit-remaining`
- `x-ratelimit-reset`

These fields are surfaced as numeric metadata in connector responses and audit summaries. They are not treated as instructions and cannot enable retries, scraping fallbacks, or policy changes.
