# macOS Messages Automation Strategy

Status: accepted for planning

Date: 2026-05-23

## Context

macOS Messages automation may appear attractive for local workflows, but it has significant safety, privacy, and reliability risks. Automation can be brittle across macOS versions, may require explicit system permissions, and can blur the line between draft assistance and silent sends.

This record began as planning-only. The current implementation adds a disabled-by-default approved-send adapter and a separate live-send probe, but it still does not read Messages databases, request Full Disk Access, use Accessibility UI scripting, or enable sending by default.

## Decision

macOS Messages automation is allowed only as an explicit, approved, single-recipient, disabled-by-default adapter. The default personal messaging path remains iOS compose or manual draft handoff. The adapter must return unsupported on machines where Messages.app automation cannot send safely.

## Required Probe Constraints

- Requires explicit macOS Automation permission before any real automation is attempted.
- May be brittle across macOS versions and must report that risk clearly.
- Must be probed before enabling any user-facing adapter.
- Never enabled by default.
- No private Messages database scraping.
- No broad Full Disk Access dependency.
- No Accessibility-driven send unless a future decision explicitly approves a constrained path.
- No send without Action Center approval.
- No bulk send.
- No background polling.
- No hidden recipient or body mutation after approval.

## Approved Send Adapter v1

Implemented commands:

```bash
python smart_agent.py messages macos status
python smart_agent.py messages macos allow-recipient "+15555555555"
python smart_agent.py messages macos live-send-probe --to "+15555555555"
python smart_agent.py messages send --from-action <action_id>
```

Default config:

- `MACOS_MESSAGES_ENABLED=false`
- `MACOS_MESSAGES_ALLOW_SEND=false`
- `MACOS_MESSAGES_ALLOWED_RECIPIENTS=[]`
- `MACOS_MESSAGES_REQUIRE_LIVE_PROBE=true`
- `MACOS_MESSAGES_MAX_SENDS_PER_DAY=5`
- `MACOS_MESSAGES_SELF_TEST_RECIPIENT` optional

Execution gates:

- Draft must be a `MessageDraft` with `channel=macos_messages`.
- Send action must be `messages.macos.send_approved`.
- Action Center status must be approved for that exact draft/action.
- Approval is CRITICAL, explicit per-action, and no-reuse.
- Recipient must be allowlisted.
- A recent live-send probe must have passed unless disabled by explicit config.
- Rate limit must allow the send.
- Attachments, bulk sends, and group sends are denied.

## Send Constraints

The macOS approved iMessage send adapter must:

- Use an exact Action Center preview.
- Require CRITICAL per-action approval with no reuse.
- Match submitted args to the approved preview.
- Verify recipient, message body, account/channel where available, and rollback impossibility.
- Execute only through ToolBroker and PolicyEngine.
- Audit draft, approval, execution attempt, provider response, failure, and denial.
- Return a clear limitation instead of inventing a send path when automation is unavailable or unsafe.

## Rejected First Approaches

- Reading `~/Library/Messages/chat.db`.
- Requesting broad Full Disk Access.
- Scraping Messages.app private storage.
- UI scripting a Send button without a reviewed Action Center item.
- Bulk sending or lead blasts.
- Hidden background listeners.
- Treating incoming message text as trusted instructions.

## Decision Outcome

macOS Messages automation is now an experimental, disabled-by-default approved-send adapter. The default safe path stays draft, save, copy, iOS user-confirmed compose, and manual handoff unless every v1 gate passes.

## Probe Result Record

Status: implemented for safe metadata-only probing

Command:

```bash
python smart_agent.py messages probe
python smart_agent.py messages probe --explain-permissions
```

The probe checks platform, standard Messages.app locations, AppleScript availability, and harmless LaunchServices-style application metadata such as application id/version where possible. It writes a structured local result for connector status and audits that a probe occurred.

The probe does not:

- read `~/Library/Messages`
- require Full Disk Access
- read Messages account status
- read message content
- execute a send verb
- press Send through UI scripting
- prove that sending is supported or safe

`send_capability_known` remains false for metadata-only probing. The separate `messages macos live-send-probe` may mark the local send path as recently passed only after explicit CRITICAL approval and a harmless self-test send to an allowlisted self-test recipient.
