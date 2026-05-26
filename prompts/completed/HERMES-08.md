---
prompt_id: HERMES-08
pack_id: hermes-inspired-safe-autonomy-v1
title: Sandbox backend abstraction
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-07"]
status: completed
order: 8
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:17:22+00:00
completed_at: 2026-05-25T18:23:24+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused sandbox abstraction tests passed with 10 passed; combined sandbox abstraction plus feature maturity docs tests passed with 23 passed; command registry validation passed with 471 commands; make policy-check passed
docs_updated: README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, RISK_REGISTER, THREAT_MODEL, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Completed HERMES-08 as mock-only sandbox backend abstraction; no arbitrary command execution, sandbox process startup, Docker/VM/browser/cloud runtime, networked sandbox, broad filesystem access, personal-data access, plugin runtime, background persistence, or safety-control bypass.
---

# Prompt

You are Codex working in this repo.

Task:
Build sandbox backend abstraction.

Goal:
Prepare a pluggable sandbox abstraction for future code execution, browser automation, subagents, and self-improvement, while keeping all risky sandbox execution disabled or mock-only by default.

Scope:
- Sandbox backend interface.
- Mock/local workspace-safe backend.
- Policy docs.
- Tests.
- No Docker/VM installation.
- No browser automation.

Non-goals:
- Do not install Docker or sandbox tools.
- Do not execute arbitrary code.
- Do not run browser automation.
- Do not enable networked sandbox.
- Do not grant broad filesystem access.
- Do not run untrusted scripts.

Create:
- agent/sandbox/
  - __init__.py
  - base.py
  - models.py
  - registry.py
  - mock_backend.py
  - policy.py
  - errors.py
- tests/sandbox/test_sandbox_abstraction.py
- docs/autonomy/SANDBOX_BACKEND_ABSTRACTION.md
- docs/autonomy/SANDBOX_POLICY.md

Sandbox backend types:
- mock
- local_workspace_safe
- docker_rootless, planned
- macos_sandbox, planned
- firecracker_vm, planned
- browser_sandbox, planned
- cloud_sandbox, deferred

Sandbox request fields:
- sandbox_id
- task_type
- risk_level
- network_allowed
- filesystem_roots
- time_limit_seconds
- memory_limit_mb
- command_allowlist
- personal_data_allowed
- audit_required

Requirements:
1. Mock backend only by default.
2. No arbitrary command execution.
3. No network by default.
4. Workspace roots only.
5. Personal data not allowed by default.
6. Sandbox cannot bypass ToolBroker/PolicyEngine.
7. All sandbox operations auditable.
8. Docker/VM/browser/cloud backends planned/stubbed only.
9. Clear setup hints.
10. Command registry updated.

Commands:
- python smart_agent.py sandbox backends
- python smart_agent.py sandbox policy
- python smart_agent.py sandbox dry-run

Tests:
- mock backend works.
- unknown backend denied.
- network disabled by default.
- personal data disabled.
- arbitrary command rejected.
- planned backend returns setup/stub.
- command registry updated.

Update docs/tracking.

Final report:
- sandbox abstraction added
- tests run/results
- next recommended prompt
