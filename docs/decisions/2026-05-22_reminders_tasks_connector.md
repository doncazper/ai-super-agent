# Reminders / Tasks Connector Decision Notes

Date: 2026-05-22

## Connector

Reminders / Tasks connector v1.

## User Value

Tasks are a practical next personal productivity surface after read-only personal connectors and Action Center. They let the agent turn daily briefing, meeting prep, email triage, and manual user requests into reviewable reminders without enabling email/text sending.

## Data Accessed

- Selected-scope task/reminder metadata.
- Task title.
- Optional due date/time.
- Optional list name.
- Optional notes only when explicitly allowed.
- Completion state.

No full task export is allowed by default.

## Actions Possible

Read:

- `tasks.list`

Write:

- `tasks.draft_create`
- `tasks.create`
- `tasks.update`
- `tasks.complete`
- `tasks.delete`

## Risk Level

- `tasks.list`: HIGH because task titles may contain private personal data.
- `tasks.draft_create`: MEDIUM because it stores a local pending Action Center record only and does not touch a task provider.
- `tasks.create`, `tasks.update`, `tasks.complete`, `tasks.delete`: CRITICAL because they modify personal task state.

## Trust Level

Returned task data is `LOCAL_PRIVATE_DATA`. Task text can contain user-supplied content and must be treated as data, not instructions.

## Permissions Required

V1 uses an adapter interface and mock provider only. A future native Reminders implementation must use permissioned macOS APIs or AppleScript automation prompts and must not scrape private databases or require broad Full Disk Access.

## Storage And Memory Behavior

- No long-term memory writes by default.
- Task contents are not stored in memory automatically.
- Audit logs redact task titles/ids/notes where possible.
- Action Center stores sanitized previews for pending writes.

## Approval Requirements

- Listing tasks requires approval.
- Drafting task creation routes through the brokered `tasks.draft_create` capability and creates an Action Center item only.
- Creating tasks requires Action Center review and per-action approval.
- Updating, completing, and deleting tasks require explicit approval.
- Denied or pending actions must not execute.

## Failure Modes

- Connector disabled by default.
- Provider not configured returns clear setup instructions.
- Unknown provider returns unsupported-provider guidance.
- Missing selected task id fails safely.
- Approval unavailable in non-interactive mode denies safely.

## Rollback Options

- Create can usually be rolled back by deleting the created task if a future native provider returns a task id.
- Update/complete rollback requires prior task state and is not guaranteed in v1.
- Delete rollback is not guaranteed and should be treated as irreversible unless a future provider stores explicit rollback data.

## Implementation Option Chosen

Build adapter interface plus mock provider first:

- No native Reminders write path.
- No private database scraping.
- No Full Disk Access.
- Action Center used for create drafts through brokered `tasks.draft_create`.
- All tool execution goes through ToolBroker.

## Alternatives Rejected

- Scraping Reminders private storage: rejected as unsafe and privacy-hostile.
- Broad Full Disk Access dependency: rejected.
- Direct CLI writes bypassing Action Center/ToolBroker: rejected.
- Background task creation from model output: rejected.

## Tests Required

- Disabled module denies access.
- List requires approval.
- Draft create creates pending Action Center action.
- Create requires approval.
- Complete/delete require approval.
- No memory writes by default.
- Audit logs reads/writes.
- Mock provider success paths pass.
