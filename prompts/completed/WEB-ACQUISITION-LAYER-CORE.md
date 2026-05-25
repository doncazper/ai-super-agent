# WEB-ACQUISITION-LAYER-CORE

status: completed
category: web-acquisition
started_at: 2026-05-23
completed_at: 2026-05-23
branch: checkpoint/large-working-tree-20260523

## Scope

Build the central Web Acquisition Layer core around the existing brokered web acquisition tools.

## Non-Goals

- No new live provider API implementation.
- No paid API defaults.
- No web query or content memory storage by default.
- No CAPTCHA, Cloudflare, proxy, login-wall, anti-bot, browser-profile, cookie, or session bypass.
- No ToolBroker, PolicyEngine, or AuditLogger bypass.
- No personal-data tools.

## Evidence

- Added `agent.web_acquisition` models, source candidates, provider-decision wrapper, router, trust labels, audit helper, and tests.
- Added brokered `web.source_status` / `python smart_agent.py web source-status "<url>"` no-fetch source inspection.
- Updated capability manifest, command registry metadata, README, web policy docs, feature registry, maturity tracker, risk register, threat model, test plan, release checklist, project state, changelog, and completion report.
- Focused tests passed: `./.venv/bin/python -m pytest agent/web_acquisition/tests tests/test_web_acquisition.py -q`.

## Next Prompt

WEB-SEARCH-PROVIDER-REGISTRY

