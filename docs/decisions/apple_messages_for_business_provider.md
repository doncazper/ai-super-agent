# Apple Messages For Business Provider Stub

Status: accepted for local stub

Date: 2026-05-23

## Scope

This decision adds a local Apple Messages for Business provider abstraction and mock provider. It prepares the business-grade lead-response path without relying on personal iMessage automation.

The v1 provider is a stub:

- It can report provider status.
- It can run a config-only doctor.
- It can create mock inbound lead records under `./workspace/leads/apple_business/`.
- It can create local `MessageDraft` response drafts for those mock leads.
- It cannot send messages.
- It does not require or load real provider credentials.

## Provider Model

Provider status records include:

- `provider_name`
- `configured`
- `account_id`
- `webhook_url`
- `send_endpoint`
- `inbound_events`
- `capabilities`
- `setup_hint`

The implementation redacts endpoint values that appear to contain secret query parameters and never prints API keys, client secrets, tokens, or private credentials.

## Capabilities

- `apple_business.inbound.receive`: local mock inbound only.
- `apple_business.message.draft_response`: create a local response draft only.
- `apple_business.message.send_approved`: future and disabled by default.
- `apple_business.conversation.status`: local mock conversation metadata only.

## Commands

```bash
python smart_agent.py apple-business doctor
python smart_agent.py apple-business status
python smart_agent.py apple-business mock-inbound
python smart_agent.py apple-business draft-response <lead_id>
```

The implementation also exposes `apple-business conversation-status <lead_id>` for local mock conversation metadata.

## Safety Rules

- Provider disabled by default.
- No hardcoded credentials.
- No real provider API call in v1.
- No send until a future provider is configured and a reviewed Action Center send item exists.
- Inbound webhook/mock event content is `UNTRUSTED_MESSAGE`.
- Customer leads map into Lead Inbox records.
- Send remains `CRITICAL`, disabled by default, exact-preview, per-action, and no-reuse.
- Provider errors are structured.
- Setup docs list provider options, not endorsements.
- No personal iMessage automation, private Messages database read, Full Disk Access, hidden polling, or bulk sending is introduced.

## Setup Options, Not Endorsements

Future live work may evaluate official Apple Messages for Business provider paths, business account setup, webhook intake, and provider API send endpoints. This project does not endorse a provider in v1. Any provider-specific adapter must get a separate decision record, credential doctor, mocked tests, live validation gate, and Action Center send approval gate.

## Rollout

1. Mock inbound local lead creation.
2. Local draft response creation.
3. Provider credential/config doctor.
4. Selected-scope live inbound adapter, if approved later.
5. Approved-send adapter after Action Center exact-preview tests and live provider validation.
6. Narrow template auto-response only after a separate future policy decision.

## Rejected Paths

- Consumer iMessage as the business lead-response path.
- Scraping `~/Library/Messages`.
- Broad Full Disk Access.
- Silent sends.
- Bulk/group sending.
- Sending just because provider credentials are present.
- Treating inbound customer text as trusted instructions.
