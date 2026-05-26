# Canonical Runtime State Model

Status: CANON-01 implemented as metadata-only scaffolding.

The canonical runtime state model is a compact JSON-serializable view of the repo's current execution and tracker state. It is a reconciliation aid, not an executor. It must not call providers, execute tools, access personal data, request approvals, or mutate trackers.

## Fields

- `schema_version`
- `generated_at`
- `branch`
- `last_commit`
- `dirty_worktree_summary`
- `active_prompt_id`
- `active_prompt_pack`
- `active_job_id`
- `active_workflow_id`
- `active_session_id`
- `active_action_id`
- `current_phase`
- `current_status`
- `next_prompt_id`
- `last_completed_prompt_id`
- `blocked_reason`
- `resume_instruction`
- `last_test_result`
- `last_policy_check`
- `last_capability_check`
- `last_command_registry_check`
- `last_prompt_audit`
- `safety_summary`
- `tracker_summary`
- `evidence_links`
- `updated_by`

## Commands

- `python smart_agent.py runtime canonical-state`
- `python smart_agent.py runtime source-of-truth`
- `python smart_agent.py runtime reconcile-preview`

These commands are read-only and return metadata. They do not repair drift automatically.

## Safety

Secret-like keys and values are redacted before JSON output. Dirty worktree reporting is summary/count based. Validation and prompt fields are sourced from local repo metadata only.
