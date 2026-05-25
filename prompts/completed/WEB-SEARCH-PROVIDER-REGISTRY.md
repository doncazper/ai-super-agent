prompt_id: WEB-SEARCH-PROVIDER-REGISTRY
title: Search Provider Registry
status: completed
category: web-acquisition
source: user
started_at: 2026-05-24
completed_at: 2026-05-24
previous_prompt_id: WEB-ROBOTS-SITEMAP-FEED-SUPPORT
next_prompt_id: SEARXNG-PROVIDER

## Scope

Build Search Provider Registry v1 as a metadata, interface, normalization, error, command, docs, and test milestone for future search providers.

## Non-Goals

- No new live provider implementation.
- No public SearXNG default.
- No paid API default.
- No query-history or web-content memory storage.
- No CAPTCHA, login-wall, proxy, Cloudflare, or anti-bot bypass.
- No ToolBroker, PolicyEngine, or AuditLogger bypass.

## Evidence

- Added `agent.web_acquisition.search` provider interface, models, normalization, errors, registry, and tests.
- Added brokered `web.search_providers` capability/tool plus `python smart_agent.py web search-providers`.
- Generalized `python smart_agent.py web search "<query>" --provider <provider>` handling so unknown/missing registry providers return normalized errors and setup hints.
- Updated README, command registry/test matrix, web docs, feature registry, maturity tracker, roadmap, risk register, threat model, test plan, release checklist, project state, changelog, prompt tracking, and completion report.

## Validation

- `./.venv/bin/python -m pytest tests/test_search_provider_registry.py tests/test_web.py -q` passed: 33 passed.
- `./.venv/bin/python -m pytest tests/test_command_registry.py tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py -q` passed: 22 passed.
- `./.venv/bin/python -m pytest -q` passed: 848 passed, 2 skipped.
- `./scripts/agent commands validate` passed with 312 commands.
- Startup policy validation passed.
- Capability manifest validation passed with 129 capabilities.
- `./scripts/agent prompts audit` passed with 133 completed prompts and `SEARXNG-PROVIDER` next.
