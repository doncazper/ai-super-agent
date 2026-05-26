# Deep Scan Policy

Deep scan is planned, not implemented.

## Definition

Deep scan v1 means gathering all publicly accessible linked resources from a user-provided URL within policy. It may produce a source map and unavailable/blocked report.

## Required Gates

- Explicit user approval.
- Domain allowlist.
- Crawl budget.
- Rate limit.
- Robots policy.
- Legal/compliance note.
- Data retention policy.
- No paid API unless allowed.
- No bypass/evasion.
- Dogfood/eval suite.

## Required Limits

- No login/CAPTCHA/paywall/anti-bot bypass.
- No browser automation in the current milestone.
- No binary downloads by default.
- Content labeled `UNTRUSTED_WEB`.
- Network domains audited.
- Blocked sources reported as unavailable.
- Source map separates fetched, snippet-only, robots-blocked, login-blocked, CAPTCHA-blocked, paywall-blocked, binary-blocked, and failed sources.

## Planned Commands

```bash
python smart_agent.py web deep-scan <url> --dry-run
python smart_agent.py web source-map <url>
python smart_agent.py web blocked-report <url>
```

These commands are planned/stubbed only until a future implementation prompt adds ToolBroker-routed behavior and tests.
