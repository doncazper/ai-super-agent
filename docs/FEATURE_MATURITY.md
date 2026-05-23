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
| ToolBroker / PolicyEngine / AuditLogger | Safety control plane | 8 Mature Pattern | 95 | 10+ | Complete | Implemented | Broad policy, approval, audit, dry-run, preflight, and release-gate tests | Central enforcement path; unknown tools/capabilities denied | Hardened for denials, secrets, approvals, dry-run, preflight, and hash-chain audit | Validated through local test suite and CLI flows | Documented in SPEC, AGENTS, README, threat model, release checklist | Audit viewer verification could be richer | Keep as required pattern for every new tool |
| Unified Action Center | Safety and UX | 4 Tested | 73 | 1 | Complete for v1 review queue | Implemented as persisted action review records linked to approval requests; intentionally no direct execution path | Store, list/show, HIGH/CRITICAL approval requirements, one-time approval consumption, denial, edit invalidation, non-interactive blocking, audit lifecycle, redaction, and CLI tests | Integrates with ApprovalStore and AuditLogger; future execution still must go through ToolBroker and PolicyEngine | CRITICAL approvals are per-action only, previews require exact args, irreversible actions show rollback limits, edits invalidate approvals, secrets redacted | Local tests only; no live approved write/send flow yet | README command docs and project tracking updated | It is a review surface only; approved writes/sends are still not implemented | Use Action Center as the release gate before calendar writes, contact edits, email sends, or message sends |
| Connector framework | Connector foundation | 4 Tested | 72 | 1 | Basic framework requirements documented | Implemented as metadata/status/health registry; no action execution | Registry, unknown connector, redaction, personal-data-safe health, disabled/missing provider, and brokered existing connector tests | Status-only; does not bypass ToolBroker for actions | Secrets redacted and personal connector checks are configuration-only | Local tests only | README documents module roles and safety boundary | Does not yet unify provider construction or live health probes | Use for future connectors before adding new provider-specific dashboard logic |
| Weather connector | External connector | 7 User-Ready | 92 | 20+ | Complete | Implemented with Open-Meteo default provider, NWS U.S.-only provider, WeatherKit stub, explicit safe preferences, and weather-aware web research | Broad provider, cache, preferences, router, CLI, audit, error, NWS forecast/alerts, WeatherKit stub, weather+web impact tests, and city/state live-eval regression coverage | ToolBroker-only, LOW risk, audited, rate-limited | Hardened for no system location inference, opt-in default location, default-use audit source, structured errors, no precise-location cache, NWS U.S.-only guard, WeatherKit credential non-disclosure, web-only-when-needed impact routing, and Open-Meteo city/state abbreviation fallback | Open-Meteo safe eval passed on 2026-05-23; NWS/web impact live smoke remains optional | CLI doctor/smoke/current/forecast/alerts/config, WeatherKit decision record, readable formatter, setup docs | WeatherKit is intentionally stubbed; NWS current uses first hourly forecast period as best-effort observational summary | Review WeatherKit decision record before implementing JWT signing |
| Web search/fetch/research | External connector and workflow | 5 Hardened | 83 | 8 | Complete | Implemented with Brave provider option and disabled fallback | Broad mocked search/fetch/research tests, including provider missing, fetch failures, blocked domains, prompt injection, foreign-language content, no fabricated sources, no memory writes, and audit logs | ToolBroker-only, audited, rate-limited, `UNTRUSTED_WEB` | Prompt injection, fetch limits, blocked domains, first-class fetch failure reporting, and no fabricated sources covered | Live Brave smoke requires user API key | README and research commands documented | Live search validation depends on configured provider | Run live Brave smoke and document result |
| Browser selected URL and clipping | External/browser connector | 4 Tested | 73 | 1 | Complete for URL-workflow v1 | Implemented explicit URL read, summarize, and workspace clipping workflow plus selected-tab unavailable stub | URL summarize through brokered web fetch, blocked domain denial, prompt-injection filtering, workspace-only clipping, no history/cookie access, selected-tab stub, and audit tests | URL workflows use `web.fetch_url` and `filesystem.write` through ToolBroker/PolicyEngine/AuditLogger; selected-tab stub remains disabled and audited | No browser history, cookies, sessions, forms, passwords, profile database scraping, form submission, or browser automation; clips are workspace-only and labeled `UNTRUSTED_DOCUMENT` | Local mocked tests only; no live webpage smoke captured | README and decision record updated | Native selected-tab support is intentionally not implemented; explicit URL fetch depends on web access | Run live `browser summarize-url https://example.com` smoke when web access is available |
| Notes / Knowledge Capture v1 | Workspace workflow | 4 Tested | 74 | 1 | Complete for workspace inbox v1 | Implemented local workspace captures from explicit notes, workspace files, and URLs plus list, summarize, and memory promotion command | Capture note, from-URL brokered fetch, from-file workspace policy, unsafe path denial, secret rejection, memory promotion policy path, personal-data default block, prompt-injection filtering, audit, and CLI tests | Captures write through `filesystem.write`; files read through `filesystem.read`; URLs fetch through `web.fetch_url`; promotion calls `memory.store` through ToolBroker/PolicyEngine/AuditLogger | No Apple Notes integration, no private app database scraping, workspace-only storage, secrets rejected before writing, URL/file content treated as untrusted, and personal-looking content blocked from default memory promotion | Local mocked tests only | README and tracking docs updated | No Apple Notes provider; capture deletion/editing UI is not implemented yet; personal memory promotion requires future approved design | Add capture edit/delete/export if needed, then live smoke on real workspace notes |
| Workspace file assistant | Project tools | 5 Hardened | 82 | 5 | Complete | Implemented for bounded project filesystem/git/test actions plus `files` CLI workflow | Broad path, denial, write, backup, patch diff, untrusted-document, git, pytest, CLI, and audit tests | ToolBroker-only, audited, allowed-root enforcement; read content labeled `UNTRUSTED_DOCUMENT` | Path traversal, denied paths, `.env`, private app folders, large file limits, backups, and instruction-injection summaries covered | Local repo tests validate behavior | README command examples and milestone docs cover usage | No arbitrary shell, delete shortcut, or git push by design | Live user workflow smoke on real project files when desired |
| Memory | Memory | 5 Hardened | 83 | 5 | Complete | Implemented with SQLite persistent memory, category-aware search, export/delete/clear lifecycle, and bounded context injection | Preference, project fact, workflow lesson, secret refusal, personal approval, email body refusal, category search, context budget, no personal injection, export/clear, CLI, and audit tests | ToolBroker-only and audited; personal memory approval-gated; context injection audits injected IDs | Secret refusal, personal-data default denial, scoped/category search, non-personal context injection, deletion lifecycle covered | Local tests only | README documents commands, categories, context injection, and deletion limits | No advanced embeddings; deletion cannot rewrite audit logs or filesystem backups | Live UX smoke and optional richer memory viewer later |
| Personal connector readiness gate | Safety release gate | 5 Hardened | 84 | 1 | Complete | Checklist and evidence run completed; no connector implementation added | Full suite, startup policy, capability manifest validation, direct-access scans, and ToolBroker-bypass scans passed | Confirms ToolBroker, PolicyEngine, ApprovalManager, AuditLogger, connector registry, and personal defaults before personal connector work | Confirms selected-scope defaults, HIGH/CRITICAL approval rules, untrusted wrappers, non-interactive blocking, and no personal memory by default | Local validation only; no live personal-data reads by design | Checklist, release checklist, risk register, registry, roadmap, project state, and completion report updated | Does not replace connector-specific approval/live-smoke gates | Proceed to calendar read-only selected date range with explicit approval gate |
| Calendar read-only | Personal connector | 5 Hardened | 78 | 6 | Complete | Adapter and optional AppleScript path implemented, disabled by default | Disabled-module, approval, selected-range, selected-event, broad-range, notes/body omission, availability privacy, memory, audit, CLI, and event-text-as-data tests | HIGH risk, disabled by default, approval-gated, audited as `LOCAL_PRIVATE_DATA`; event title/id args redacted | Range limits, selected event token/date-title access, notes omission, location redaction, no memory storage, and event text labeled as data rather than instructions covered | Not live-validated against Calendar.app in this environment | README setup and limitations exist | Needs explicit live local smoke with user approval | Run dry-run then selected-range/selected-event live smoke only with approval |
| Calendar approved writes v1 | Personal write connector | 4 Tested | 72 | 1 | Complete for Action Center-gated stub execution | Draft commands create Action Center records; `--from-action` consumes approved records once and calls brokered write tools; live external write provider remains deferred | Draft pending action, create/update/delete approval-required, denial block, approved create one-shot, rollback token capture, notes omission, audit lifecycle, manifest disabled-by-default, and CLI smoke tests | Uses Action Center plus ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger; capabilities remain disabled by default and CRITICAL per-action | No direct chat writes, no automatic invites, no recurring events, no full calendar export, notes/body omitted unless explicitly allowed, and no memory writes by default | Local tests and draft CLI smoke only; no live Calendar.app writes | README, changelog, feature registry, project state, and completion report updated | Current connector is a no-external-change stub unless a future safe native write provider is approved | Design/review native Calendar.app/EventKit write provider separately before any live writes |
| Contacts read-only | Personal connector | 5 Hardened | 76 | 5 | Complete | Adapter and optional Contacts.app path implemented, disabled by default | Disabled-module, approval, no-bulk, compact search, requested-field, sensitive-redaction/config, memory, audit, CLI, and contact-text-as-data tests | HIGH risk, disabled by default, approval-gated, audited as `LOCAL_PRIVATE_DATA` | No bulk export, selected tokens, no notes, sensitive field redaction/config gates, no memory storage, and contact text labeled as data rather than instructions covered | Not live-validated against Contacts.app in this environment | README setup and limitations exist | Needs explicit live local smoke with user approval | Run selected-scope live smoke only with approval |
| Contacts approved edits v1 | Personal write connector | 4 Tested | 71 | 1 | Complete for Action Center-gated stub execution | Draft update/create commands create Action Center records with field-level previews; `--from-action` consumes approved records once and calls brokered write stubs; live external write provider remains deferred | Disabled-by-default manifest, pending update/create action, approval-required, denial block, approved one-shot update, exact field diff, phone/email/address redaction, bulk-edit denial, delete-deferred, no-memory, and audit lifecycle tests | Uses Action Center plus ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger; capabilities remain disabled by default and CRITICAL per-action | No direct chat edits, no bulk export/edit, no contact delete, sensitive field values redacted in stored previews/audits, and no memory writes by default | Local tests and draft CLI smoke only; no live Contacts.app writes | README, changelog, feature registry, project state, and completion report updated | Current connector is a no-external-change stub unless a future safe native write provider is approved; exact sensitive values are not persisted for live writes yet | Design/review native Contacts write provider separately before any live edits |
| Reminders / Tasks connector v1 | Personal connector | 4 Tested | 72 | 1 | Complete for adapter/mock v1 | Adapter interface, mock provider, brokered list/create/update/complete/delete tools, Action Center draft-create/create flow, and CLI commands implemented | Disabled module, list approval, draft-create, create approval, complete/delete approval, mock provider success paths, no-memory, audit, manifest, and CLI smoke tests | ToolBroker-only execution; list HIGH approval; writes CRITICAL per-action; create flows through Action Center | No full export, selected-scope list, no memory writes, task title/id/notes redaction, no native database scraping, no Full Disk Access dependency | Local tests and draft CLI smoke only; no live Reminders provider | README, decision notes, risk register, threat model, registry, roadmap, project state, and completion report updated | Native Reminders provider deferred; update/complete/delete direct CLI approval UX depends on interactive approval availability | Design native Reminders connector separately before live local writes |
| Email metadata + selected-thread + draft-only | Personal workflow | 5 Hardened | 80 | 6 | Complete | IMAP adapter option plus metadata, selected-thread read, summary, draft-only tools, and triage workflow, disabled by default | Disabled-module, metadata approval, thread approval, untrusted body, prompt-injection, draft-only, no-send, no-memory, audit, CLI, metadata-trust, and triage tests | HIGH risk, disabled by default, approval-gated, audited as `UNTRUSTED_EMAIL`, body args redacted | No send/delete/move/archive, no bulk read, metadata/body untrusted labels, untrusted body wrapper, prompt-injection filtering, triage body redaction, no body memory covered | Not live-validated with real account | README setup, triage commands, and limitations exist | Real provider setup and OAuth/keychain handling remain immature | Run with a deliberately configured non-production account only after explicit approval |
| Email approved send v1 | Personal send connector | 4 Tested | 72 | 1 | Complete for Action Center-gated mock/stub execution | Draft-new and reviewed draft-reply commands create Action Center records; `send --from-action` consumes approved records once and calls brokered send tool; real provider remains deferred | Disabled-by-default manifest, CRITICAL approval, no approval reuse, denial block, edit invalidation, full body preview, missing recipient block, attachment block, untrusted reply context, mock send, direct unreviewed send block, and audit lifecycle tests | Uses Action Center plus ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger; capability remains disabled by default and CRITICAL per-action | No direct unreviewed model-output sends, no background sends, no bulk sends, attachments blocked, email thread content labeled `UNTRUSTED_EMAIL`, and no memory writes by default | Local tests and mock provider only; no live email send provider | README, changelog, feature registry, risk register, threat model, project state, and completion report updated | Real provider/OAuth/keychain path not implemented; mock provider is test-only; body is intentionally visible in Action Center preview | Create provider decision record before any real email send integration |
| Messages/text draft-only | Personal workflow | 5 Hardened | 75 | 5 | Complete for safe fallback | Stubbed live connector plus explicit `messages.draft_from_text` workspace-file fallback, disabled by default | Disabled-module, no-send, bulk denial, unsafe-adapter, workspace-only fallback, untrusted content, prompt-injection, draft-only, no-memory, audit, CLI, and manifest tests | HIGH risk, disabled by default, approval-gated, audited as `UNTRUSTED_MESSAGE`; fallback file reads audited | No send/delete/move/archive/contact harvesting, no database scraping, no Full Disk Access, workspace-only fallback, untrusted wrapper, prompt-injection filtering, and no body memory covered | No live safe Messages connector by design | README setup and limitation docs exist | Live macOS Messages path intentionally absent | Keep live connector blocked until a safe permissioned integration exists |
| Messages safe handoff v1 | Personal handoff workflow | 4 Tested | 72 | 1 | Complete for save/copy handoff | Draft-from-text queues Action Center save/copy records; save writes inside workspace and copy uses clipboard/mock only; no automatic send path implemented | Workspace-only draft reads, unsafe path denial, untrusted labeling, prompt-injection filtering, no send tool, save/copy approval, workspace save, mock clipboard copy, no-memory, audit lifecycle, and CLI denial tests | Draft, save, and copy execute through ToolBroker/PolicyEngine; save/copy require Action Center approval; all actions audited | No Messages DB scraping, no Full Disk Access, no automatic send, no bulk read, no memory writes, clipboard risk documented, saved drafts constrained to workspace | Local tests only; no live clipboard smoke captured beyond mock | README and decision record updated | Clipboard can expose personal data to local apps; automatic send remains deferred | Create a separate provider decision and approval model before any automatic text sending |
| Daily briefing | Workflow | 5 Hardened | 82 | 5 | Complete for v2 | Implemented configurable opt-in sections for weather, calendar date range, tasks/reminders, email metadata, web topics, memory preferences, suggested actions, dry-run, and config show/set | Weather-only, calendar/tasks/email approval skip, denied approval, suggested Action Center action, no write/send, dry-run, audit, no-memory, and config tests | All selected sections execute or dry-run through ToolBroker; calendar/tasks/email are HIGH risk and approval-gated when enabled; suggested actions queue Action Center records only | No inferred location, no email bodies/messages/contacts/browser history, no writes/sends, no memory writes, unapproved personal sections skipped, and each section can fail independently | Local tests only; live personal sections require explicit user approval/config | README commands, config commands, and limitations documented | Personal sections are skipped by default because personal tools remain disabled; suggested action is a conservative review task only | Live-validate weather/web locally and run approved calendar/tasks/email dry-run before raising maturity |
| Meeting prep | Workflow | 5 Hardened | 76 | 1 | Complete for v1 | Implemented with brokered selected calendar event read, optional contact search, optional web topic search, dry-run, and deterministic prep output | Missing approval, approved event read, contact approval, optional web, no write/send, dry-run, no-memory, audit, and CLI tests | Calendar/contact steps execute through ToolBroker and approval gates; web remains brokered LOW risk | No emails/texts sent, no calendar/contact edits, no bulk export, no memory writes, calendar/contact data private, web untrusted | Local tests only; live personal sections require explicit user approval/config | README commands and limitations documented | Attendee names are not returned by default; event-id must be a selected event token | Live-validate with explicit dry-run and user-approved selected event |
| Meeting follow-up | Workflow | 4 Tested | 72 | 1 | Complete for v1 | Implemented brokered selected event read, workspace notes read, optional contact lookup, deterministic decisions/action-items extraction, and Action Center task/email/calendar suggestions | Event approval, workspace notes path enforcement, pending task actions, pending email action, no write/send, denied approval skip, prompt-injection filtering, no-memory, audit, and CLI dry-run tests | Calendar/contact/file reads execute or dry-run through ToolBroker; suggested tasks/email/calendar updates are Action Center records only and are not executed | Notes are `UNTRUSTED_DOCUMENT`, instruction-injection lines are filtered, no sends/writes/contact edits/task creates/calendar updates execute, and no memory writes occur | Local tests only; live personal sections require explicit user approval/config | README commands and limitations documented | Email draft uses `review-required@example.invalid` placeholder until edited; synthesis is deterministic and intentionally conservative | Live-validate notes-only dry-run and approved selected event read before raising maturity |
| Personal task extraction | Workflow | 4 Tested | 72 | 1 | Complete for v1 | Implemented brokered extraction from workspace notes/captures, selected email thread, selected calendar meeting, and selected URL into Action Center task drafts | Notes extraction, email approval, calendar approval, prompt-injection filtering, pending-only actions, denied source no-action, dry-run no-read, audit, and CLI JSON tests | Sources execute or dry-run through ToolBroker; personal sources are approval-gated; extracted tasks are Action Center `tasks.create` records only | Source instructions are ignored, no `tasks.create` execution occurs, denied personal reads create no actions, and no memory writes occur | Local tests only; live personal sources require explicit user approval/config | README commands and limitations documented | Extraction is deterministic and line-pattern based; task due dates/owners are not inferred yet | Live-validate notes-only dry-run and an approved selected email/calendar extraction before raising maturity |
| Email triage | Workflow | 5 Hardened | 76 | 1 | Complete for v1 | Implemented with brokered metadata-only priority classification, optional selected-thread read, summary, draft-only reply, dry-run, and deterministic report | Metadata-only, body approval, prompt-injection, draft-only, no-memory, audit, provider-unavailable, and CLI tests | All steps execute through ToolBroker and approval gates; body args are redacted | No sending, deleting, moving, archiving, bulk body reads, or memory writes; selected body omitted from triage report | Local tests only; live email provider requires explicit user approval/config | README commands and limitations documented | Priority classification is heuristic and metadata-only | Live-validate with a non-production account after explicit approval |
| Self-improvement backlog + implementation loop | Workflow | 5 Hardened | 84 | 5 | Complete for v1 | Implemented read-only backlog/propose plus approved proposal implementation on `codex/` branches, brokered writes/tests/diff, Action Center commit drafts, and approved commit execution path | Read-only propose, approved-file reads, policy-weakening blocked suggestions, ranked backlog, audit read, dry-run, approved proposal required, branch creation, policy/audit/package/persistence blocks, tests, diff, commit approval denial, and audit tests | Backlog/propose uses brokered `filesystem.read`; implementation writes through `filesystem.write`; tests/diff through ToolBroker; commits require Action Center and `git.commit` approval | Blocks policy weakening, audit disabling, protected safety file edits, personal-data grants, package installs without approval, persistence paths, send/write side effects, and unapproved commits | Local tests only | README command examples and limitations documented | Proposal approval store is JSON-file based in v1; no rich proposal review UI yet | Live-smoke an approved docs-only proposal on a throwaway branch before raising maturity |
| Prompt Ledger, Prompt Queue, and Prompt Pack tracking | SDLC tracking | 4 Tested | 76 | 2 | Complete for v1 | Implemented ledger, queue, audit docs, prompt record directories, templates, prompt CLI commands, best-effort prompt reconstruction, and strict prompt pack import/splitting | Docs existence, queue prompt IDs, list/next/audit, mark-complete evidence requirement, CLI dispatch, pack parsing, duplicate id/order rejection, missing metadata/end rejection, invalid risk/dependency/cycle rejection, validate-no-write, import writes, dependency-aware next, approval gate blocking, body preservation, and docs validation tests | Tracking commands are metadata-only and do not execute agent tools; prompt pack import is `import_only`; blocked approval-gated prompts remain explicit | Prevents missed/silent prompt drift, marks blocked/superseded prompts, requires evidence or `--unknown` for mark-complete, rejects execute-all packs, preserves prompt text as data, and updates AGENTS/PROJECT_STATE resume rules | Local tests only | Prompt docs, pack format docs, AGENTS rules, project state fields, changelog, registry, and roadmap updated | Reconstruction is best-effort and imported queue rows must be maintained after future batches | Use `prompts validate-pack` before importing mega prompts, then `prompts next` before running one prompt at a time |
| PromptOps Workbench v1 | SDLC tracking and orchestration | 4 Tested | 75 | 1 | Complete for v1 | Implemented one-command import from stdin/file/clipboard, raw single prompt import, next/copy/show/resume/status/review/audit, disabled-by-default runner, and safe-only autopilot guardrails | Import from stdin/file/clipboard, raw single prompt, invalid pack rejection, dependency-aware next, blocked approval gate stop, copy-next, disabled run-next, safe autopilot rejection of HIGH/approval-gated prompts, report redaction, mark-complete evidence requirement, and CLI tests | Workbench is metadata/orchestration only; prompt text is `UNTRUSTED_DOCUMENT`; runner is disabled by default; autopilot refuses HIGH/CRITICAL/FORBIDDEN and approval-gated prompts | Does not execute prompt packs automatically, does not grant approvals, does not weaken policy, does not add personal-data connectors, and reports redact secret-looking values | Local tests only; no live Codex runner execution by design | README, `docs/PROMPTOPS_WORKBENCH.md`, Prompt Pack format docs, AGENTS rules, project state, registry, changelog, and completion report updated | Runner integration is intentionally disabled unless configured; autopilot v1 stops conservatively and does not auto-mark completion | Use `work import` for pasted mega prompts and `work next` or `work copy-next` before running one prompt at a time |
| Command Registry and Manual QA System | SDLC tracking and QA | 4 Tested | 74 | 1 | Complete for v1 | Implemented static command catalog, generated registry/test matrix/legacy/runbook docs, validation helpers, and read-only `commands` CLI inspection commands | Command docs validation, required metadata validation, CLI list/show/search/legacy/validate/qa-plan/qa-run tests, and docs validation coverage | Metadata-only; no tool execution, connector access, personal-data read, approval consumption, or memory writes; `qa-run` prints safe command examples instead of executing them | Tracks command drift, status/maturity/risk/approval/test/manual-QA fields, legacy replacements, and safe manual QA plans; does not mark manual verification complete without evidence | Local tests only; manual QA runs are still pending for most commands | README command registry section, AGENTS rules, command docs/templates, feature registry, maturity tracker, roadmap, project state, changelog, and completion report updated | Registry is generated from curated metadata, so future command changes must update `agent/ui/command_registry.py` and regenerate docs; manual QA results remain mostly unverified | Run `python smart_agent.py commands qa-plan`, start with the Weather safe suite, and log manual QA findings in the matrix |
| Scheduler / Automation v1 | Automation | 4 Tested | 73 | 1 | Complete for manual-run v1 | Implemented local schedule store, explicit create/list/run/pause/delete commands, supported workflow allowlist, audited lifecycle events, and manual-run execution | Create/list, safe workflow run, personal approval-required section, CRITICAL non-execution, pause/delete, no hidden persistence, audit, and CLI tests | Scheduled tool workflows build a ToolBroker with PolicyEngine, ApprovalManager, and AuditLogger; connector/audit status workflows are metadata-only; personal sections keep existing approval gates | No LaunchAgent, cron, daemon, login item, or background runner; unsupported workflows are rejected; CRITICAL actions are not executed automatically; memory cleanup is no-op in v1 | Local tests only; no real background scheduling by design | README, `docs/SCHEDULER.md`, command registry, feature registry, roadmap, risk register, threat model, test plan, release checklist, project state, and completion report updated | V1 requires manual `schedule run`; recurrence parsing/background execution is deferred pending decision record and approval | Manually QA `connector_doctor` and weather-only `daily_briefing`; create a decision record before any system-level automation |
| Agent dashboard | UX | 5 Hardened | 78 | 5 | Complete for CLI v1 | Consolidated read-only `dashboard` and `status` commands for runtime, LM Studio, tools, connectors, permissions, approvals, audit metadata, memory counts, risk settings, last test run, and setup hints | Dashboard load, secret redaction, personal connector disabled status, pending approval display, audit tail, status metadata-only, doctor, connector dashboard, config/audit viewer tests | Dashboard executes no tools and grants/uses no approvals; underlying action commands retain ToolBroker/policy gates | Secrets redacted; personal connectors status-only; audit is metadata-only; memory summary returns counts only and no content | Local tests and CLI smoke only | README dashboard/status docs exist | No local web dashboard; live LM Studio status depends on local server/model config | Run release gate, then consider optional local web dashboard only if it stays inspect-only |
| Live validation and eval harness | Validation | 4 Tested | 72 | 1 | Complete for v1 scope | Implemented eval list/run/report, structured pass/fail/skipped results, docs report output, and safe default checks | Eval list/run/report, mocked safe evals, skipped personal evals, failure reporting, ToolBroker/audit evidence, no-personal-access, and CLI dispatch tests | Safe tool checks execute through ToolBroker; personal-data evals are skipped by default | No sends, no calendar/contact writes, no personal memory storage; workspace eval writes only under `./workspace/eval`; memory eval stores and deletes non-sensitive project fact | Local mocked tests only; live evals are user opt-in | README and `docs/EVAL_REPORT.md` template exist | Does not yet include opt-in approval-gated personal live evals or quantitative model scoring | Run `python smart_agent.py eval run --safe` locally with configured providers and record results |

