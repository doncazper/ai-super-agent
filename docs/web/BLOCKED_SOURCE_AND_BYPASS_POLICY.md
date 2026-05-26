# Blocked Source And Bypass Policy

Blocked sources are data-access boundaries, not puzzles to solve.

| Source condition | Required response |
|---|---|
| CAPTCHA or bot challenge | Return unavailable; do not solve or bypass. |
| Cloudflare or anti-bot challenge | Return unavailable; do not evade. |
| Login wall | Return unavailable unless a future approved user-in-the-loop workflow applies. |
| Paywall | Return unavailable; use snippets, metadata, official APIs, or user-provided exports if allowed. |
| Robots/crawl disallow | Respect policy and report blocked. |
| Rate limit | Stop, back off, and report limitation. |
| Binary/downloaded file | Disabled by default; future use is HIGH and scoped. |

All blocked/unavailable reports must include the source URL/domain when safe, blocked reason, retrieved/checked time if available, and `bypass_attempted=false`.

Forbidden bypass categories:

- CAPTCHA bypass
- Cloudflare or anti-bot bypass
- proxy evasion
- rate-limit evasion
- login-wall bypass
- paywall bypass
- cookie/session scraping
- human impersonation
- stealth browser automation
