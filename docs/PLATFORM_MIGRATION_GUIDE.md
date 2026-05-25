# Platform Migration Guide

This guide covers moving the agent across macOS, iOS, Windows, web dashboards, or other shells.

## Core Versus Bridge

The Python core owns safety and orchestration. Platform bridges provide local permissions, UI, OS-specific handoffs, or presentation. Bridges do not own final policy authority.

## Portable Core

Preserve:

- CLI entrypoint.
- Brokered tools.
- Capability manifest.
- Safety control plane.
- Audit logs.
- Prompt tracker.
- Command registry.
- Feature maturity.
- Release gates.

## Platform Capability Registry

Each bridge must declare:

- platform
- capability name
- risk level
- trust level
- default enabled state
- approval requirement
- audit behavior
- storage behavior
- setup requirements
- known limitations

## Lazy Loading

Platform-specific imports, SDKs, and permission probes must be lazy. Status commands must not trigger hidden personal-data reads, native app prompts, or network calls.

## Permissions

Bridge permissions must be selected-scope where possible. Broad filesystem, private database, browser cookie, Keychain, and background automation access require explicit decision records and approval.

## Adding A Bridge Safely

1. Write a decision record.
2. Add metadata and tests first.
3. Keep the bridge disabled by default.
4. Route execution through `ToolBroker`.
5. Add policy, approval, audit, redaction, and failure tests.
6. Add command registry and maturity entries.
7. Run release gates.

## Platform Examples

- macOS can provide local app handoff and permissioned automation probes.
- iOS can provide user-confirmed compose surfaces.
- Windows can provide filesystem and app bridges with explicit permissions.
- Web dashboards can provide review UI but must not approve or execute directly.
