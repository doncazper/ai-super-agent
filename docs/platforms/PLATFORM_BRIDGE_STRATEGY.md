# Platform Bridge Strategy

This document defines how future macOS, iOS companion, Windows, and app/frontend integrations should connect to the existing Python agent without coupling the core to any one operating system.

## Scope

This is a planning and architecture document plus the current stub boundary. It defines adapter boundaries, capability metadata, safety gates, and future work order. Stub bridge modules are allowed to return structured `requires_setup`, `unsupported`, or `blocked` results only; they do not add real platform behavior.

## Strategy

The Python core stays portable and CLI-first. Platform bridges are optional adapters that can expose platform-specific capabilities through structured metadata and future ToolBroker-routed tools.

Bridge modules must be:

- Disabled or lazy by default.
- Safe to import on any supported OS.
- Mockable in tests.
- Capable of returning `unsupported`, `unavailable`, or `requires_setup` without crashing.
- Unable to bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

## Portable Core Components

The portable core includes:

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

## Bridge Families

| Bridge | Purpose | Initial posture |
|---|---|---|
| macOS bridge | Future macOS-native permissions, file pickers, notifications, and selected app integrations | Planned, disabled, lazy |
| iOS companion bridge | Future mobile approval, compose handoff, quick actions, pairing, notifications | Planned, disabled, lazy |
| Windows bridge | Future Windows status, file picker, notifications, UI Automation, Graph-facing integrations | Planned, disabled, lazy |
| Generic web/server bridge | Future localhost or IPC app frontend status, pending actions, approval submission, audit summaries | Planned, disabled, lazy |

## Execution Rule

Bridge existence is not execution permission. A bridge may advertise capabilities, but execution must flow:

`CLI/app request -> ToolBroker -> PolicyEngine -> PermissionManager -> ApprovalManager when required -> bridge adapter -> AuditLogger`

Any direct platform action outside this path is a release blocker.

## Status and Doctor Rule

Status, doctor, and capability inspection commands must not:

- Read calendars, contacts, messages, emails, tasks, browser profiles, or app databases.
- Request OS permissions.
- Start background services.
- Start app bridge servers.
- Import heavyweight native frameworks.
- Treat platform content as trusted instructions.

They may read safe config flags, static capability metadata, current Python platform identifiers, and explicit user-provided paths.

## Read-Only Platform Commands

The following commands are implemented as read-only, brokered metadata inspection commands:

- `python smart_agent.py platform doctor`
- `python smart_agent.py platform status`
- `python smart_agent.py platform capabilities`
- `python smart_agent.py platform matrix`
- `python smart_agent.py platform explain <capability_id>`

They execute through SAFE `platform.*` ToolBroker tools, PolicyEngine manifest entries, and AuditLogger events. They inspect static capability metadata, safe bridge config flags, lazy-load status, and `sys.platform` detection only. They do not execute bridge actions, import native frameworks, request permissions, access personal data, start app bridge servers, or enable planned/stubbed platform capabilities.

## Registry v1

The first implementation milestone for this track is `agent.platforms`, a portable data registry for planned/stubbed capabilities. It defines platform kinds, capability statuses, bridge metadata shapes, safe detection results, and static capability records without importing bridge implementations.

Registry v1 is intentionally not a bridge loader and not an execution path:

- It can list and explain known future capability records.
- It returns structured unsupported metadata for unknown platforms or capability IDs.
- It keeps every planned personal-data capability disabled by default.
- It records CRITICAL future capabilities as per-action approval-required.
- It uses lazy-load module names as strings only; it does not import those modules.
- It performs no network calls, subprocess calls, permission prompts, personal-data reads, or app bridge startup.

The next milestones must keep using this registry as descriptive metadata only until manifest placeholders, ToolBroker mappings, bridge interfaces, and startup/lazy-load guardrails are implemented and tested.

## Bridge Interfaces v1

The bridge interface milestone adds abstract contracts plus `NullPlatformBridge`. This is still not real platform behavior; it is the fail-closed seam that future macOS, iOS companion, Windows, and app/server bridge implementations must follow.

