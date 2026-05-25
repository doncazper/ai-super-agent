# Future macOS Bridge Guide

This guide defines the approved path for a future macOS bridge. It is not permission to implement EventKit, Contacts, Messages, Mail, private database access, notifications, file pickers, or send/write behavior in this milestone.

## Add A macOS Bridge

1. Keep the Python core platform-neutral and CLI-only mode functional.
2. Extend `agent.platforms.macos.bridge.MacOSPlatformBridge` only after the capability is declared in the static platform registry and disabled capability manifest.
3. Keep native imports out of module import, core startup, platform doctor/status, and health checks.
4. Return structured `requires_setup`, `unsupported`, or `blocked` for missing permissions or unsupported systems.
5. Route execution through a ToolBroker tool; workflows must not call bridge methods directly.

## Add A macOS Capability

Every new capability needs:

- Static platform registry entry.
- Disabled capability manifest entry with risk, trust, approval, default-enabled state, docs reference, and audit fields.
- ToolBroker mapping before execution.
- PolicyEngine and PermissionManager checks.
- ApprovalManager behavior for HIGH/CRITICAL actions.
- AuditLogger correlation in previews and results.
- Tests for denied, unsupported, missing setup, approval, audit, and no startup import behavior.

## Required Tests

- macOS bridge import does not import native frameworks.
- Platform doctor/status read no calendars, contacts, messages, mail, browser profiles, private app databases, or personal files.
- Missing setup returns a setup hint.
- Direct `execute_action()` is blocked.
- HIGH actions require approval.
- CRITICAL actions require exact per-action approval with no reuse.
- Action results include audit correlation.
- CLI-only Python mode still works on non-macOS systems.

## Command Registry And Maturity

Add or update `docs/COMMAND_REGISTRY.md` for any new command, including risk, approval behavior, ToolBroker path, audit behavior, docs, tests, manual QA, and known limitations. Update `docs/FEATURE_MATURITY.md` conservatively:

- Stub or metadata only: Scaffolded or Tested.
- Mocked behavior: Tested at most.
- Live local macOS validation: Live-Validated only after explicit non-sensitive QA.
- User-Ready requires docs, diagnostics, release-gate evidence, and known limitations.

## Startup Overhead Rules

- No `EventKit`, `Contacts`, `ScriptingBridge`, `AppKit`, `Foundation`, PyObjC, subprocess, network call, permission prompt, or app scan at import time.
- Health/status checks are metadata-only.
- Permission prompts must happen only in a future explicit user-approved flow.

## Unsupported Behavior

Unsupported or unconfigured macOS behavior must return structured status and setup hints. It must not crash, request permissions, scan personal data, or silently fall back to private app data access.

## Forbidden Without Explicit Future Approval

- Private macOS app database reads, including Messages `chat.db`.
- Silent send/write behavior.
- EventKit, Contacts, Mail, or Messages implementation.
- Full Disk Access assumptions.
- Browser profile, cookie, session, or Keychain scraping.
- Approval, policy, ToolBroker, PermissionManager, or audit bypass.
