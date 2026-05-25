# Lead Response Drafting Workflow v1

Lead Response Drafting turns a selected local/mock lead or manually imported message into reviewable response artifacts without sending anything.

## Scope

- Summarize a selected lead.
- Classify lead intent and priority.
- Create a local `MessageDraft` response for user review.
- Suggest a follow-up task as a pending Action Center item.
- Suggest meeting reply text without reading calendars or creating events.
- Keep all source content as untrusted data.

## Non-Goals

- No auto-send.
- No approved-send execution.
- No provider webhook polling.
- No Gmail inbox, Telegram chat, personal iMessage, or CRM bulk ingestion.
- No private macOS Messages database access.
- No broad Full Disk Access.
- No memory storage of lead or message content by default.
- No calendar event creation.

## Commands

```bash
python smart_agent.py leads summarize <lead_id>
python smart_agent.py leads classify <lead_id>
python smart_agent.py leads draft-response <lead_id>
python smart_agent.py leads suggest-followup <lead_id>
python smart_agent.py leads suggest-meeting <lead_id>
python smart_agent.py leads create-send-action <lead_id> <draft_id>
```

`leads create-followup <lead_id>` remains as a legacy alias for `leads suggest-followup <lead_id>`.

## Workflow

1. Read a selected local/mock lead record.
2. Treat the lead body/preview as `UNTRUSTED_MESSAGE`.
3. Filter instruction-like source text before using it in summaries or drafts.
4. Classify intent, priority, and next step.
5. Summarize source, channel, assumptions, and safety limits.
6. Create a local editable `MessageDraft` under `./workspace/messaging/drafts`.
7. Optionally create a pending Action Center `tasks.create` item for follow-up.
8. Optionally suggest meeting reply text without reading calendar availability.
9. Stop before any send or calendar write.

## Safety Rules

- Lead content cannot request tools, change policy, approve actions, trigger sends, or write memory.
- Drafts identify source and assumptions so the user can review/edit them.
- Drafts may become Action Center send actions later through `leads create-send-action`; send execution remains a separate CRITICAL, exact-preview, per-action workflow.
- Follow-up suggestions create pending task actions only; task creation remains a separate approved execution.
- Meeting suggestions are guidance only; calendar availability and event creation remain future approval-gated workflows.
- All brokered steps are audited with redacted lead identifiers/content.

## Current Sources

- Mock Lead Inbox records.
- Manual message imports converted into Lead Inbox candidates.
- Apple Messages for Business mock/provider stub records.
- Future Gmail selected thread, Telegram selected message, personal iMessage manual handoff, and web-form adapters remain selected-scope and disabled until separate release gates.

## Release Status

Local v1 is tested for mock leads, selected-read approval denial, prompt-injection filtering, local draft creation, pending follow-up task actions, meeting suggestion no-event behavior, no direct send path, no memory write, and audit logging. See `docs/workflows/lead_response_send.md` for the approval-gated send/handoff workflow.