## Summary

Most mature features:

- ToolBroker / PolicyEngine / AuditLogger: `8 Mature Pattern`
- Weather connector: `7 User-Ready`
- Personal connector readiness gate: `5 Hardened`
- Connector framework: `4 Tested`
- Unified Action Center: `4 Tested`
- Browser selected URL and clipping: `4 Tested`
- Notes / Knowledge Capture v1: `4 Tested`
- Calendar approved writes v1: `4 Tested`
- Reminders / Tasks connector v1: `4 Tested`
- Contacts approved edits v1: `4 Tested`
- Email approved send v1: `4 Tested`
- Messages safe handoff v1: `4 Tested`
- Prompt Ledger, Prompt Queue, and Prompt Pack tracking: `4 Tested`
- Command Registry and Manual QA System: `4 Tested`
- Scheduler / Automation v1: `4 Tested`
- LM Studio no-tool chat, web research, workspace tools, and memory: `5 Hardened`

Least mature features:

- Agent dashboard: `5 Hardened`
- Self-improvement backlog + implementation loop: `5 Hardened`
- Optional local web dashboard remains deferred; CLI dashboard is the current UX surface.

Features needing hardening:

- Calendar read-only
- Contacts read-only
- Email draft-only live provider path
- Messages draft-only
- Meeting prep live personal-data path
- Calendar approved writes native provider path
- Reminders / Tasks native provider path
- Contacts approved edits native provider path
- Email approved send real provider path
- Messages automatic send provider path
- Optional local web dashboard

