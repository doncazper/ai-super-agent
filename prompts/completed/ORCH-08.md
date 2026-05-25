---
prompt_id: ORCH-08
pack_id: agent-runtime-orchestration-v1
title: Runtime doctor/status/commands
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-07"]
status: completed
order: 8
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:14+00:00
completed_at: 2026-05-23T21:31:14+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed; runtime/jobs/workflows/events CLI smoke passed; commands validate passed
docs_updated: yes
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
notes: Added runtime status/doctor/services/features/health, jobs list/show, workflows list/run, and events tail commands.
---

# Prompt

You are Codex working in this repo.

Task:
Add safe runtime doctor/status CLI commands.

Goal:
Expose the runtime orchestrator state to the user without executing tools, calling LM Studio, accessing personal data, or loading heavy services.

Scope:
- Read-only commands.
- Command registry updates.
- Tests.

Non-goals:
- Do not execute tools.
- Do not call LM Studio unless explicitly using the existing doctor command and not in these runtime status commands.
- Do not access personal data.
- Do not initialize platform bridges.
- Do not start scheduler.
- Do not start app bridge.
- Do not start background workers.

Add commands if practical:
- python smart_agent.py runtime status
- python smart_agent.py runtime doctor
- python smart_agent.py runtime services
- python smart_agent.py runtime features
- python smart_agent.py runtime health
- python smart_agent.py jobs list
- python smart_agent.py jobs show <job_id>
- python smart_agent.py workflows list
- python smart_agent.py workflows run <workflow_id>
- python smart_agent.py events tail

Command behavior:
runtime status:
- runtime mode
- boot status
- service count
- feature count
- enabled/disabled/planned counts
- job count
- workflow count
- warnings

runtime doctor:
- runtime kernel loads
- service registry loads
- feature flags load
- audit logger reachable
- policy manifest valid
- command registry status if available
- prompt queue status if available
- no heavy imports
- no personal-data tools enabled by default

runtime services:
- service id
- status
- enabled
- lazy-load state
- setup hint

runtime features:
- feature/capability
- status
- risk
- approval behavior
- enabled/default

runtime health:
- consolidated health report

jobs list/show:
- read-only job metadata
- no job execution

workflows list:
- list workflow metadata

workflows run:
- for now either refuse execution unless explicitly safe, or create a run record that stops at ToolBroker/approval gates.
- if unsure, keep as planned/stubbed and document.

events tail:
- if event bus exists, show redacted recent events.
- otherwise return setup/unavailable.

Requirements:
1. Commands are read-only unless workflows run explicitly handles safe mode.
2. Commands do not access personal data.
3. Commands do not execute tools.
4. Commands do not call LM Studio.
5. Commands do not start scheduler/app bridge/background services.
6. Commands redact secrets.
7. Commands handle missing runtime subsystems gracefully.
8. Commands update COMMAND_REGISTRY.
9. Commands include examples in docs.

Tests:
- runtime status works
- runtime doctor works
- services list works
- features list works
- health works
- jobs list/show safe
- workflows list safe
- workflows run refuses unknown/high-risk workflow
- no LM Studio call
- no tool execution
- no personal data
- command registry validation passes

Update:
- README.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/runtime/RUNTIME_ORCHESTRATION_STRATEGY.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run:
- targeted tests
- full tests if practical
- startup policy validation
- command registry validation

Final report:
- commands added
- tests run/results
- example command output
- next recommended prompt
