# Resume, Recovery, and Checkpoint Model

Status: CANON-04 implemented as read-only checkpoint/recovery scaffolding.

The recovery model supports interrupted prompt packs, QA runs, workflows, self-improvement/code operations, and future frontend/channel actions. CANON-04 does not resume automatically, execute commands, bypass approvals, or mutate tracker state.

## Checkpoint Fields

- `checkpoint_id`
- `record_id`
- `created_at`
- `kind`
- `state_hash`
- `input_hash`
- `output_hash`
- `artifact_hashes`
- `current_step`
- `completed_steps`
- `remaining_steps`
- `approval_state`
- `audit_ids`
- `resume_command`
- `rollback_plan`
- `safe_to_resume`
- `human_review_required`
- `notes`

## Rules

- Recovery preview does not resume automatically.
- Active approval gates remain active.
- CRITICAL action resume requires fresh explicit approval.
- Prompt-pack resume uses prompt tracker evidence.
- Recovery output is redacted and must not contain secrets or personal data.

## Commands

- `python smart_agent.py runtime recovery-preview`
- `python smart_agent.py runtime checkpoints list`
- `python smart_agent.py runtime checkpoints show <checkpoint_id>`
