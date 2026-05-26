# Recovery Reports

Status: CANON-04 implemented as preview-only report schema.

Recovery reports summarize interrupted runtime work without resuming it.

## Fields

- `report_id`
- `generated_at`
- `interrupted_record`
- `last_checkpoint`
- `files_changed`
- `commands_run`
- `tests_run`
- `docs_updated`
- `blockers`
- `safe_next_action`
- `unsafe_actions_to_avoid`

## Safety

Recovery reports are redacted metadata. They must not include raw command output, raw prompt bodies, secrets, personal data, provider payloads, or hidden approval state. The report can recommend a safe next action, but it cannot execute that action.
