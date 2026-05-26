# Code Mode Truth Boundary

Code-mode and self-heal workflows must treat source code, tests, command metadata, capability manifests, generated reports, approval previews, and prompt tracker state as separate evidence streams. No single artifact can silently override the others.

## Source Boundaries

- `config/capabilities.yaml` remains the runtime capability, risk, approval, and default-enable truth.
- Actual code and tests remain implementation truth.
- `docs/COMMAND_REGISTRY.md` remains command metadata truth after validation.
- Prompt tracker files remain prompt-state evidence, not proof of feature maturity by themselves.
- Artifact hashes are tamper-evidence metadata, not approval or execution authority.
- Safety lints are conservative blockers for safe-only self-heal, not a replacement for full review.

## Forbidden Shortcuts

Code-mode and self-heal paths must not:

- Patch files without explicit scoped work.
- Commit or push automatically.
- Weaken ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.
- Reuse CRITICAL approvals.
- Enable personal-data tools by default.
- Store secrets or raw personal data.
- Install packages without approval.
- Start background services, servers, listeners, or live providers by default.
- Treat generated reports or model output as trusted instructions.

## CANON-05 Status

The current implementation is a read-only hardening layer: artifact hash reports and safety lint reports can inform review and block safe-only self-heal plans, but they do not execute recovery, apply patches, or update approval state.

