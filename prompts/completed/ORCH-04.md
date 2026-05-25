---
prompt_id: ORCH-04
pack_id: agent-runtime-orchestration-v1
title: Runtime lifecycle and kernel
category: feature
risk_level: LOW
approval_gate: false
depends_on: ["ORCH-03"]
status: completed
order: 4
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:12+00:00
completed_at: 2026-05-23T21:31:12+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed; runtime status/doctor smoke passed
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
notes: Added lightweight runtime kernel and lifecycle/status/health checks with no LM Studio/tool/personal-data/background calls.
---

# Prompt

You are Codex working in this repo.

Task:
Build AgentRuntimeKernel and LifecycleManager.

Goal:
Create a lightweight runtime kernel that coordinates initialization, status, health, service registry access, feature flags, and shutdown without executing tools or loading heavy services by default.

Scope:
- Runtime kernel.
- Lifecycle manager.
- Status/health aggregation.
- Tests.
- No risky execution.

Non-goals:
- Do not replace the existing orchestrator chat loop.
- Do not execute tools.
- Do not call LM Studio.
- Do not start background workers.
- Do not start scheduler.
- Do not start app bridge server.
- Do not access personal data.
- Do not enable new features.

Create:
- agent/runtime/kernel.py
- agent/runtime/lifecycle.py
- tests/runtime/test_runtime_kernel.py
- tests/runtime/test_runtime_lifecycle.py

AgentRuntimeKernel methods:
- boot()
- shutdown()
- status()
- health()
- list_services()
- list_features()
- list_workflows()
- list_jobs()
- get_state_snapshot()

LifecycleManager responsibilities:
- track boot state
- track shutdown state
- record boot warnings/errors
- expose safe lifecycle events
- prevent duplicate boot
- safe no-op shutdown when not booted
- no background persistence

Requirements:
1. Boot must be lightweight.
2. Boot must not execute tools.
3. Boot must not call LM Studio.
4. Boot must not access personal data.
5. Boot must not load platform/native bridge modules.
6. Boot must not start scheduler or event loop workers.
7. status() must be safe and read-only.
8. health() must aggregate registry/feature/audit/config state if safe.
9. shutdown() must not delete data or kill unrelated processes.
10. Runtime must work in test mode.

Tests:
- kernel boots once
- duplicate boot handled
- shutdown before boot safe
- status returns snapshot
- health returns report
- no LM Studio call during boot/status/health
- no tool execution during boot/status/health
- no personal-data access
- registry integrated
- feature flags integrated
- import/startup overhead reasonable

Update:
- docs/runtime/RUNTIME_LIFECYCLE.md
- docs/runtime/STARTUP_OVERHEAD_POLICY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- kernel added
- lifecycle added
- tests run/results
- overhead observations
- next recommended prompt