Features needing live validation:

- LM Studio no-tool chat against the currently selected local model
- Web search/fetch/research with configured Brave Search
- Calendar read-only with explicit user-selected range and macOS approval
- Contacts read-only with explicit user-selected contact and macOS approval
- Meeting prep with explicit selected event and optional approved contacts
- Email draft-only with a deliberately configured non-production account

Features needing docs:

- Optional local web dashboard documentation if that path is selected later

Features needing tests:

- Optional local web dashboard workflow tests if that path is selected later

Current recommended work up next:

- Native Skills Program foundation, planning-first and without auto-installing or auto-enabling unvetted skills.

1. Run `python smart_agent.py work next` or `python smart_agent.py prompts next` and confirm `NATIVE-SKILLS-FOUNDATION`.
2. Keep Action Center as the review surface before any approved write/send implementation.
3. Run approved dry-runs before any live calendar/tasks/email metadata briefing or meeting prep personal sections.
4. Keep personal-data evals skipped until an explicit approval-gated opt-in design is added.

## Next Work-Up Candidates

Early or stubbed features:

- WeatherKit provider: decision record and configuration stub only; JWT signing and Apple API calls are intentionally deferred.
- Browser selected-tab native reader: explicit URL workflows are implemented, but native selected-tab access is a stub until a safe permissioned path is designed.
- Native Reminders/Tasks provider: v1 uses an adapter/mock pattern; real native integration needs a separate decision record and live approval model.
- Live calendar/contact write providers: Action Center-gated stubs exist, but real native writes are not enabled.
- Real email send provider: mock-only execution path exists; OAuth/keychain/provider strategy remains deferred.
- Automatic Messages send path: intentionally deferred; safe handoff is the current supported path.

