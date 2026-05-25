# Cross-Platform Core + Platform Bridge Architecture

Status: accepted for roadmap planning.

Date: 2026-05-25.

Scope: architecture decision and future implementation guide only. This decision does not implement macOS, iOS, Windows, Microsoft Graph, EventKit, Contacts, Mail, Messages, UI Automation, app frontend, personal-data access, or send/write actions.

## Decision

The Python agent core remains platform-neutral. Platform-specific behavior will be added only through optional, lazy platform bridges that advertise capability metadata and route any future side-effectful action through the existing safety control plane.

The portable core remains:

- Orchestrator
- Router
- LM Studio/Qwopus client
- ToolBroker
- PolicyEngine
- PermissionManager
- ApprovalManager
- AuditLogger
- Memory
- Web/search/research
- Weather
- Workspace files
- Native skills
- PromptOps
- Command registry
- Feature maturity
- Session logs
- Dogfood/evals
- Workflows

Future platform bridges are adapters, not replacements for the core:

- macOS bridge
- iOS companion bridge
- Windows bridge
- generic web/server bridge

## Required Principles

1. Python agent core remains platform-neutral.
2. Platform bridges are optional adapters.
3. CLI-only mode must remain fully functional.
4. Platform bridges must be disabled or lazy by default.
5. Platform-specific imports must never happen at core startup.
6. No platform bridge may bypass ToolBroker.
7. No platform bridge may bypass PolicyEngine.
8. No platform bridge may bypass ApprovalManager or AuditLogger.
9. Missing platform support must return structured `unsupported` or `requires_setup`, not crash.
10. Future platform capabilities must be declared in capability manifests before execution.
11. Future platform bridge actions must be mockable, testable, auditable, and approval-gated according to risk.
12. Platform status checks must not access personal data.

## Capability Boundary

A bridge may declare that a platform can eventually support a capability, but declaration is not execution permission. Execution requires all of the following:

- Capability manifest entry with risk, trust, default enabled state, approval requirement, audit fields, memory behavior, setup hint, and docs reference.
- ToolBroker route that owns validation and execution.
- PolicyEngine decision before execution.
- PermissionManager checks when platform or user permissions are required.
- ApprovalManager gate for HIGH and CRITICAL actions.
- AuditLogger evidence for requests, denials, approvals, executions, failures, and correlation IDs.
- Tests that prove unsupported platforms fail closed.

## Future Capability Examples

macOS examples:

- `macos.calendar.read`
- `macos.calendar.write`
- `macos.contacts.search`
- `macos.contacts.update`
- `macos.file_picker`
- `macos.security_scoped_bookmark`
- `macos.messages.probe`
- `macos.notifications`

iOS companion examples:

- `ios.message_compose_handoff`
- `ios.mobile_approval`
- `ios.notification`
- `ios.quick_action`
- `ios.pairing`

Windows examples:

- `windows.platform_doctor`
- `windows.file_picker`
- `windows.notifications`
- `windows.ui_automation`
- `microsoft_graph.mail`
- `microsoft_graph.calendar`
- `microsoft_graph.contacts`
- `windows.outlook_bridge`
- `windows.teams_bridge`

Generic app bridge examples:

- `app_bridge.status`
- `app_bridge.pending_actions`
- `app_bridge.submit_approval`
- `app_bridge.audit_summary`

## Consequences

Positive:

- The Python core can be reused by CLI, macOS, iOS companion, Windows, and local web/server frontends.
- Platform work can advance without importing native dependencies at startup.
- Future app frontends inherit the existing ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger rules.

Tradeoffs:

- Every bridge needs more upfront metadata and tests before it can do useful work.
- Platform behavior cannot be "quickly" added by calling native APIs directly.
- User-ready platform integrations require separate live validation and release gates.

## Explicit Non-Goals

- No real Windows functionality.
- No Microsoft Graph implementation.
- No Windows UI Automation implementation.
- No macOS EventKit, Contacts, Mail, or Messages implementation.
- No iOS companion behavior.
- No native app frontend code.
- No personal-data tool enablement.
- No send/write actions.
