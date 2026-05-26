# First-Party Testing Policy

First-party testing is allowed only when the user has authority over the target and scope is explicit.

Allowed examples:

- Localhost or staging app testing owned by the user.
- Official CAPTCHA/Turnstile/reCAPTCHA test keys.
- Test accounts created for the app under test.
- Written partner or contracted security-testing scope.

Required controls:

- Explicit target domain or app.
- Approval before automation.
- No credential harvesting.
- No stealth or human impersonation.
- Rate limits and crawl budgets.
- Audit of domains, actions, and blocked results.
- Data retention plan.

If the agent cannot verify that the target is first-party or explicitly authorized, it must treat the target as third-party and apply the stricter blocked-source policy.
