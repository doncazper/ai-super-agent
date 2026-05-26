---
prompt_id: CANON-01
pack_id: canonical-runtime-gateway-hardening-v1
title: Canonical runtime state model and source-of-truth hierarchy
category: runtime
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:45:56+00:00
completed_at: 2026-05-26T04:55:45+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted runtime tests 13 passed; command registry validation passed with 564 commands; startup policy and capability manifest validation passed via make policy-check
docs_updated: true
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
notes: CANON-01 added read-only canonical runtime state model, source-of-truth hierarchy, reconciliation preview, runtime commands, docs, command registry rows, and tests.
---

# Prompt

You are Codex working in this repo.

Task:
Create Canonical Runtime State model and source-of-truth hierarchy.

Goal:
Define a single canonical machine-readable runtime state model that future CLI/dashboard/app/channel surfaces can read, while keeping markdown trackers as human-readable summaries. This borrows runtime-truth concepts without rewriting the repo.

Before making changes, read SPEC.md, docs/SDLC.md, AGENTS.md, README.md, CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md if present, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/RELEASE_CHECKLIST.md, docs/PROMPT_LEDGER.md if present, docs/PROMPT_QUEUE.md if present, docs/PROMPT_AUDIT.md if present, docs/runtime/ if present, agent/runtime/ if present, tests/runtime/ if present.

Scope:
- Canonical runtime state docs.
- Data models/schema.
- Source-of-truth hierarchy.
- Read-only metadata commands if practical.
- Tests.
- No runtime rewrite.

Non-goals:
- Do not replace markdown trackers yet.
- Do not delete tracker history.
- Do not create a daemon.
- Do not start background persistence.
- Do not alter ToolBroker/Policy/Audit behavior.

Create or update:
- docs/runtime/CANONICAL_RUNTIME_STATE_MODEL.md
- docs/runtime/SOURCE_OF_TRUTH_HIERARCHY.md
- docs/runtime/CANONICAL_STATE_BOUNDARIES.md
- docs/decisions/canonical_runtime_state.md
- agent/runtime/canonical_state.py
- tests/runtime/test_canonical_runtime_state.py

Define canonical state fields:
- schema_version, generated_at, branch, last_commit, dirty_worktree_summary
- active_prompt_id, active_prompt_pack, active_job_id, active_workflow_id, active_session_id, active_action_id
- current_phase, current_status, next_prompt_id, last_completed_prompt_id, blocked_reason, resume_instruction
- last_test_result, last_policy_check, last_capability_check, last_command_registry_check, last_prompt_audit
- safety_summary, tracker_summary, evidence_links, updated_by

Define source-of-truth hierarchy:
1. SPEC.md
2. docs/SDLC.md
3. AGENTS.md
4. config/capabilities.yaml
5. actual code/tests
6. canonical runtime state JSON/model
7. COMMAND_REGISTRY
8. FEATURE_REGISTRY / FEATURE_MATURITY
9. PROMPT_LEDGER / PROMPT_QUEUE / PROMPT_AUDIT
10. PROJECT_STATE / COMPLETION_REPORT / CHANGELOG
11. summary dashboards

Commands if practical:
- python smart_agent.py runtime canonical-state
- python smart_agent.py runtime source-of-truth
- python smart_agent.py runtime reconcile-preview

Requirements:
- JSON-serializable.
- No secrets/personal data.
- No tool execution/provider calls.
- Existing trackers remain intact.
- Tests cover serialization and conflict markers.
Update docs/tracking and run targeted tests and validations.
