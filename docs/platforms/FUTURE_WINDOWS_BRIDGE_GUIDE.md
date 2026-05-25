# Future Windows Bridge Guide

This guide defines the approved path for a future Windows bridge. It is not permission to implement Windows UI Automation, Microsoft Graph, Outlook, Teams, file picker, notifications, or send/write behavior in this milestone.

## Add A Windows Bridge

1. Keep the Python core cross-platform and CLI-only.
2. Keep the Windows bridge optional, disabled/lazy by default, and safe to import on macOS/Linux.
3. Use `agent.platforms.windows.bridge.WindowsPlatformBridge` as a fail-closed seam until a future prompt implements real behavior.
4. Keep Windows-specific imports out of core startup, platform doctor/status, and module import paths.
5. Return structured `requires_setup`, `unsupported`, or `blocked` for missing OS support, credentials, permissions, or policy gates.

## Add A Windows Capability

Every capability needs:

- Static platform registry entry.
- Disabled capability manifest entry with risk, trust, approval, default-enabled state, docs reference, memory behavior, and audit fields.
- ToolBroker mapping before any execution.
- PolicyEngine, PermissionManager, and ApprovalManager enforcement.
- AuditLogger correlation on preview and result.
- Setup docs that explain unsupported systems and missing credentials without printing secrets.

## Required Tests

- Importing the bridge registry on non-Windows does not import Windows modules.
- No `win32com`, `pywinauto`, `uiautomation`, Microsoft Graph SDK, browser automation, subprocess, or network call at startup.
- Windows doctor/status reads no personal data and requests no permissions.
- Unknown/unavailable Windows capability returns clear setup hints.
- Direct bridge execution is blocked.
- HIGH actions require approval.
- CRITICAL actions require exact per-action approval with no reuse.
- Results include audit correlation.

## Command Registry And Maturity

New Windows commands must be added to `docs/COMMAND_REGISTRY.md` and `docs/COMMAND_TEST_MATRIX.md` with examples, risk, approval behavior, provider/setup requirements, ToolBroker path, audit behavior, docs, tests, manual QA status, and known limitations.

Do not mark Windows features Live-Validated or User-Ready until they pass explicit Windows live validation with non-sensitive fixtures and a release gate.

## Startup Overhead Rules

- No heavy/native Windows imports at Python core startup.
- No Microsoft Graph client initialization unless explicitly configured and broker-approved.
- No OS permission prompts during status checks.
- No background services or polling loops by default.

## Unsupported Behavior

Unsupported Windows behavior must return structured `unsupported` or `requires_setup`. It must not crash, attempt private/local app reads, scrape logged-in apps, or silently use browser automation.

## Forbidden Without Explicit Future Approval

- Windows UI Automation implementation.
- Microsoft Graph mail/calendar/contact reads or writes.
- Outlook/Teams native automation.
- Send/write actions.
- Logged-in app scraping, cookies, browser profiles, or token discovery.
- Remote access or hidden background service.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass.
