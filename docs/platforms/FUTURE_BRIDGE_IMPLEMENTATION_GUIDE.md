# Future Bridge Implementation Guide

Use this guide when adding a future macOS, iOS companion, Windows, or generic app bridge milestone.

For platform-specific implementation constraints, also read:

- `docs/platforms/FUTURE_MACOS_BRIDGE_GUIDE.md`
- `docs/platforms/FUTURE_IOS_COMPANION_GUIDE.md`
- `docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md`
- `docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md`
- `docs/platforms/CROSS_PLATFORM_RELEASE_GATE.md`

## Required Order

1. Write or update the decision record.
2. Add or update the capability matrix row.
3. Add disabled capability manifest entries.
4. Add bridge interfaces or stubs that return `unsupported`, `unavailable`, `blocked`, or `requires_setup`.
5. Add ToolBroker mapping for any executable action.
6. Add PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger behavior.
7. Add tests for unsupported platforms, missing setup, approval denial, audit correlation, and no startup imports.
8. Add command registry entries for commands.
9. Update feature registry, feature maturity, project state, changelog, risk register, threat model, release checklist, and completion report.
10. Run targeted tests, full tests if feasible, startup policy validation, capability manifest validation, docs validation, and command registry validation.

## How to Add a Capability

Every platform capability needs:

- Stable capability ID.
- Platform owner.
- Risk level.
- Trust level.
- `default_enabled=false` for personal-data, write, send, or native bridge actions.
- Approval requirement.
- Memory behavior.
- Audit fields.
- Setup hint.
- Docs reference.
- Test coverage.

Planned and stubbed capabilities are listable but not executable.

## How to Add a Bridge

A future bridge should expose:

- Bridge ID.
- Platform kind.
- Availability/status method.
- Health check that reads no personal data.
- Capability list.
- Capability status lookup.
- Prepare/preview method with no side effects.
- `execute_action()` method that is internal to brokered tools only.

The bridge must not import native frameworks at module import time. Use lazy imports inside platform-specific implementation paths only after ToolBroker and PolicyEngine have approved the action.

For the current v1 contracts, `NullPlatformBridge` is the reference implementation. Future bridges must preserve the same fail-closed behavior for unsupported platforms and setup failures: structured status, setup hints, audit correlation fields, no side effects in `prepare_action()`, and direct `execute_action()` denial outside ToolBroker-approved execution.

## Current Stub Packages

The current stub packages are:

- `agent.platforms.macos`
- `agent.platforms.ios_companion`
- `agent.platforms.windows`
- `agent.platforms.web_bridge`

These packages are lazy-loadable through `PlatformBridgeRegistry` and must remain safe on every OS. They declare capability metadata through the portable registry and inherit fail-closed behavior from `NullPlatformBridge`. They are not permission to add EventKit, Contacts, Messages, Mail, Microsoft Graph, Windows UI Automation, native app frontend code, network calls, subprocesses, personal-data reads, or send/write actions.

## App Bridge Contract Before Frontend Code

Future native or local web frontends must start from `docs/platforms/APP_BRIDGE_API.md`, `APP_BRIDGE_SECURITY.md`, `APP_BRIDGE_PAIRING.md`, and `APP_BRIDGE_PAYLOADS.md`. Do not implement a server, native UI, remote access, approval submission, or result handoff until the payload schema tests pass and a separate prompt adds ToolBroker mapping, manifest entries, audit handling, and release-gate coverage.

When replacing a stub with a real implementation, keep import-time behavior lightweight. Native or heavy imports belong inside broker-approved execution paths after policy and approval checks, never in core startup, doctor/status, or module import paths.

## ToolBroker Mapping

ToolBroker remains the only execution path. Workflows must not call bridge methods directly. The brokered tool owns:

- Argument validation.
- Capability lookup.
- Policy evaluation.
- Permission checks.
- Approval enforcement.
- Audit correlation.
- Result redaction.

## Tests to Add

At minimum:

- Registry loads on all OSes.
- Unsupported platform returns structured unsupported.
- Missing setup returns setup hints.
- Planned/stubbed capability cannot execute.
- HIGH requires approval.
- CRITICAL requires exact per-action approval with no reuse.
- Direct workflow-to-bridge execution is blocked or architecturally impossible.
- Health/status checks read no personal data.
- Core startup imports no native or heavy bridge modules.
- Audit correlation fields are present on future action results.

## Forbidden Without Explicit Future Approval

- Personal-data tools enabled by default.
- Send/write actions.
- Calendar, contact, email, message, or task writes.
- Private macOS app database access.
- Windows UI Automation.
- Microsoft Graph reads/writes.
- EventKit/Contacts/Mail/Messages native behavior.
- Browser profile/cookie/session scraping.
- Background persistence.
- Remote app bridge access.
- Policy, approval, or audit bypass.
