# Feature Maturity

This file tracks how developed, tested, safe, documented, and production-ready each feature is.

It is not enough to mark a feature as done. A feature can be implemented but still immature, under-tested, undocumented, unvalidated against live systems, or missing UX polish.

Codex and any coding agent must update this file whenever a feature, connector, workflow, command, policy, approval, audit, memory, or UI surface is added or changed.

This file complements:

- `docs/PROJECT_STATE.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_ROADMAP.md`
- `CHANGELOG.md`
- `docs/COMPLETION_REPORT.md`
- `docs/RELEASE_CHECKLIST.md`

## Maturity Levels

| Level | Name | Meaning |
|---:|---|---|
| 0 | Idea | Mentioned or proposed, but not specified. |
| 1 | Specified | Requirements, non-goals, risks, and acceptance criteria are written. |
| 2 | Scaffolded | Basic files/classes/commands exist, but behavior is incomplete or stubbed. |
| 3 | Implemented | Core behavior works in code, but tests/docs/hardening may be incomplete. |
| 4 | Tested | Unit/integration/security/denial tests exist and pass. |
| 5 | Hardened | Policy, approval, audit, failure modes, prompt injection, and edge cases are covered for the feature's risk. |
| 6 | Live-Validated | Tested against real LM Studio/provider/local runtime conditions. |
| 7 | User-Ready | Clear UX, setup docs, diagnostics, known limitations, and release gate are in place. |
| 8 | Mature Pattern | Reusable as a pattern for future modules/connectors/workflows. |

## Maturity Signals

Prompt count is useful context but is not proof of maturity.

| Signal | Description |
|---|---|
| Prompt / iteration count | Number of focused implementation, polish, or hardening passes spent on the feature. |
| Design completeness | Scope, non-goals, requirements, risks, and acceptance criteria are documented. |
| Implementation completeness | The feature works, is partial, or remains stubbed. |
| Test coverage | Success, error, denial, approval, security, and edge cases are tested. |
| Policy integration | ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger are enforced where applicable. |
| Approval integration | Approval behavior matches the feature risk level and non-interactive behavior is safe. |
| Audit coverage | Allows, denials, approvals, executions, failures, dry-runs, files, domains, and commands are logged where relevant. |
| Security hardening | Prompt injection, secrets, path traversal, personal data, unsafe writes, cache retention, and failure modes are considered. |
| Live validation | The feature has been smoke-tested against real LM Studio/provider/local runtime conditions. |
| UX/docs readiness | The user has clear commands, setup docs, diagnostics, limitations, and release gate notes. |
| Known limitations | Remaining risks or missing validation are named. |
| Next work needed | The next useful hardening, live validation, or feature pass is explicit. |

## Readiness Score

Use the maturity level as the main label. Use the readiness score as a secondary, approximate signal.

| Category | Max Points |
|---|---:|
| Spec and design | 10 |
| Implementation | 15 |
| Tests | 20 |
| Policy, approval, and audit integration | 20 |
| Security and threat hardening | 15 |
| Live validation | 10 |
| UX, docs, and diagnostics | 10 |
| Total | 100 |

| Score | Readiness |
|---:|---|
| 0-20 | Early idea or rough plan |
| 21-40 | Prototype |
| 41-60 | Implemented but needs hardening |
| 61-75 | Tested and usable with caution |
| 76-90 | Hardened or near user-ready |
| 91-100 | Mature reusable pattern |

## Current Assessment

