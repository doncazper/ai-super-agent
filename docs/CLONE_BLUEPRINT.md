# Clone Blueprint

This blueprint describes how to rebuild the agent from scratch while preserving its DNA.

## Docs To Read First

1. `SPEC.md`
2. `docs/SDLC.md`
3. `AGENTS.md`
4. `docs/AGENT_DNA.md`
5. `docs/ARCHITECTURE_PRINCIPLES.md`
6. `docs/FEATURE_REGISTRY.md`
7. `docs/FEATURE_MATURITY.md`
8. `docs/COMMAND_REGISTRY.md`
9. `docs/PROMPT_LEDGER.md`
10. `docs/COMPLETION_REPORT.md`

## Minimum Architecture

- CLI entrypoint with Python 3.11+ guard.
- Orchestrator and router.
- Local model client or compatible model adapter.
- `ToolBroker`.
- `PolicyEngine`.
- `PermissionManager`.
- `ApprovalManager`.
- `AuditLogger`.
- `SecretRedactor`.
- Trust and risk models.
- Capability manifest validation.
- Workspace-bounded filesystem and safe test tools.
- Memory with default no personal-data storage.
- Prompt tracker and queue.
- Command registry and manual QA matrix.
- Feature maturity and release-gate docs.

## Required Modules

The clone must preserve these module families:

- Core runtime: orchestration, routing, messages, sessions, runtime status.
- Safety: policy, permission, approval, audit, redaction, validation, rate limits.
- Tools: registry, brokered low-risk tools, external providers, personal connectors disabled by default.
- Memory: safe storage and search with secret/personal-data guards.
- Workflows: dry-run-first, Action Center proposals, no direct sends/writes.
- Config: capabilities, provider policy, connector status, startup validation.
- Docs tracking: project state, registry, maturity, roadmap, changelog, completion report, prompt tracking, release checklist.

## Safety Systems

The clone is not equivalent unless it preserves:

- `ToolBroker` as the only execution path.
- `PolicyEngine` as the capability gate.
- `PermissionManager` for configured scopes.
- `ApprovalManager` for HIGH and CRITICAL approval behavior.
- `AuditLogger` for redacted append-only evidence.
- `SecretRedactor` for logs, reports, previews, and doctors.
- Trust labels for untrusted content.
- Risk labels for capability decisions.

## Tracking Systems

The clone must keep these source-of-truth files or compatible replacements:

- `docs/PROJECT_STATE.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/COMMAND_REGISTRY.md`
- `docs/PROMPT_LEDGER.md`
- `docs/PROMPT_QUEUE.md`
- `docs/PROMPT_AUDIT.md`
- `CHANGELOG.md`
- `docs/COMPLETION_REPORT.md`

## Minimum Tests

- Startup policy validation.
- Capability manifest validation.
- Unknown tool denial.
- Personal-data capabilities disabled by default.
- HIGH approval required.
- CRITICAL per-action approval with no reuse.
- Secret redaction.
- Untrusted content isolation.
- Prompt tracker validation.
- Command registry validation.
- Cloneability docs validation.

## Minimum Docs

The clone must include the specification, SDLC, working rules, Agent DNA, architecture principles, clone blueprint, migration guides, build history, provenance, decision index, registry, maturity tracker, roadmap, and completion report.

## Release Gate

Before claiming equivalence, run full tests, docs validation, startup policy validation, capability manifest validation, command registry validation, prompt audit, and a manual review of changed safety boundaries.

## Clone Equivalence

A clone is equivalent when it can explain its architecture, deny unsafe defaults, reproduce command/tracking docs, preserve prompt history or reconstruction caveats, and pass the cloneability release gate.
