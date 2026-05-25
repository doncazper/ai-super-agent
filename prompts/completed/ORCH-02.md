---
prompt_id: ORCH-02
pack_id: agent-runtime-orchestration-v1
title: Runtime package scaffolding and models
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-01"]
status: completed
order: 2
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:10+00:00
completed_at: 2026-05-23T21:31:11+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed
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
notes: Added runtime models, errors, state, serialization, validation, and tests.
---

# Prompt

You are Codex working in this repo.

Task:
Create runtime package scaffolding and core models.

Goal:
Add lightweight, platform-neutral runtime scaffolding that can represent services, features, workflows, jobs, runtime state, and health without executing tools or loading heavy modules.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- docs/runtime/RUNTIME_ORCHESTRATION_STRATEGY.md
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/STARTUP_OVERHEAD_POLICY.md
- docs/PROJECT_STATE.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md

Scope:
- Add lightweight runtime package and dataclasses/models.
- No real orchestration side effects.
- No tool execution.
- No background services.
- No personal-data access.

Non-goals:
- Do not run workflows.
- Do not call LM Studio.
- Do not start a scheduler.
- Do not start app bridge server.
- Do not import platform/native libraries.
- Do not add send/write behavior.

Create:
- agent/runtime/__init__.py
- agent/runtime/models.py
- agent/runtime/errors.py
- agent/runtime/state.py
- tests/runtime/test_runtime_models.py
- tests/runtime/test_runtime_state.py

Models:
- RuntimeMode
- RuntimeStatus
- RuntimeHealthStatus
- RuntimeServiceStatus
- RuntimeFeatureStatus
- RuntimeWorkflowStatus
- RuntimeJobStatus
- RuntimeEventType
- RuntimeServiceInfo
- RuntimeFeatureInfo
- RuntimeWorkflowInfo
- RuntimeJobInfo
- RuntimeHealthReport
- RuntimeStateSnapshot
- RuntimeErrorBase
- RuntimeUnsupportedError
- RuntimeUnavailableError
- RuntimePolicyBlockedError

RuntimeMode values:
- cli
- interactive_cli
- mac_app_bridge
- ios_companion_bridge
- windows_app_bridge
- web_dashboard
- test
- unknown

Requirements:
1. Models must be JSON-serializable.
2. Models must not import heavy modules.
3. Runtime state must not include raw secrets.
4. Runtime state must not include raw personal data.
5. Missing fields should fail validation clearly or have safe defaults.
6. Status values should distinguish available, unavailable, disabled, planned, stubbed, blocked, and error.
7. Health reports should support warnings and failures.
8. No runtime code should execute tools.
9. No model should require LM Studio.
10. Tests should run without network/personal data.

Tests:
- models serialize to dict/JSON
- required fields validated
- secrets redaction helper used or raw secret fields rejected
- unknown status handled
- state snapshot includes no personal data
- import runtime package does not import core heavy modules unnecessarily
- test runtime mode works

Update:
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/RUNTIME_CONTROL_PLANE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run:
- targeted runtime tests
- full tests if practical
- startup policy validation

Final report:
- files created
- tests run/results
- models added
- overhead notes
- next recommended prompt