| Feature | Category | Maturity Level | Readiness Score | Prompt / Iteration Count | Design Completeness | Implementation Completeness | Test Coverage | Policy/Audit Status | Security Hardening Status | Live Validation Status | UX/Docs Status | Known Limitations | Next Work Needed |
|---|---|---:|---:|---:|---|---|---|---|---|---|---|---|---|
| LM Studio no-tool chat | Core runtime | 5 Hardened | 82 | 4 | Complete | Implemented | Broad unit and mocked runtime tests | No tools attached in no-tool mode; audit not involved for pure chat | Debug redaction and no-tool regression covered | Needs repeat live local smoke with current model | README commands and doctor diagnostics exist | Depends on LM Studio server/model availability | Run live smoke with `LMSTUDIO_MODEL` before next release tag |
| ToolBroker / PolicyEngine / AuditLogger | Safety control plane | 8 Mature Pattern | 94 | 10+ | Complete | Implemented | Broad policy, approval, audit, release-gate tests | Central enforcement path; unknown tools/capabilities denied | Hardened for denials, secrets, approvals, dry-run, hash-chain audit | Validated through local test suite and CLI flows | Documented in SPEC, AGENTS, README, release checklist | Audit viewer verification could be richer | Keep as required pattern for every new tool |
| Weather connector | External connector | 7 User-Ready | 92 | 19+ | Complete | Implemented with Open-Meteo default provider, NWS U.S.-only provider, WeatherKit stub, explicit safe preferences, and weather-aware web research | Broad provider, cache, preferences, router, CLI, audit, error, NWS forecast/alerts, WeatherKit stub, weather+web impact tests | ToolBroker-only, LOW risk, audited, rate-limited | Hardened for no system location inference, opt-in default location, default-use audit source, structured errors, no precise-location cache, NWS U.S.-only guard, WeatherKit credential non-disclosure, and web-only-when-needed impact routing | Live provider smoke documented; repeat Open-Meteo/NWS/web impact smoke before release when network desired | CLI doctor/smoke/current/forecast/alerts/config, WeatherKit decision record, readable formatter, setup docs | WeatherKit is intentionally stubbed; NWS current uses first hourly forecast period as best-effort observational summary | Review WeatherKit decision record before implementing JWT signing |
| Web search/fetch/research | External connector and workflow | 5 Hardened | 80 | 7 | Complete | Implemented with Brave provider option and disabled fallback | Broad mocked search/fetch/research tests | ToolBroker-only, audited, rate-limited, `UNTRUSTED_WEB` | Prompt injection, fetch limits, blocked domains, and no fabricated sources covered | Live Brave smoke requires user API key | README and research commands documented | Live search validation depends on configured provider | Run live Brave smoke and document result |
| Workspace file assistant | Project tools | 5 Hardened | 78 | 4 | Complete | Implemented for bounded project filesystem/git/test actions | Broad path, denial, write, git, pytest tests | ToolBroker-only, audited, allowed-root enforcement | Path traversal, denied paths, `.env`, private app folders covered | Local repo tests validate behavior | README and milestone docs cover usage | No arbitrary shell and no git push by design | Add user-facing file command examples if needed |
| Memory | Memory | 5 Hardened | 76 | 4 | Complete | Implemented with SQLite persistent memory and lifecycle tools | Broad memory tests for secret/personal refusal and deletion | ToolBroker-only and audited; personal memory approval-gated | Secret refusal, personal-data default denial, scoped search, deletion lifecycle covered | Local tests only | README and test plan document limits | No advanced embedding/index compaction beyond current lifecycle | Improve memory viewer UX before broader use |
| Calendar read-only | Personal connector | 4 Tested | 68 | 4 | Complete | Adapter and optional AppleScript path implemented, disabled by default | Mocked selected-range and availability tests | HIGH risk, disabled by default, approval-gated, audited | Range limits, notes omission, location redaction covered | Not live-validated against Calendar.app in this environment | README setup and limitations exist | Needs explicit live local smoke with user approval | Run dry-run then selected-range live smoke only with approval |
| Contacts read-only | Personal connector | 4 Tested | 67 | 4 | Complete | Adapter and optional Contacts.app path implemented, disabled by default | Mocked search/read tests | HIGH risk, disabled by default, approval-gated, audited | No bulk export, selected tokens, sensitive field redaction covered | Not live-validated against Contacts.app in this environment | README setup and limitations exist | Needs explicit live local smoke with user approval | Run selected-scope live smoke only with approval |
| Email draft-only | Personal workflow | 4 Tested | 66 | 4 | Complete | IMAP adapter option plus selected-thread summary/draft tools, disabled by default | Mocked metadata/read/summary/draft tests | HIGH/MEDIUM risk, disabled by default, approval-gated where appropriate, audited | No send, no bulk read, untrusted email wrapper, no body memory covered | Not live-validated with real account | README setup and limitations exist | Real provider setup and OAuth/keychain handling remain immature | Create decision record before any real-account expansion |
| Messages draft-only | Personal workflow | 2 Scaffolded | 48 | 3 | Partial | Stubbed live connector plus manual workspace-file fallback | Mocked/stub and manual fallback tests | Disabled by default, approval-gated, audited | No send, no database scraping, no Full Disk Access, untrusted wrapper covered | No live safe Messages connector | README documents limitation | Live macOS Messages path intentionally absent | Keep as stub until safe permissioned integration exists |
| Daily briefing | Workflow | 4 Tested | 69 | 3 | Basic | Implemented as weather-only CLI workflow plus legacy brokered time workflow | Weather briefing success/error/alerts/audit/no-memory tests and workflow step tests | Executes weather tools through ToolBroker; no personal tools | Low risk; explicit/default weather location only, no calendar/email/messages/browser/history/memory | Local tests only | README commands and limitations documented | Weather-only; no calendar/email/web composition by design | Live-validate with Open-Meteo, then decide whether to add optional sources behind approvals |
| Meeting prep | Workflow | 0 Idea | 12 | 0 | Not written | Not implemented | None | Not applicable | Not reviewed | Not validated | Not documented beyond roadmap concept | Not defined as a concrete workflow | Write spec and non-goals before implementation |
| Email triage | Workflow | 1 Specified | 24 | 1 | Basic draft-only requirements exist | Not implemented as a distinct triage workflow | No dedicated triage tests | Would require email tools and approvals | Needs prompt-injection and personal-data review | Not validated | Not documented as a command | Current email summary/draft is not full triage | Create workflow spec and tests before code |
| Self-improvement backlog | Workflow | 4 Tested | 70 | 3 | Complete for controlled self-improvement baseline | Implemented manager and guarded operations | Policy-reduction, branch, proposal tests | Uses constrained project paths and approval-gated commit behavior | Blocks policy weakening and audit disabling | Local tests only | README/milestone docs exist | UX is developer-oriented; not live exercised end-to-end here | Add CLI polish and live dry-run before raising maturity |
| Agent dashboard | UX | 3 Implemented | 58 | 3 | Partial | CLI dashboards/viewers exist; no full local web dashboard | Connector/dashboard/config/audit viewer tests in parts | Read-only status paths avoid personal-data reads | Secrets redacted; personal connectors status-only | Local tests only | README connector dashboard docs exist | Dashboard is CLI-centered and fragmented | Consolidate status, permissions, audit, and maturity views |

