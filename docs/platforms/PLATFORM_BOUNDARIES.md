# Platform Boundaries

Platform bridges must keep platform-specific code outside the core startup path and outside direct workflow execution. This protects CLI-only mode, release stability, and the safety control plane.

## Core Boundary

The portable Python core owns:

- Orchestration and routing.
- ToolBroker execution.
- Policy, permission, approval, and audit enforcement.
- Memory and retention policy.
- Command registry and maturity tracking.
- Dogfood/eval/release validation.

The core must not import native macOS, iOS, Windows, Microsoft Graph, or app frontend dependencies at startup.

## Bridge Boundary

Platform bridges may eventually own:

- Platform-specific setup checks.
- User-selected file or app handoff surfaces.
- Platform permission status adapters.
- Platform action adapters called only by brokered tools.
- Structured unsupported/requires-setup responses.

Platform bridges must not own:

- Policy decisions.
- Permission grants.
- Approval decisions.
- Audit redaction or storage policy.
- Memory writes.
- Direct execution from workflows.
- Startup registration that imports heavyweight native modules.

## Unsupported Behavior

Unsupported platforms must return structured output:

- `status=unsupported`
- `reason`
- `setup_hint`
- `capability_id`
- `platform`
- `audit_correlation_id` when a brokered tool was invoked

Unsupported platforms must not crash, fall back to scraping, call private databases, or silently skip safety checks.

## Detection And Path Boundary

Platform detection and path helpers are part of the portable core boundary, not real bridge behavior.

They may:

- Read `sys.platform`.
- Read explicit non-secret platform bridge environment flags.
- Return `macos`, `windows`, `linux`, or `unknown`.
- Return runtime mode metadata such as `cli`, `test`, `packaged_app`, or future bridge mode labels.
- Compute project-local paths for config, data, cache, logs, workspace, reports, and platform state.

They must not:

- Import native platform frameworks.
- Import bridge implementation modules.
- Scan personal directories or app data.
- Use cookies, sessions, browser profiles, or private OS stores.
- Create directories or write files during detection.
- Request OS permissions.
- Enable bridges or capabilities because a platform is detected.

Existing filesystem tools and their denied/sensitive path policies remain the source of truth for actual file reads and writes. Windows denied/sensitive paths can be documented as future metadata, but they must not be over-applied to unrelated core workflows until a reviewed platform policy exists.

Default bridge config remains disabled and lazy:

- `PLATFORM_BRIDGES_ENABLED=false`
- `PLATFORM_BRIDGE_MODE=auto`
- `PLATFORM_LAZY_LOAD_BRIDGES=true`
- `MACOS_BRIDGE_ENABLED=false`
- `IOS_COMPANION_BRIDGE_ENABLED=false`
- `WINDOWS_BRIDGE_ENABLED=false`
- `WEB_APP_BRIDGE_ENABLED=false`
- `APP_BRIDGE_ENABLED=false`
- `APP_BRIDGE_ALLOW_REMOTE=false`

## App Bridge Boundary

The App Bridge contract is for future local Mac app, iOS companion, Windows app, or local web dashboard frontends. In v1 it is a schema and documentation boundary only.

It may define:

- Local request/response envelopes.
- Pairing status metadata.
- Audit correlation requirements.
- Side-effect-free preview payloads.
- Redacted status, capability, connector, and audit-summary metadata.

It must not:

- Start a server by default.
- Allow remote access.
- Execute tools.
- Approve, deny, or reuse approvals outside `ApprovalManager`.
- Change policy or permissions.
- Return personal data from status/capability/health endpoints.
- Start polling loops.
- Import native app frameworks into the Python core.
- Add send/write actions.

## Command Boundary

`python smart_agent.py platform doctor`, `platform status`, `platform capabilities`, `platform matrix`, and `platform explain <capability_id>` are implemented as read-only metadata commands. They route through SAFE `platform.*` ToolBroker tools, PolicyEngine manifest entries, and AuditLogger events, but they do not execute platform bridge actions.

They may inspect:

- Static `agent.platforms` capability records.
- Safe platform bridge config booleans.
- `sys.platform` detection metadata.
- Lazy bridge registry loader/loaded counts.

They must not inspect:

- Calendar/contact/mail/message/task content.
- Browser profile/history/cookie/session data.
- Private macOS app databases.
- Windows app private stores.
- Microsoft Graph account data.
- Native framework status that would require importing platform-specific modules.

## Null Bridge Boundary

`NullPlatformBridge` is the default boundary object for unavailable platforms and bridge implementations. It may expose registry metadata and setup hints, but it must not:

- Import native platform modules.
- Read personal data during health, status, permission, or capability checks.
- Execute side effects from `prepare_action()`.
- Allow direct `execute_action()` calls from workflows.
- Self-enable capabilities because a bridge exists.

Direct `execute_action()` calls return a blocked result with `blocked_reason=direct_bridge_execution_forbidden`. Even broker-context calls through the null bridge return `requires_setup` because no real bridge implementation is present.

## Personal Data Boundary

Platform status checks must not access:

- Calendar event details.
- Contact records.
- Mail, Messages, chat, or notification contents.
- Browser history, cookies, passwords, sessions, or profile databases.
- Private macOS app databases.
- Windows app private stores.
- Microsoft Graph account data.

Future personal-data reads remain HIGH risk, disabled by default, selected-scope, approval-required, audited, retention-bounded, and source-labeled as data rather than instructions.

## Write and Send Boundary

Future writes and sends remain CRITICAL unless a later policy explicitly lowers risk with evidence. CRITICAL actions require exact preview, per-action approval, no approval reuse, ToolBroker execution, PolicyEngine evaluation, ApprovalManager enforcement, and AuditLogger evidence.

## App Frontend Boundary

Future app frontends may display status, pending actions, setup hints, and redacted audit summaries. They must not:

- Approve their own generated actions without user interaction.
- Execute tools directly.
- Change policy.
- Grant permissions.
- Start background services by default.
- Expose remote access in v1.
