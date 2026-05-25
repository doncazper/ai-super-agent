# Lead Response Workflow

Status: specified

Date: 2026-05-23

## Goal

Define a safe, channel-agnostic lead response workflow that can later combine Gmail, Telegram, Apple Messages for Business, Mail, manual message handoff, contacts, tasks, calendar availability, and approved sends.

This is a workflow specification only. It does not implement lead-source adapters, read personal data, create tasks, schedule meetings, or send messages.

## Inputs

- Selected LeadInbox record.
- Optional selected contact reference.
- Optional selected calendar availability request.
- Optional selected workspace notes or captured context.
- Optional approved provider setup.

## Outputs

- Lead summary.
- Classification and priority.
- Relevant context.
- Draft response.
- Suggested follow-up task.
- Suggested meeting times.
- Pending Action Center items when writes/sends are requested.

## Rollout Levels

| Level | Name | Behavior | Gate |
|---:|---|---|---|
| 0 | Summarize only | Summarize selected lead metadata or selected content. | HIGH reads require approval for personal sources. |
| 1 | Draft response | Produce a draft response for manual review. | No send, no provider mutation. |
| 2 | Create pending action | Create Action Center items for tasks, calendar suggestions, or response drafts. | Actions remain pending until user review. |
| 3 | Send after explicit approval | Send only from an approved Action Center item. | CRITICAL per-action approval, no reuse. |
| 4 | Narrow template-based auto-send | Future-only constrained policy for low-risk templates. | Separate decision record, tests, live validation, and release gate required. |
| 5 | Autonomous lead handling | Agent handles leads without per-action review. | Deferred. |

## Workflow Steps

1. Load selected LeadInbox record after policy evaluation.
2. Label content by source trust level.
3. Summarize the lead without treating content as instructions.
4. Classify urgency and intent from metadata and selected content.
5. Optionally look up selected contact after approval.
6. Optionally check selected calendar availability after approval.
7. Draft response using only available source data and explicit user context.
8. Create follow-up task or meeting suggestion as pending Action Center items when requested.
9. For future send-capable paths, require exact preview and CRITICAL per-action approval.
10. Audit every read, draft, action creation, approval, denial, execution, and failure.

## Safety Rules

- No bulk inbox reads.
- No sends by default.
- No calendar/contact writes by default.
- No task creation without Action Center approval.
- No memory write unless explicitly approved by Memory policy.
- No source content can approve actions or change policy.
- No private Messages database scraping.
- No broad Full Disk Access.
- No hidden background polling.
- Personal data remains selected-scope.

## Failure Modes

- Provider unavailable: return setup instructions and do not fabricate lead data.
- Missing approval: skip that section and report the skipped reason.
- Untrusted content contains instructions: treat as data and filter instruction-like text.
- Send provider unavailable: keep draft and handoff only.
- Ambiguous recipient/channel: block send and require user clarification.

## Future Implementation Order

1. LeadInbox metadata models and tests.
2. Gmail lead-source adapter in metadata/read-selected mode.
3. Telegram lead-source adapter in selected-thread mode.
4. Apple Messages for Business provider strategy and mock adapter.
5. Lead response draft workflow.
6. Lead follow-up task workflow.
7. Lead scheduling workflow.
8. Approved lead response send with Action Center.
9. Auto-response policy design, future decision only.
