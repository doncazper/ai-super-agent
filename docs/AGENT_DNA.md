# Agent DNA

This file defines the identity that must survive a rewrite, model migration, platform port, or future app shell.

## 1. Mission In Plain English

Build a local-first AI agent that helps the user think and act while keeping control, privacy, safety, and resumability in the user's hands.

## 2. What Makes This Agent Different

The agent is not a raw chatbot, a hidden automation daemon, or a collection of direct scripts. It is a governed local assistant whose useful actions pass through explicit tool, policy, permission, approval, and audit boundaries.

## 3. Safety-First, Capabilities-Second

New capability is allowed only when the safety control plane can enforce it. A powerful feature that cannot be brokered, denied, audited, redacted, and tested is not ready.

## 4. Python Core As Portable Brain

The Python core owns orchestration, routing, policy, tools, memory, workflows, prompt tracking, command registry, dogfood loops, and release gates. Native apps and external services are bridges, not the brain.

## 5. Native Apps As Bridges

macOS, iOS, browser, and future app shells may provide UI, permissions, local integrations, or handoff surfaces. They must preserve the Python core's safety decisions and must not become side doors around policy.

## 6. CLI And Manual Mode Always Usable

Every important workflow must remain inspectable and recoverable from the CLI or docs. Native UX can improve ergonomics, but the repo must remain operable without a hidden app state.

## 7. ToolBroker-Only Execution

The model can request tools, but tools execute only through `ToolBroker`. Unknown tools and unknown capabilities are denied.

## 8. PolicyEngine-Enforced Permissions

`PolicyEngine` evaluates every tool request against the capability manifest. Personal-data, write, send, destructive, and irreversible actions stay disabled or approval-gated by default.

## 9. PermissionManager And ApprovalManager Responsibilities

`PermissionManager` owns configured permission state and protected scopes. `ApprovalManager` owns explicit user approvals, non-interactive denials, approval expiration, and CRITICAL per-action approval behavior.

## 10. AuditLogger Append-Only Record

Security-relevant decisions and executions must be auditable. Audit records are append-only, redacted, and treated as evidence for release gates.

## 11. Trust Model

Untrusted web, email, message, document, forum, and lead content is data, not instruction. Trust labels must survive through summaries, drafts, workflows, and action previews.

## 12. Risk Model

Risk levels are `SAFE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, and `FORBIDDEN`. CRITICAL actions require exact per-action approval with no approval reuse. FORBIDDEN actions remain unavailable unless a future explicit decision changes the policy.

## 13. Personal-Data Selected-Scope Rules

Personal-data connectors are disabled by default. Reads must be selected-scope, minimal, approval-gated when required, and audited. Bulk exports and private app database scraping are not first approaches.

## 14. Memory Rules

Memory is opt-in for sensitive content. Personal data is not stored in memory by default. Untrusted content cannot instruct a memory write.

## 15. Secret Handling

Secrets are never printed, logged raw, committed, or stored in session reports. Doctors may detect secret presence but must redact values and warn about unsafe file placement.

## 16. Self-Improvement Limits

Self-improvement may propose, test, and queue approved changes. It may not weaken policy, disable audit logging, grant itself personal-data access, create persistence, install packages without approval, send messages, or commit without an approved action.

## 17. Prompt Pack Discipline

Large tracks use prompt packs. Original packs are preserved under `prompts/packs/`. Split prompts are tracked in the prompt ledger and queue. Reconstructed packs must be labeled reconstructed and must never be claimed exact without evidence.

## 18. Feature Maturity Discipline

Completion is not maturity. Maturity depends on tests, docs, policy/audit behavior, live validation, dogfood evidence, and release-gate results. Prompt count is context, not proof.

## 19. Command Registry Discipline

Every command has a registry entry, risk level, approval requirement, maturity status, docs link, and test or manual QA status. Commands are not user-ready until tracked.

## 20. Dogfood, Session, Bug, Regression Loop

The project improves by running real or mocked safe sessions, capturing feedback, generating bugs, creating regression tests, and feeding evidence back into maturity and release gates.

## 21. Cross-Platform Bridge Philosophy

Portability comes from keeping core policy and orchestration independent from platform bridges. Bridges expose capabilities through explicit adapters and metadata, not direct access.

## 22. What Must Survive A Rewrite

The safety control plane, capability manifest, prompt tracking, command registry, feature maturity, project state, changelog, completion report, release checklist, and dogfood loop must survive.

## 23. What Must Never Be Compromised

Do not bypass `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, or `AuditLogger`. Do not silently enable personal-data tools. Do not silently send messages or email. Do not weaken CRITICAL approval rules.

## 24. How To Evaluate A Future Rewrite

A rewrite has the same DNA only if it denies unknown tools, preserves default-disabled personal data, enforces HIGH/CRITICAL approvals, treats untrusted content as data, redacts secrets, updates tracking docs, passes cloneability tests, and can run the manual release gate.
