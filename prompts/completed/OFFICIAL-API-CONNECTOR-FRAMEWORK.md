---
prompt_id: OFFICIAL-API-CONNECTOR-FRAMEWORK
title: Official API Connector Framework for web sources
category: web-acquisition
status: completed
created_at: 2026-05-24
started_at: 2026-05-24
completed_at: 2026-05-24
branch: checkpoint/large-working-tree-20260523
next_prompt_id: INTERNET-DOGFOOD-EVAL-SUITE
---

# Completion Evidence

Implemented local framework/stub v1 for official API providers:

- Added `agent.web_acquisition.official_apis` interfaces, models, registry, GitHub/Wikipedia/arXiv/Reddit stubs, domain matching, setup/error normalization, and mocked public result normalization.
- Added brokered tools and CLI commands for `web official-apis`, `web api-status <provider>`, and `web api-search <provider> "<query>"`.
- Added capability manifest entries and command registry/test matrix entries.
- Added docs at `docs/web/OFFICIAL_API_CONNECTORS.md` and provider docs under `docs/web/providers/`.

Safety invariants:

- No live API calls by default.
- No credentials committed.
- No high-risk personal connectors.
- No write operations.
- No Reddit web scraping substitute.
- No search history or article body memory storage.
- Web/API results remain `UNTRUSTED_WEB`.
- Tool execution remains ToolBroker/PolicyEngine/AuditLogger-routed.

Validation:

- `./.venv/bin/python -m pytest tests/test_official_api_connectors.py -q`: 9 passed.
- `./.venv/bin/python -m pytest tests/test_official_api_connectors.py tests/test_command_registry.py -q`: 14 passed.
- `./.venv/bin/python -m pytest tests/test_web.py tests/test_search_provider_registry.py tests/test_web_cache_index.py tests/test_official_api_connectors.py -q`: 74 passed.
- `./.venv/bin/python -m pytest tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py -q`: 17 passed.
- `./.venv/bin/python -m pytest -q`: 913 passed, 2 skipped.
- Startup policy validation passed.
- Capability manifest validation passed with 143 capabilities.
- Command registry validation passed with 332 commands.
