# App Bridge Security

The App Bridge must preserve the safety control plane. It is not an alternate execution path.

## Required Controls

1. Localhost/IPC only in v1.
2. `APP_BRIDGE_ENABLED=false` by default.
3. Remote access disabled and unsupported in v1.
4. Pairing required before sensitive surfaces.
5. Frontends cannot bypass `ApprovalManager`.
6. A frontend cannot approve its own generated action without explicit user interaction.
7. All future App Bridge requests must be audited.
8. Payloads are schema-validated before processing.
9. Sensitive fields are redacted in logs and reports.
10. CRITICAL actions require exact preview confirmation, per-action approval, and no approval reuse.
11. Results must correlate to action IDs and audit correlation IDs.
12. Status and capability surfaces must not return personal data.

## Forbidden In v1

- Remote access.
- Server startup by default.
- Native frontend implementation.
- Native platform imports in the Python core.
- Tool execution through the frontend.
- Policy, permission, approval, or audit changes through the frontend.
- Personal-data reads from status, capabilities, health, connector status, or audit summaries.
- Send/write actions.
- Background polling loops.

## Threat Notes

The primary threat is privilege confusion: a local app might appear trusted to users while bypassing the Python control plane. The mitigation is strict schema validation, pairing checks, audit correlation, and routing all executable behavior through existing ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger paths.

