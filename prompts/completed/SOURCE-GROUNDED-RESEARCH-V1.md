# Prompt Record: SOURCE-GROUNDED-RESEARCH-V1

prompt_id: SOURCE-GROUNDED-RESEARCH-V1
title: Source-grounded research workflow v1
category: web-acquisition
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on:
- WEB-FETCH-EXTRACTION-HARDENING
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
- PROVIDER-COST-POLICY
related_files:
- agent/workflows/research.py
- smart_agent.py
- agent/ui/command_registry.py
files_expected:
- agent/workflows/research.py
- docs/web/SOURCE_GROUNDED_RESEARCH.md
files_changed:
- agent/workflows/research.py
- smart_agent.py
- agent/ui/command_registry.py
- tests/test_workflows.py
- docs/web/SOURCE_GROUNDED_RESEARCH.md
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
- Brokered source-grounded research workflow
- Real URL source list with retrieved timestamps and provider metadata
- Structured coverage/limitations and fetch-failure reporting
commands_expected:
- python smart_agent.py research "query"
- python smart_agent.py research "query" --provider auto
- python smart_agent.py research "query" --max-sources 5
- python smart_agent.py research "query" --freshness recent
- python smart_agent.py research "query" --no-fetch
commands_run:
- ./.venv/bin/python -m pytest tests/test_workflows.py -q -k 'source_grounded_research'
- ./.venv/bin/python -m pytest tests/test_workflows.py tests/test_web.py tests/test_command_registry.py -q
- ./.venv/bin/python -m pytest -q
tests_expected:
- mocked research workflow tests
- command registry validation
- startup policy validation
- capability manifest validation
- full suite if feasible
tests_run: focused source-grounded workflow tests 14 passed; targeted workflow/web/command tests 128 passed; feature/prompt docs tests 17 passed; full suite 879 passed, 2 skipped; startup policy ok; capability manifest ok with 134 capabilities; command registry ok with 320 commands
test_result: pass
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links:
- docs/web/SOURCE_GROUNDED_RESEARCH.md
- docs/COMPLETION_REPORT.md
blockers: none
next_prompt_id: INTERNET-ROUTING-POLICY
supersedes:
superseded_by:
notes: No fabricated citations, paid API default, live provider call, query-history persistence, web-content memory storage, CAPTCHA/login/paywall/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/AuditLogger bypass was added.
