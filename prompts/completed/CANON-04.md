---
prompt_id: CANON-04
pack_id: canonical-runtime-gateway-hardening-v1
title: Resume, recovery, and checkpoint model
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-03"]
status: completed
order: 4
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:04:41+00:00
completed_at: 2026-05-26T05:08:19+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted runtime tests 32 passed; command registry validation passed with 574 commands; startup policy and capability manifest validation passed via make policy-check
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
notes: CANON-04 added checkpoint/recovery contracts, preview-only recovery commands, docs, command registry rows, and tests.
---

# Prompt

Create durable checkpoint and recovery model for interrupted prompt packs, QA runs, workflows, self-improvement/code operations, and future frontend/channel actions.

Create/update:
- docs/runtime/RESUME_RECOVERY_CHECKPOINT_MODEL.md
- docs/runtime/RECOVERY_REPORTS.md
- agent/runtime/checkpoints.py
- agent/runtime/recovery.py
- tests/runtime/test_resume_recovery_checkpoints.py

Checkpoint fields:
- checkpoint_id, record_id, created_at, kind, state_hash, input_hash, output_hash, artifact_hashes
- current_step, completed_steps, remaining_steps, approval_state, audit_ids
- resume_command, rollback_plan, safe_to_resume, human_review_required, notes

Recovery report fields:
- report_id, generated_at, interrupted_record, last_checkpoint, files_changed, commands_run, tests_run, docs_updated, blockers, safe_next_action, unsafe_actions_to_avoid

Commands if practical:
- python smart_agent.py runtime recovery-preview
- python smart_agent.py runtime checkpoints list
- python smart_agent.py runtime checkpoints show <checkpoint_id>

Rules:
- Recovery preview does not resume automatically.
- Active approval gates remain active.
- CRITICAL action resume requires fresh explicit approval.
- Prompt-pack resume uses prompt tracker evidence.
- Redacted only; no secrets/personal data.
Add tests for an interrupted prompt-pack scenario.
