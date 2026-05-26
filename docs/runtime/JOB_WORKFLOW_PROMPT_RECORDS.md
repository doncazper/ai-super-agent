# Job, Workflow, Prompt, and Command Records

Status: CANON-02 implemented as schema scaffolding.

Execution records use the shared `DurableExecutionRecord` fields:

- `record_id`
- `record_type`
- `status`
- `created_at`
- `updated_at`
- `started_at`
- `completed_at`
- `branch`
- `commit_hash`
- `prompt_id`
- `prompt_pack_id`
- `command`
- `args_redacted`
- `risk_level`
- `approval_required`
- `approval_id`
- `toolbroker_required`
- `audit_ids`
- `input_hash`
- `output_hash`
- `artifact_hashes`
- `checkpoint_ids`
- `resume_command`
- `rollback_plan`
- `blocked_reason`
- `evidence_paths`
- `test_results`
- `docs_updated`
- `next_record_id`

## Compatibility

Prompt tracker files remain the human-readable prompt source of truth. Durable execution records link to prompt IDs, prompt pack IDs, evidence paths, audit IDs, and checkpoint IDs; they do not replace `PROMPT_LEDGER`, `PROMPT_QUEUE`, or `PROMPT_AUDIT`.

## Approval-Gated Resume

Records with `risk_level` `HIGH` or `CRITICAL` must set `approval_required=true`. `ApprovalGatedResumeRecord` also requires approval even if the current record metadata is otherwise safe.