Features lacking live validation:

- LM Studio no-tool chat against the currently selected local Qwopus model.
- Web search/fetch/research with the user's configured search provider.
- NWS alerts/forecast against live `api.weather.gov`.
- Calendar and contacts selected-scope reads with explicit user approval.
- Email metadata/draft-only with a deliberately configured non-production account.
- Tasks, calendar writes, contact writes, and email sends against real providers remain deferred until provider-specific decision records and approval gates are reviewed.

Features needing UX polish:

- Action Center editing for rich draft bodies and provider-specific previews.
- Approval queue/session persistence ergonomics.
- Memory viewer/search/export presentation.
- Command QA result logging and bug capture from manual QA.
- Scheduler recurrence display and human-readable next-run previews.
- Dashboard grouping for large command/connector inventories.

Features needing security hardening:

- Any future native write provider for calendar, contacts, tasks, email, or messages.
- Any future background scheduler/LaunchAgent/cron integration.
- Native skills loader, vetter, and marketplace flow.
- Provider credential storage and secret/config doctor improvements.
- Live personal-data eval path, which must remain opt-in and approval-gated.

Mature enough to reuse as patterns:

- ToolBroker / PolicyEngine / AuditLogger safety control plane.
- Capability manifest normalization and startup validation.
- Weather connector provider/status/cache/rate-limit pattern.
- Connector metadata/status framework.
- Action Center as the review surface for risky operations.
- PromptOps and command registry as SDLC tracking patterns.
- Workspace file assistant path policy and audit pattern.

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
