# Scheduled Action Gates

Status: HERMES-06 policy note.

## Allowed Shape

Scheduler v1 is manual-run only. Safe or low-risk workflow templates can be previewed, dry-run, created as local records, and manually run by explicit user action.

## Gate Matrix

| Workflow class | Default | Auto-run | Required gate |
|---|---|---:|---|
| SAFE diagnostics | Allowed for manual review | No | User command |
| LOW maintenance/evals | Allowed for manual review | No | User command |
| HIGH personal-data workflows | Disabled or approval-required | No | Explicit approval/config per run |
| CRITICAL send/write workflows | Blocked | No | Use an explicit one-off Action Center workflow instead |
| OS persistence | Blocked | No | Separate decision record and approval |

## Forbidden Without Future Approval

- cron, LaunchAgent, daemon, login item, or service installation
- hidden polling loops or background persistence
- unattended HIGH/CRITICAL workflows
- message/email sends
- calendar/contact writes
- personal-data tools enabled by default
- approval reuse for CRITICAL actions
- any ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger bypass

## Review Guidance

Use `schedule risks <workflow_id>` before creating or manually running a schedule. If a workflow is blocked or approval-required, do not convert it into a background task. Use an explicit reviewed Action Center flow instead.

