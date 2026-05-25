# iOS Message Compose Strategy

Status: accepted; agent-side mock/interface v1 implemented

Date: 2026-05-23

## Context

The safest near-term personal messaging path is user-confirmed compose. The agent may help prepare a draft, but the user must inspect the message in a native compose UI and tap Send themselves. This avoids silent background sending and keeps social context under user control.

This record began as planning-only. The current repo now includes an agent-side mock/interface bridge that creates local handoff payloads and records returned compose results, but it still does not add an iOS app, App Intent, Shortcuts bridge, deep link, clipboard bridge, send adapter, or message provider.

## Decision

Future personal iOS messaging support should start as a user-confirmed compose bridge:

1. The agent creates or receives a reviewed draft.
2. The user intentionally opens a compose surface.
3. The native iOS compose UI displays recipient and body.
4. The user taps Send, edits, or cancels.
5. The agent records only handoff metadata and audit status, not message delivery success unless a future explicit integration supports it safely.

## Requirements

- The user must tap Send.
- No silent background sending.
- No bulk sending.
- No send to a non-allowlisted recipient in tests.
- No message history read is implied by compose.
- Draft source content remains `UNTRUSTED_MESSAGE` or `MODEL_OUTPUT` until reviewed.
- Clipboard or deep-link handoff containing personal data is HIGH risk and approval-required.
- Exact preview must show recipient, channel, full body, source workflow, and rollback impossibility.
- The bridge must return a clear limitation if native user-confirmed compose cannot be supported safely.

## Suitable Use Cases

- Personal/manual assistant handoff.
- Drafting a reply from user-provided text.
- Moving a reviewed draft into a user-visible compose surface.
- Small selected-recipient workflows where the user remains the sender.

## Non-Goals

- No automatic send.
- No Messages database access.
- No inbox polling.
- No background delivery tracking.
- No mass outreach.
- No contact harvesting.
- No bypass of iOS compose confirmation.

## Future Implementation Notes

Possible future implementation paths must be evaluated separately, such as a small local companion app, Shortcuts/App Intents, or a documented manual handoff. Any implementation must preserve selected scope, exact preview, approval gates, redaction, and auditability.

The current local interface is documented in `docs/decisions/ios_companion_message_compose.md`.

## Decision Outcome

iOS user-confirmed compose is the preferred personal-send exploration path because it keeps final send authority with the user. It is not a silent send path and must not be marketed or implemented as one.