## Summary

Most mature features:

- ToolBroker / PolicyEngine / AuditLogger: `8 Mature Pattern`
- Weather connector: `7 User-Ready`
- LM Studio no-tool chat, web research, workspace tools, and memory: `5 Hardened`

Least mature features:

- Meeting prep: `0 Idea`
- Email triage: `1 Specified`
- Messages draft-only: `2 Scaffolded`

Features needing hardening:

- Calendar read-only
- Contacts read-only
- Email draft-only
- Messages draft-only
- Agent dashboard

Features needing live validation:

- LM Studio no-tool chat against the currently selected local model
- Web search/fetch/research with configured Brave Search
- Calendar read-only with explicit user-selected range and macOS approval
- Contacts read-only with explicit user-selected contact and macOS approval
- Email draft-only with a deliberately configured non-production account

Features needing docs:

- Meeting prep
- Email triage
- Agent dashboard consolidation

Features needing tests:

- Meeting prep
- Email triage
- Full dashboard workflow tests

Current recommended work up next:

1. Add feature maturity validation and keep this file, `docs/FEATURE_REGISTRY.md`, and `docs/PROJECT_STATE.md` synchronized.
2. Run a live LM Studio no-tool smoke with the configured `LMSTUDIO_MODEL`.
3. Use Weather as the reference pattern for the next low-risk external connector only after a decision record.

## Maintenance Rules

Before starting a task, Codex must read this file to understand feature maturity.

Before finishing a task, Codex must update this file if the task changed any:

- feature
- command
- connector
- workflow
- policy behavior
- approval behavior
- audit behavior
- memory behavior
- user-facing documentation
- tests

A feature is not complete unless its maturity level, readiness score, tests, docs, policy/audit status, and next work needed are updated.

Do not mark a feature mature unless tests, docs, policy/audit behavior, and release gates justify it. Prompt count is useful context but not proof of maturity. A feature can be complete but still immature. A feature can be mature but still have known limitations.
