# Future iOS Companion Guide

This guide defines the approved path for a future iOS companion bridge. It is not permission to build an iOS app, implement pairing, mobile approvals, notifications, compose handoff, or send/write behavior in this milestone.

## Add An iOS Companion Bridge

1. Keep the Python core fully usable without an iOS device or app.
2. Treat the iOS companion as an optional frontend/approval adapter, not an authority that can bypass the core.
3. Use the App Bridge contract for status, capabilities, pending actions, approval decisions, and results.
4. Keep transport localhost/IPC-only for v1 unless a separate future approval changes the threat model.
5. Return `requires_setup` until pairing, trust, manifest mapping, ToolBroker routing, and audit correlation are implemented.

## Add An iOS Capability

Every new capability needs:

- Static platform registry entry and disabled capability manifest placeholder.
- App Bridge payload schema if the companion participates.
- ToolBroker mapping owned by Python core.
- PolicyEngine and PermissionManager checks before preview or execution.
- ApprovalManager enforcement for HIGH/CRITICAL actions.
- AuditLogger correlation for request, approval, handoff, and result payloads.
- Tests for unpaired denial, frontend self-approval denial, exact-preview CRITICAL approval, and no approval reuse.

## Required Tests

- Importing App Bridge/iOS scaffolding starts no server and imports no native app code.
- Status/capabilities payloads contain no personal data.
- Unpaired sensitive requests are denied.
- The frontend cannot approve its own generated action without user interaction.
- CRITICAL actions require exact preview and per-action approval.
- Results must carry audit/action correlation IDs.
- CLI-only mode works when no companion app exists.

## Command Registry And Maturity

Any iOS companion command must be recorded in `docs/COMMAND_REGISTRY.md` with risk, trust, approval behavior, ToolBroker path, audit behavior, docs, and tests. Do not mark iOS companion features User-Ready until pairing, setup docs, manual QA, and release-gate evidence exist.

## Startup Overhead Rules

- No mobile SDK, push-notification service, pairing daemon, polling loop, network listener, or subprocess at Python startup.
- Lazy initialize only after explicit configuration and user action.
- Status commands may inspect safe config metadata only.

## Unsupported Behavior

If the companion is absent, unpaired, disabled, or untrusted, return structured `requires_setup` or `unsupported` with next setup steps. Do not request permissions, start a server, or execute fallback send/write behavior.

## Forbidden Without Explicit Future Approval

- Silent or automatic message send.
- Bulk send.
- Remote access.
- Background persistence.
- Notification or pairing services started by default.
- ApprovalManager bypass or approval reuse.
- Personal-data reads or writes enabled by default.
