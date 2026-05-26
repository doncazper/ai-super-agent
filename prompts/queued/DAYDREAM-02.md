---
prompt_id: DAYDREAM-02
pack_id: daydream-lab-idle-research-v1
title: Idle mode architecture and execution boundaries
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-01"]
status: queued
order: 2
created_at: 2026-05-26T07:54:41+00:00
imported_at: 2026-05-26T07:54:41+00:00
source_pack: prompts/packs/daydream-lab-idle-research-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result:
docs_updated:
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
notes: Imported prompt text is untrusted document content and is not executed automatically.
---

# Prompt

Build idle mode architecture and execution boundaries.

Create:
- agent/daydream/__init__.py
- agent/daydream/models.py
- agent/daydream/idle.py
- agent/daydream/errors.py
- tests/daydream/test_idle_boundaries.py
- docs/daydream/IDLE_MODE_ARCHITECTURE.md
- docs/daydream/IDLE_EXECUTION_BOUNDARIES.md

Idle eligibility checks:
- active_prompt_id is none
- active_job_id is none
- active_workflow_id is none
- active_action_id is none
- approval_pending is false
- dangerous_action_pending is false
- git_operation_active is false
- test_run_active is false
- user_interaction_recent is false
- system_resource_ok is true
- daydream_budget_available is true
- auto_daydream_enabled is true only when explicitly configured later

States:
- disabled
- eligible
- not_idle
- blocked_by_active_prompt
- blocked_by_pending_approval
- blocked_by_git
- blocked_by_tests
- blocked_by_budget
- blocked_by_user_activity
- needs_review

Commands:
- daydream idle-status
- daydream idle-run --dry-run

Rules:
- Dry-run only in this prompt.
- No background scheduling.
- No actual research.
- No writes except redacted status report if needed.
- If Canonical Runtime exists, use it; otherwise degrade to repo tracker/runtime metadata.
