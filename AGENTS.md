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
- Before starting feature work, read `docs/FEATURE_MATURITY.md`.
- Run tests after changes.
- Update `docs/COMPLETION_REPORT.md` after each milestone attempt.
- After changing any feature, command, connector, workflow, policy, approval, audit, or memory behavior, update `docs/FEATURE_MATURITY.md`.
- Do not mark a feature mature unless tests, docs, policy/audit behavior, and release gates justify it.
- Prompt count is useful context but not proof of maturity.
- A feature can be complete but still immature.
- A feature can be mature but still have known limitations.
- Be honest about failures.
- Stop at approval gates.
