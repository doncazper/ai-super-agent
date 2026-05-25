# Future App Frontend Guide

This guide defines the approved path for a future Mac app, iOS companion app, Windows app, or local web dashboard. It is not permission to implement a frontend, start a server, enable remote access, or execute platform actions in this milestone.

## Add An App Frontend

1. Start from the App Bridge contract docs: `APP_BRIDGE_API.md`, `APP_BRIDGE_SECURITY.md`, `APP_BRIDGE_PAIRING.md`, and `APP_BRIDGE_PAYLOADS.md`.
2. Keep `APP_BRIDGE_ENABLED=false` by default.
3. Keep remote access disabled and unsupported in v1.
4. Use localhost/IPC-only transport unless a separate threat-model approval changes the boundary.
5. Treat the frontend as a display/approval surface, not an execution authority.
6. Keep all execution owned by Python core ToolBroker paths.

## Add A Frontend Capability

Every new surface needs:

- App Bridge payload schema.
- Capability registry and disabled manifest entry when it can lead to an action.
- ToolBroker-owned request handling.
- PolicyEngine/PermissionManager/ApprovalManager enforcement in the Python core.
- Audit correlation across frontend request, preview, approval, execution result, and displayed status.
- Redaction for sensitive fields in logs and payload summaries.

## Required Tests

- Importing the contract starts no server, polling loop, network listener, or subprocess.
- Status/capabilities payloads contain no personal data.
- Remote host config is forced back to localhost/IPC.
- Pairing required before sensitive actions.
- Frontend cannot approve its own generated action without user interaction.
- CRITICAL actions require exact preview and per-action approval with no reuse.
- Result payloads require audit/action correlation IDs.
- Secrets are redacted.

## Command Registry And Maturity

Any frontend command must be recorded in `docs/COMMAND_REGISTRY.md` with risk, approval behavior, provider/setup requirements, side effects, ToolBroker path, audit behavior, memory behavior, docs link, test coverage, manual QA status, and known limitations.

Do not mark frontend features User-Ready until setup docs, pairing docs, manual QA, and release-gate evidence exist.

## Startup Overhead Rules

- No server starts at import or CLI startup.
- No polling loop by default.
- No native app dependencies in the Python core.
- No network listener unless explicitly configured and approved in a future milestone.
- Status endpoint must remain lightweight and personal-data-free.

## Unsupported Behavior

If the frontend is disabled, unpaired, unsupported, or missing, return structured `requires_setup` or `unsupported`. Do not start a server, request permissions, open network ports, or execute fallback actions.

## Forbidden Without Explicit Future Approval

- Remote access.
- Native frontend implementation.
- Frontend-owned approvals that bypass ApprovalManager.
- Frontend self-approval without user interaction.
- App bridge server startup by default.
- Personal-data payloads in status/capabilities.
- Send/write actions.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass.
