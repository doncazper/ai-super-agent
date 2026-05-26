# Authorized Web Automation Policy

This policy defines what future browser automation or deep scanning may do. It does not enable browser automation today.

## Allowed Only With Explicit Scope

- First-party staging app testing.
- Official CAPTCHA/Turnstile/reCAPTCHA test keys.
- User-in-the-loop manual login where the user controls the session.
- Official APIs/OAuth.
- Approved partner access.
- Contracted security testing with written scope.
- User-provided exports.
- Browser selected-page handoff where the user controls the session.

## Forbidden For Third-Party Or Unauthorized Sites

- CAPTCHA bypass.
- Cloudflare or anti-bot bypass.
- Proxy evasion.
- Rate-limit evasion.
- Login-wall bypass.
- Paywall bypass.
- Cookie/session scraping.
- Human impersonation.
- Stealth browser automation.

## Required Behavior

Blocked sources return `blocked` or `unavailable` with a reason and `bypass_attempted=false`. The agent must not retry through stealth, alternate identities, session theft, proxy rotation, or CAPTCHA solving.

Future automation must route through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager when required, and AuditLogger.
