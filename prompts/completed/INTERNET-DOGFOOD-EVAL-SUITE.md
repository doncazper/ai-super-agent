---
prompt_id: INTERNET-DOGFOOD-EVAL-SUITE
title: Internet Access dogfood/eval suite and release gate
category: web-acquisition
status: completed
created_at: 2026-05-24
started_at: 2026-05-24
completed_at: 2026-05-24
branch: checkpoint/large-working-tree-20260523
next_prompt_id: REDDIT-FORUM-INTELLIGENCE-TRACK
---

# Completion Evidence

Implemented mock-first Internet Access dogfood and eval release-gate coverage:

- Added `internet_core`, `web_providers`, `web_fetch`, `web_research`, and `web_blocked_sources` dogfood suites.
- Added recursive `eval_cases/internet/` loading and fixture-backed `eval run --internet` / `eval report --internet`.
- Added `docs/web/INTERNET_DOGFOOD_RUNBOOK.md`.
- Added command registry entries for the internet eval commands and regenerated command docs.

Safety invariants:

- No live provider calls in internet evals.
- No paid provider default.
- No CAPTCHA, login-wall, paywall, anti-bot, proxy-evasion, or browser-automation bypass.
- No personal-data tools.
- No search history or full web-content memory write by default.
- Web/source content remains `UNTRUSTED_WEB`.
- Dogfood commands delegate to existing ToolBroker/PolicyEngine/AuditLogger paths.

Validation:

- `./.venv/bin/python -m pytest tests/test_internet_dogfood_eval.py tests/test_dogfood_suites.py -q`: 19 passed.
- `./.venv/bin/python -m pytest tests/test_internet_dogfood_eval.py tests/test_command_registry.py -q`: 10 passed.
- `./.venv/bin/python smart_agent.py eval run --internet`: 5 passed, 0 failed, 5 skipped personal-data evals.
- Dogfood dry-runs for `internet_core`, `web_research`, `web_providers`, `web_fetch`, and `web_blocked_sources`: ok.
- `./.venv/bin/python -m pytest tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py tests/test_command_registry.py -q`: 22 passed.
- `./.venv/bin/python -m pytest -q`: 918 passed, 2 skipped.
- Startup policy validation passed.
- Capability manifest validation passed with 143 capabilities.
- Command registry validation passed with 334 commands.
- Prompt audit passed with `REDDIT-FORUM-INTELLIGENCE-TRACK` queued next.
