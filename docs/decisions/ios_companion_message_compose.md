# iOS Companion Message Compose Bridge

Status: accepted for mock/interface v1

Date: 2026-05-23

## Context

The project needs a safer path from reviewed message drafts to a user-visible send surface. iOS does not provide a safe general-purpose silent background personal-message send API for this project. The approved direction is a companion-app or deep-link handoff that opens Apple's compose UI, where the user reviews the recipient/body and taps Send or Cancel.

No iOS app project is present in this repository today. This v1 therefore adds only the local agent-side interface, payload schema, mock bridge behavior, result recording, tests, and documentation.

## Decision

The agent may create an iOS compose handoff payload from a local `MessageDraft` when either:

- the draft has a matching approved Action Center `messaging.send_approved` item, or
- the user explicitly invokes compose-only mode, where the iOS compose UI is the approval surface and the user must tap Send manually.

The payload is local workspace data. It includes `draft_id`, exact recipient, exact body, optional/deferred attachments, `expires_at`, `action_id`, nonce, integrity hash, risk level, and approval status. The future iOS companion app must present native compose UI and return `sent`, `queued`, `cancelled`, or `failed`.

## Safety Requirements

- No silent send.
- No background send.
- No message database read.
- No broad Full Disk Access.
- No bulk recipient list.
- Attachments are deferred in v1.
- Recipient and body must match the approved Action Center preview when `--from-action` is used.
- Payloads expire and expired payloads cannot record `sent` or `queued`.
- Results are recorded only after a returned iOS status.
- The agent never marks a send complete unless iOS reports `sent` or `queued`.
- All payload creation, status inspection, and result recording go through `ToolBroker` and `AuditLogger`.
- Message content is not written to memory by default.

## Commands

```bash
python smart_agent.py messaging ios-compose-payload <draft_id>
python smart_agent.py messaging ios-compose-payload <draft_id> --from-action <action_id>
python smart_agent.py messaging ios-compose-status <draft_id>
```

## Current Implementation

V1 writes local handoff payloads and returned-result records under:

```text
workspace/messaging/ios_compose/payloads/
workspace/messaging/ios_compose/results/
```

The local payload includes an integrity hash so a companion app or test harness can detect mutation. There is no iOS companion app in this repo yet and no send adapter is registered.

## Future iOS App Work

A future companion app should:

1. Receive a handoff payload through an approved mechanism such as a local file handoff, deep link, Shortcuts/App Intents bridge, or other reviewed path.
2. Verify payload integrity and expiration.
3. Present Apple's compose UI with exact recipient/body.
4. Let the user edit, send, or cancel.
5. Return only minimal result metadata to the agent.

Any future bridge that copies payloads across devices, uses deep links, or handles attachments needs its own threat-model and release-gate pass.

## Non-Goals

- No silent iOS message sending.
- No macOS Messages automation.
- No private Messages database access.
- No inbox read.
- No bulk messaging.
- No Apple Messages for Business provider.
- No delivery tracking beyond a returned compose result.
