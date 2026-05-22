# M1 Safety Control Plane

## Scope

Build policy, permission, approval, redaction, rate-limit, and audit infrastructure.

## Non-Goals

No personal-data tools, write/send actions, arbitrary shell, or self-improvement.

## Requirements

- `RiskLevel`, `TrustLevel`, `PolicyDecision`.
- Capability manifest.
- `PolicyEngine`, `PermissionManager`, `ApprovalManager`.
- Hash-chained `AuditLogger`.
- `SecretRedactor`.
- Rate limiter.
- Startup policy validator.

## Risks

- Misconfigured capabilities can overgrant access.
- Approval reuse can accidentally authorize critical actions.
- Audit redaction can miss secrets.

## Tests

- Unknown capability denied.
- SAFE allowed.
- HIGH asks approval.
- CRITICAL asks per-action approval.
- FORBIDDEN denied.
- Audit logs denials and approvals.
- Secrets redacted.
- Tools cannot bypass `ToolBroker`.

## Approval Gate

None.