Required interface behavior:

- `health_check()` is metadata-only and must not access calendars, contacts, messages, mail, browser profiles, app databases, account data, or personal files.
- `list_capabilities()` and `get_capability_status()` read the static platform capability registry only.
- `prepare_action()` may create a preview or structured payload, but it must be side-effect-free.
- `execute_action()` is internal-only to future ToolBroker-approved tools and must fail closed when called directly.
- Action payloads and results include audit correlation fields so brokered tools can connect bridge outcomes to `AuditLogger` evidence.
- Bridges may declare capabilities, but they cannot enable or execute them without capability manifest entries, PolicyEngine checks, required approvals, and ToolBroker routing.

`NullPlatformBridge` is returned when a platform or bridge implementation is unavailable. It imports no native modules, performs no side effects, reads no personal data, and returns structured `blocked`, `unsupported`, or `requires_setup` results instead of crashing.

## Bridge Stubs v1

The bridge stub milestone adds lightweight, lazy-loadable packages:

- `agent.platforms.macos`
- `agent.platforms.ios_companion`
- `agent.platforms.windows`
- `agent.platforms.web_bridge`

Each stub subclasses `NullPlatformBridge`, uses a stable bridge ID, and lists static registry-backed capabilities for its platform family. The default `PlatformBridgeRegistry` registers loaders for these stubs without importing the modules at startup; a stub module is imported only when `get_bridge(platform)` asks for that bridge.

Stub behavior is intentionally fail-closed:

- `health_check()` returns `requires_setup`, `available=false`, and `personal_data_accessed=false`.
- `list_capabilities()` returns static metadata only.
- `prepare_action()` returns a side-effect-free preview payload.
- Direct `execute_action()` returns `blocked` with `direct_bridge_execution_forbidden`.
- Broker-context `execute_action()` returns `requires_setup` and performs no side effects.

These stubs do not import EventKit, Contacts, Messages, Mail, Microsoft Graph, Windows UI Automation, native app frameworks, or app frontend servers. They are implementation seams only; future executable platform actions still require manifest entries, ToolBroker mappings, PolicyEngine/PermissionManager/ApprovalManager gates, AuditLogger evidence, and a separate release gate.

## App Bridge API Contract v1

The App Bridge contract prepares a future local Mac app, iOS companion app, Windows app, or local web dashboard without starting a server or implementing a frontend. The current contract is schema/model validation only:

- `APP_BRIDGE_ENABLED=false` by default.
- `APP_BRIDGE_ALLOW_REMOTE=false` and remote access is unsupported in v1.
- Transport is localhost/IPC only: `stdio`, `unix_socket`, or `localhost_http`.
- Pairing is required before sensitive surfaces.
- Frontends cannot bypass `ApprovalManager` or approve their own generated actions without user interaction.
- CRITICAL actions require exact-preview confirmation, per-action approval, and no approval reuse metadata.
- Requests/results require audit correlation IDs.
- Status/capability surfaces must not return personal data.
- Importing the contract starts no server, polling loop, native app dependency, network call, or subprocess.

## Release Gate And Future Build Guides

The current cross-platform release gate is documented in `docs/platforms/CROSS_PLATFORM_RELEASE_GATE.md`. It validates the existing groundwork as metadata/interface/config/inspection/contract-only scaffolding and keeps release readiness conservative because manifest mapping, dedicated startup/lazy-load guardrails, live OS validation, and real bridge actions remain future work.

Future platform implementation must start from the shared guide plus the platform-specific guide:

- `docs/platforms/FUTURE_BRIDGE_IMPLEMENTATION_GUIDE.md`
- `docs/platforms/FUTURE_MACOS_BRIDGE_GUIDE.md`
- `docs/platforms/FUTURE_IOS_COMPANION_GUIDE.md`
- `docs/platforms/FUTURE_WINDOWS_BRIDGE_GUIDE.md`
- `docs/platforms/FUTURE_APP_FRONTEND_GUIDE.md`
