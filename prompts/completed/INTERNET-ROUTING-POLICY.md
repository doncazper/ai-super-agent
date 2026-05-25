# Prompt Record: INTERNET-ROUTING-POLICY

prompt_id: INTERNET-ROUTING-POLICY
title: Router internet-only-when-needed behavior
category: web-acquisition
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on:
- SOURCE-GROUNDED-RESEARCH-V1
status: completed
source: user
created_at: 2026-05-24
pasted_to_codex: 2026-05-24
started_at: 2026-05-24
completed_at: 2026-05-24
branch: checkpoint/large-working-tree-20260523
commit_hash:
related_feature_ids:
- CONN-WEB
- INTERNET-ROUTING-POLICY
related_files:
- agent/core/router.py
- agent/ui/preflight.py
- agent/ui/cli_commands.py
- agent/ui/command_registry.py
files_expected:
- agent/core/router.py
- docs/web/INTERNET_ROUTING_POLICY.md
files_changed:
- agent/core/router.py
- agent/ui/preflight.py
- agent/ui/cli_commands.py
- agent/ui/command_registry.py
- tests/test_router.py
- tests/test_preflight.py
- tests/test_model_quality_evals.py
- eval_cases/model_router_prompt_quality.json
- docs/web/INTERNET_ROUTING_POLICY.md
- README.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/TEST_PLAN.md
- docs/RELEASE_CHECKLIST.md
- docs/PROJECT_STATE.md
- docs/PROMPT_QUEUE.md
- docs/PROMPT_LEDGER.md
- docs/PROMPT_AUDIT.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md
expected_outputs:
- Deterministic internet routing metadata
- Read-only `router explain` command
- Preflight internet-routing fields
commands_expected:
- python smart_agent.py router explain "query"
- python smart_agent.py preflight "query"
commands_run:
- ./.venv/bin/python -m pytest tests/test_router.py tests/test_preflight.py -q
- ./.venv/bin/python -m pytest tests/test_router.py tests/test_preflight.py tests/test_model_quality_evals.py tests/test_command_registry.py -q
- ./.venv/bin/python smart_agent.py router explain "What is the latest OpenAI API pricing?"
- ./.venv/bin/python smart_agent.py preflight "What is the latest OpenAI API pricing?"
- ./.venv/bin/python -m pytest -q
- ./.venv/bin/python -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy(); print('startup policy ok')"
- ./.venv/bin/python smart_agent.py commands validate
- ./.venv/bin/python smart_agent.py prompts audit
tests_expected:
- router/preflight tests
- command validation
- startup policy validation
- capability manifest validation
- full suite if feasible
tests_run: focused router/preflight tests 34 passed; targeted router/preflight/model-quality/command-registry tests 48 passed; final full suite 889 passed, 2 skipped; startup policy ok; capability manifest ok with 134 capabilities; command registry ok with 321 commands; prompt audit ok with zero active prompts, 138 completed prompts, one queued prompt, and `CITATION-SOURCE-ATTRIBUTION` next
test_result: pass
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links:
- docs/web/INTERNET_ROUTING_POLICY.md
- docs/COMPLETION_REPORT.md
blockers: none
next_prompt_id: CITATION-SOURCE-ATTRIBUTION
supersedes:
superseded_by:
notes: No provider call during routing, no LLM router by default, no user-message rewrite, no web/query memory persistence, no paid API default, no CAPTCHA/login/paywall/anti-bot bypass, no browser automation, no personal-data tool enablement, and no ToolBroker/PolicyEngine/AuditLogger bypass was added.
