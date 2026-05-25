# Lead Inbox Abstraction v1

Lead Inbox v1 creates a channel-neutral local schema for future lead response workflows. It is intentionally mock-only for runtime behavior in this pass.

## Scope

- Define local lead models and statuses.
- Provide a mock provider for tests and CLI smoke.
- Route lead listing, classification, drafting, and follow-up task proposals through `ToolBroker`.
- Create local `MessageDraft` records for reviewed response drafts.
- Create Action Center `tasks.create` records for follow-up tasks.

## Non-Goals

- No real Gmail, Telegram, iMessage, Apple Messages for Business, web-form, or CRM adapter.
- No provider sends.
- No message/database scraping.
- No broad Full Disk Access.
- No inbox bulk ingestion.
- No memory storage of lead content by default.
- No auto-response.
- No CRM sync.

## Commands

```bash
python smart_agent.py leads list
python smart_agent.py leads show <lead_id>
python smart_agent.py leads classify <lead_id>
python smart_agent.py leads summarize <lead_id>
python smart_agent.py leads draft-response <lead_id>
python smart_agent.py leads suggest-followup <lead_id>
python smart_agent.py leads suggest-meeting <lead_id>
python smart_agent.py leads create-send-action <lead_id> <draft_id>
python smart_agent.py leads send --from-action <action_id>
python smart_agent.py leads handoff <draft_id>
python smart_agent.py leads mark-responded <lead_id>
```

`leads list`, `classify`, `summarize`, `draft-response`, `suggest-followup`, and `suggest-meeting` operate on synthetic mock/local records in v1. `leads show` models selected full-message reads and remains disabled by default because real personal/customer lead reads are HIGH risk. `leads create-followup` remains available as a legacy alias for `leads suggest-followup`.

## Schema

Lead records include:

- `lead_id`
- `source`
- `channel`
- `sender_ref`
- `sender_display`
- `received_at`
- `subject_or_context`
- `message_preview`
- `full_message_ref`
- `trust_level`
- `risk_level`
- `status`
- `linked_contact_id`
- `linked_thread_id`
- `linked_actions`
- `tags`
- `priority`
- `consent_status`

Sources:

- `gmail`
- `telegram`
- `apple_messages_for_business`
- `personal_imessage_manual`
- `web_form`
- `manual`
- `mock`

Statuses:

- `new`
- `reviewed`
- `needs_info`
- `drafted`
- `pending_approval`
- `responded`
- `closed`
- `blocked`

## Safety Rules

- Lead content is `UNTRUSTED_MESSAGE` unless explicitly entered by the trusted user.
- Selected full-message reads are HIGH risk when personal/customer data is involved.
- Response sends are CRITICAL, exact-preview, per-action, and no-reuse. V1 supports approved orchestration and safe handoff; live provider sends still depend on disabled-by-default channel adapters passing their own gates.
- Classification does not create actions.
- Summarize and classify return review metadata only.
- Draft response creates an editable local `MessageDraft` with source and assumptions; `leads create-send-action` can later turn that reviewed draft into a CRITICAL Action Center item.
- Follow-up suggestion queues an Action Center `tasks.create` action and does not create a real task.
- Meeting suggestion returns reply guidance only; it does not read calendars or create events.
- Prompt-injection-like lead text is treated as data and filtered from drafts.
- Audit logs record list/classify/draft/follow-up activity with redacted lead arguments.
- Memory writes are disabled by default.

See `docs/workflows/lead_response_drafting.md` for the v1 drafting workflow and `docs/workflows/lead_response_send.md` for approval-gated send/handoff orchestration.

## Future Adapters

Future provider adapters must stay selected-scope, disabled by default, audited, and brokered:

- Gmail lead source: metadata/read-selected/draft-first only.
- Telegram lead source: selected lead/chat scope only; no token-presence reads.
- Apple Messages for Business: preferred long-term business path, now represented by a mock/local provider stub with no live provider calls and no sends.
- Personal iMessage: manual handoff first; no private Messages database scraping.
- Web forms: explicit inbound records only.

Approved lead response send orchestration is available for reviewed drafts, but live provider sends remain disabled unless the selected channel adapter is explicitly configured, approved, and validated. Unsupported channels return fallback handoff options instead of fake success.

## Apple Messages For Business Stub

```bash
python smart_agent.py apple-business doctor
python smart_agent.py apple-business status
python smart_agent.py apple-business mock-inbound
python smart_agent.py apple-business draft-response <lead_id>
```

The stub maps mock Apple Messages for Business inbound events into local Lead Inbox records under `./workspace/leads/apple_business/`. Inbound content is `UNTRUSTED_MESSAGE`; `draft-response` creates a local `MessageDraft` with `channel=apple_messages_for_business` and does not create a send action. Future `apple_business.message.send_approved` remains disabled by default and must be CRITICAL, exact-preview, per-action, and no-reuse before any live provider send is considered.
