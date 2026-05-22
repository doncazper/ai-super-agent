# M8 Approved Write Actions

## Scope

Add high-risk write/send actions with explicit preflight and approval.

## Non-Goals

No bulk sending, background sending, hidden approvals, or approval reuse for critical actions.

## Requirements

- `calendar.create_event`
- `calendar.update_event`
- `calendar.delete_event`
- `contacts.update_selected`
- `email.send_approved`
- `messages.send_approved`
- Preflight summary for every critical action.

## Risks

- Sending wrong content or recipient.
- Irreversible modifications.
- Approval confusion.
- Abuse through prompt injection.

## Tests

- Email send requires approval.
- Text send requires approval.
- Calendar create requires approval.
- Contact edit requires approval.
- No approval reuse for critical actions.
- Denial prevents execution.
- Approval and execution audited.

## Approval Gate

Explicit user approval required before implementation. Every critical action requires per-action approval.
