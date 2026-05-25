# Rewrite Checklist

Use this checklist before declaring a rewrite, port, or model migration compatible with this project.

- [ ] `ToolBroker` remains the only execution path.
- [ ] `PolicyEngine` denies unknown capabilities.
- [ ] `PermissionManager` preserves selected-scope rules.
- [ ] `ApprovalManager` enforces HIGH approval and CRITICAL per-action approval.
- [ ] CRITICAL approval reuse is blocked.
- [ ] `AuditLogger` remains enabled and redacted.
- [ ] Untrusted content is isolated as data.
- [ ] Personal-data tools remain disabled by default.
- [ ] Send/write/destructive tools remain approval-gated.
- [ ] Secrets are redacted in logs, reports, doctors, and tests.
- [ ] CLI/manual mode remains usable.
- [ ] Prompt packs and prompt ledger remain available.
- [ ] Reconstructed prompt packs are labeled reconstructed.
- [ ] Command registry and test matrix are current.
- [ ] Feature maturity is conservative.
- [ ] Project state and completion report are current.
- [ ] Dogfood, eval, bug, and regression loops remain available.
- [ ] Startup policy validation passes.
- [ ] Capability manifest validation passes.
- [ ] Docs validation passes.
- [ ] Full tests pass or failures are documented.
- [ ] Cloneability release gate passes.
