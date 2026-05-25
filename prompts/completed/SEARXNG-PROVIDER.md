prompt_id: SEARXNG-PROVIDER
title: SearXNG Search Provider
status: completed
category: web-acquisition
source: user
started_at: 2026-05-24
completed_at: 2026-05-24
previous_prompt_id: WEB-SEARCH-PROVIDER-REGISTRY
next_prompt_id: BRAVE-PROVIDER

## Scope

Implement a configured/self-hosted-only SearXNG search provider before paid APIs, including config defaults, explicit CLI routing, config-only doctor/status metadata, tests, docs, command registry, and tracking updates.

## Non-Goals

- No public SearXNG instance default.
- No Brave or SerpAPI implementation in this prompt.
- No paid API default.
- No search-history or web-content memory storage.
- No browser automation.
- No CAPTCHA, Cloudflare, proxy, login-wall, or anti-bot bypass.
- No personal-data tools.
- No ToolBroker, PolicyEngine, or AuditLogger bypass.

## Evidence

- Added `SearXngSearchProvider` with disabled-by-default env config, configured base URL requirement, JSON result normalization, setup hints, and timeout/403/429/malformed-response handling.
- Added brokered `web.searxng.doctor` and CLI `python smart_agent.py web searxng doctor`.
- Added `python smart_agent.py web search "query" --provider searxng` routing through the existing brokered `web.search` path.
- Added `python smart_agent.py connectors status searxng` metadata support.
- Updated `.env.example`, README provider setup, SearXNG provider docs, command registry/test matrix, feature registry, maturity tracker, roadmap, risk register, threat model, test plan, release checklist, project state, changelog, prompt tracking, and completion report.

## Validation

- `./.venv/bin/python -m pytest tests/test_web.py tests/test_search_provider_registry.py tests/test_connectors.py tests/test_connector_framework.py -q` passed: 58 passed.
- `./.venv/bin/python -m pytest tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py tests/test_prompt_tracker_maturity.py tests/test_secret_config_doctor.py -q` passed: 34 passed.
- `./.venv/bin/python -m pytest tests/test_prompt_tracking.py -q` passed after the next-prompt expectation update: 5 passed.
- `./.venv/bin/python -m pytest -q` passed: 857 passed, 2 skipped.
- Startup policy validation passed.
- Capability manifest validation passed with 130 capabilities.
- `./.venv/bin/python smart_agent.py commands validate` passed with 314 commands.
- `./.venv/bin/python smart_agent.py prompts audit` passed with 134 completed prompts and `BRAVE-PROVIDER` next.
