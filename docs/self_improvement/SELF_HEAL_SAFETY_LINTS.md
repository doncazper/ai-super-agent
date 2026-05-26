# Self-Heal Safety Lints

CANON-05 adds static lint checks for code-mode and self-heal diffs. The lint layer is conservative and read-only. It reports metadata and hash-only evidence so reviewers can decide whether a safe-only self-heal plan should continue.

## Blocking Checks

The linter blocks safe-only self-heal plans when added diff lines appear to:

- Disable or bypass audit logging.
- Weaken or bypass PolicyEngine checks.
- Bypass ToolBroker or introduce direct tool execution.
- Reuse CRITICAL approvals or make CRITICAL approval non-explicit.
- Enable personal-data capabilities by default.
- Add background persistence, services, daemons, or unattended loops.
- Expand filesystem access outside approved workspace boundaries.
- Remove or bypass secret redaction.
- Install packages without approval.
- Enable live or paid providers by default.
- Start servers or listeners by default.
- Store raw secrets.
- Weaken backup restore verification.

## Commands

```bash
python smart_agent.py improve lint-diff --json
python smart_agent.py improve verify-artifacts --json
```

`lint-diff` returns non-zero when high-risk findings are present. `verify-artifacts` combines the lint report with the artifact hash report. Neither command applies patches, executes tests, creates commits, pushes, installs packages, downloads models, calls providers, starts services, or runs queued prompts.

## Evidence Policy

Findings include rule IDs, severity, descriptions, blocker status, and evidence hashes. Raw matching lines are intentionally omitted because diffs may contain secrets, personal data, untrusted content, or sensitive implementation details.

