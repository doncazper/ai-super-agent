---
prompt_id: HERMES-11
pack_id: hermes-inspired-safe-autonomy-v1
title: Authorized web automation boundary
category: web
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-10"]
status: completed
order: 11
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:48:10+00:00
completed_at: 2026-05-25T18:51:58+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 24 focused docs/feature/command tests passed; command registry validation ok with 481 commands; startup policy and capability manifest validation passed via make policy-check
docs_updated: docs/decisions/authorized_web_automation_boundary.md; docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md; docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md; docs/web/FIRST_PARTY_TESTING_POLICY.md; docs/web/DEEP_SCAN_POLICY.md; docs/COMMAND_REGISTRY.md; docs/COMMAND_TEST_MATRIX.md; docs/FEATURE_REGISTRY.md; docs/FEATURE_MATURITY.md; docs/FEATURE_ROADMAP.md; docs/RISK_REGISTER.md; docs/THREAT_MODEL.md; docs/RELEASE_CHECKLIST.md; CHANGELOG.md
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Completed HERMES-11 docs-only authorized web automation boundary. Added planned command tracking for future deep-scan/source-map/blocked-report only. No browser automation, no CAPTCHA/Cloudflare/anti-bot/proxy/rate-limit/login/paywall/cookie/session bypass, no human impersonation, no stealth automation, no network calls, no paid APIs, no memory write, and no safety-control bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Create Authorized Web Automation Boundary.

Goal:
Document and scaffold a safe policy boundary for future browser automation and user-requested deep web scanning. The user eventually wants to ask the agent to gather as much information as possible from a webpage. This prompt must explicitly prohibit unauthorized CAPTCHA/Cloudflare/anti-bot/paywall/login-wall bypass and define allowed first-party/authorized testing paths.

Scope:
- Decision record.
- Policy docs.
- Risk gates.
- Test fixtures for blocked/unavailable behavior.
- No browser automation implementation.
- No bypass implementation.

Non-goals:
- Do not implement CAPTCHA bypass.
- Do not implement Cloudflare bypass.
- Do not implement anti-bot evasion.
- Do not implement proxy rotation/evasion.
- Do not impersonate humans.
- Do not bypass login walls or paywalls.
- Do not add browser automation.
- Do not scrape third-party sites beyond existing compliant fetch/search policy.

Create:
- docs/decisions/authorized_web_automation_boundary.md
- docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md
- docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md
- docs/web/FIRST_PARTY_TESTING_POLICY.md
- docs/web/DEEP_SCAN_POLICY.md
- tests/web/test_authorized_web_automation_policy.py, if web tests exist

Policy:
Forbidden for third-party or unauthorized sites:
- CAPTCHA bypass
- Cloudflare/anti-bot bypass
- proxy evasion
- rate-limit evasion
- login-wall bypass
- paywall bypass
- cookie/session scraping
- human impersonation
- stealth browser automation

Allowed only when explicitly documented and scoped:
- first-party staging app testing
- official CAPTCHA/Turnstile/reCAPTCHA test keys
- user-in-the-loop manual login
- official APIs/OAuth
- approved partner access
- contracted security testing with written scope
- user-provided exports
- browser selected-page handoff where user controls session

Deep scan v1 definition:
- gather all publicly accessible linked resources from a user-provided URL within policy
- respect robots/crawl policy
- rate limit
- no login/CAPTCHA/paywall bypass
- no binary downloads by default
- produce source map and unavailable/blocked report
- content is UNTRUSTED_WEB
- audit all network domains

Future deep scan gates:
- explicit user approval
- domain allowlist
- crawl budget
- rate limit
- robots policy
- legal/compliance note
- data retention policy
- no paid API unless allowed
- no bypass/evasion
- dogfood/eval suite

Requirements:
1. Blocked sources return blocked/unavailable, not bypass attempts.
2. Tests/fixtures verify blocked-source behavior.
3. Router/doctor/docs should use this language.
4. Command registry updated only for planned/stubbed future commands:
   - python smart_agent.py web deep-scan <url> --dry-run
   - python smart_agent.py web source-map <url>
   - python smart_agent.py web blocked-report <url>
5. Feature maturity should mark deep scan as planned/stubbed, not implemented.

Update:
- docs/RISK_REGISTER.md.
- docs/THREAT_MODEL.md.
- docs/FEATURE_ROADMAP.md.
- docs/FEATURE_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMMAND_REGISTRY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- policy boundary created
- blocked behavior documented
- tests run/results
- next recommended prompt
