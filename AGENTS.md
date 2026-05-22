# Codex Working Rules

These rules are permanent for this repository.

- Build milestone by milestone.
- Do not skip safety systems.
- Do not bypass `ToolBroker`.
- Do not bypass `PolicyEngine`.
- Do not bypass `ApprovalManager` for high or critical actions.
- Do not bypass `AuditLogger`.
- Do not implement personal-data tools before the safety control plane.
- Do not implement send/write actions before read-only and draft-only workflows.
- Do not weaken policy.
- Do not disable audit logging.
- Do not let self-improvement grant permissions, weaken safety, or create persistence.
- Run tests after changes.
- Update `docs/COMPLETION_REPORT.md` after each milestone attempt.
- Be honest about failures.
- Stop at approval gates.
