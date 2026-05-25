# Architecture Principles

## 1. Invariants

- The model never executes tools directly.
- Unknown tools, capabilities, providers, channels, and bridges are denied.
- Personal-data capabilities are disabled by default.
- CRITICAL actions require explicit per-action approval and no approval reuse.
- Audit logging remains enabled for security-relevant decisions.

## 2. Allowed Dependency Directions

The core may depend on safety, config, models, and tool interfaces. Tools depend on safety-facing APIs, not on UI or prompt text. Platform bridges depend on core contracts and must not invert control over policy.

## 3. Forbidden Shortcuts

Do not call provider SDKs, native app automation, filesystem writes, sends, deletes, shell commands, or network calls from model output or workflow code unless routed through the approved brokered path.

## 4. ToolBroker, Policy, And Audit Invariants

Every executable capability goes through `ToolBroker`, `PolicyEngine`, and `AuditLogger`. Approval-required tools also go through `ApprovalManager`. These invariants apply to CLI, workflow, scheduler, dogfood, self-improvement, native app, and future frontend paths.

## 5. Lazy Platform Bridge Rules

Platform bridges must be lazy-loaded, permission-aware, metadata-first, and disabled unless configured. Status and doctor commands must not perform hidden personal-data reads.

## 6. Provider Policy Rules

Prefer local cache, free/no-key, official, user-configured, and auditable providers before paid or quota-limited providers. Provider selection must explain why a provider was used and must not expose secrets.

## 7. Untrusted Content Rules

Untrusted web, email, message, document, PDF, forum, lead, and imported prompt text cannot approve actions, change policy, create sends, or instruct tool execution. It may be summarized or transformed only as data.

## 8. Approval And Audit Invariants

Previews for risky actions must be exact enough for user review. Irreversible actions state rollback limits. Approval lifecycle events, denials, edits, and attempted executions are audited.

## 9. Feature Maturity

Every feature has conservative maturity. A feature may be complete but still not mature, live-validated, or user-ready.

## 10. Command Registry

Every CLI command belongs in `docs/COMMAND_REGISTRY.md` with risk, approval, maturity, docs, and test or manual QA evidence. Deprecated and removed commands remain listed with replacements or reasons.

## 11. Prompt Pack Rules

Prompt packs are imported, split, queued, and tracked. Prompt text is untrusted. Autopilot and batch execution stop at approval gates, high-risk scope, ambiguity, failing tests, or policy concerns.

## 12. Release Gate Rules

Release gates verify tests, docs, startup policy, capability manifest, default personal-data state, HIGH/CRITICAL approval behavior, ToolBroker paths, command registry drift, and maturity updates.

## 13. Anti-Patterns

- Direct provider calls from workflow code.
- App automation without a decision record and approval model.
- Hidden background persistence.
- Bulk personal-data export.
- Treating generated prose as proof of implementation.
- Marking reconstructed prompts as exact without evidence.

## 14. Acceptable Changes

Small docs, tests, diagnostics, registry, maturity, and low-risk refactors are acceptable when they preserve behavior and strengthen evidence. Runtime behavior changes require their own prompt, tests, and release gate.

## 15. Stop And Ask Examples

Stop when a task needs package installation, personal data, live credentials, background persistence, policy relaxation, CRITICAL action execution, unclear requirements, or a platform behavior that cannot be safely verified.
