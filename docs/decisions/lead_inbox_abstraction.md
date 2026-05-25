# Lead Inbox Abstraction

Status: accepted for planning

Date: 2026-05-23

## Context

Future lead response may involve Gmail, Mail, Telegram, Apple Messages for Business, web forms, or manual message handoff. The agent needs a channel-agnostic model before adding provider-specific lead workflows.

This record is planning-only. It does not implement a runtime LeadInbox store or connector.

## Decision

Lead response workflows should use a LeadInbox abstraction. Provider adapters normalize selected lead metadata and selected message references into a shared schema. The abstraction must not imply permission to read full inboxes, store full messages, or send responses.

## LeadInbox Schema

| Field | Description |
|---|---|
| `lead_id` | Stable local lead identifier. |
| `source` | Provider or workflow source, such as gmail, telegram, apple_messages_for_business, manual_message, or web_form. |
| `channel` | Communication channel, such as email, chat, business_message, sms_handoff, or web. |
| `sender` | Redacted or minimal sender identity. |
| `received_at` | Received timestamp when available. |
| `subject_or_context` | Subject, thread title, or short context label. |
| `message_preview` | Minimal preview for triage; body content is not bulk-stored by default. |
| `full_message_ref` | Pointer to provider-selected content or workspace artifact, not a raw full-body dump by default. |
| `trust_level` | Trust label for returned data, such as `UNTRUSTED_EMAIL`, `UNTRUSTED_MESSAGE`, `UNTRUSTED_WEB`, or `LOCAL_PRIVATE_DATA`. |
| `risk_level` | Risk level for reading or acting on the lead. |
| `status` | Lead lifecycle status. |
| `linked_contact_id` | Optional selected contact reference. |
| `linked_thread_id` | Optional selected thread reference. |
| `linked_actions` | Pending or completed Action Center ids. |

## Initial Capabilities

- `lead.inbox.list`
- `lead.inbox.read_selected`
- `lead.classify`
- `lead.summarize`
- `lead.draft_response`
- `lead.create_follow_up_task`
- `lead.suggest_meeting_times`
- `lead.send_approved`, future only

## Status Lifecycle

- `new`
- `reviewed`
- `classified`
- `drafted`
- `action_pending`
- `responded`
- `closed`
- `blocked`

## Safety Rules

- No broad inbox ingestion by default.
- No full message body storage by default.
- Personal or business message content is untrusted data.
- Reads from personal sources are HIGH and approval-required.
- Sends are CRITICAL and per-action approved.
- Lead text cannot request tools, change policy, approve actions, reveal secrets, or write memory.
- Any memory write of lead content requires explicit Memory policy approval.
- Provider adapters must use ToolBroker and must be audited.

## Adapter Candidates

| Adapter | Initial posture |
|---|---|
| Gmail | Metadata/read-selected/draft-first. |
| Telegram | Config doctor first, selected lead adapter later. |
| Apple Messages for Business | Preferred long-term business lead path. |
| Personal Messages/iMessage | Manual selected text and handoff only. |
| Mail | Metadata/read-selected/draft-first if a safe provider path is approved. |
| Web form/capture | Workspace or provider-selected input, untrusted by default. |

## Non-Goals

- No runtime LeadInbox provider in this task.
- No email, Telegram, or Messages send.
- No private Apple database scraping.
- No background inbox polling.
- No lead auto-response policy.
