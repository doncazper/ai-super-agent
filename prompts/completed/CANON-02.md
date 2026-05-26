---
prompt_id: CANON-02
pack_id: canonical-runtime-gateway-hardening-v1
title: Durable job, workflow, and prompt execution records
category: runtime
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-01"]
status: completed
order: 2
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:55:50+00:00
completed_at: 2026-05-26T05:00:35+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: targeted runtime tests 19 passed; command registry validation passed with 568 commands; startup policy and capability manifest validation passed via make policy-check
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
notes: CANON-02 added durable execution record contracts, read-only runtime records commands, docs, command registry rows, and tests.
---

# Prompt

Create durable job, workflow, command, prompt, QA, self-heal, and approval-gated resume record contracts owned by the future Agent Gateway / Runtime Kernel.

Create/update:
- docs/runtime/DURABLE_EXECUTION_RECORDS.md
- docs/runtime/JOB_WORKFLOW_PROMPT_RECORDS.md
- agent/runtime/execution_records.py
- tests/runtime/test_execution_records.py

Define record types:
- PromptRunRecord, PromptPackRunRecord, JobRunRecord, WorkflowRunRecord, CommandRunRecord, ApprovalGatedResumeRecord, QARunRecord, SelfHealRunRecord, MediaGenerationRunRecord future/stubbed, SecretScanRunRecord future/stubbed.

Record fields:
- record_id, record_type, status, created_at, updated_at, started_at, completed_at, branch, commit_hash
- prompt_id, prompt_pack_id, command, args_redacted, risk_level, approval_required, approval_id
- toolbroker_required, audit_ids, input_hash, output_hash, artifact_hashes, checkpoint_ids
- resume_command, rollback_plan, blocked_reason, evidence_paths, test_results, docs_updated, next_record_id

Statuses:
- queued, active, waiting_for_approval, running, completed, failed, blocked, cancelled, superseded, needs_review

Commands if practical:
- python smart_agent.py runtime records list
- python smart_agent.py runtime records show <record_id>
- python smart_agent.py runtime records latest
- python smart_agent.py runtime records validate

Requirements:
- Never store raw secrets or personal data by default.
- Link to prompt tracker rows and audit ids.
- Do not run queued prompts.
- Existing prompt tracker remains compatible.
Add tests, docs, and tracking updates.
