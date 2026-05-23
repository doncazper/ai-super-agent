# Feature Roadmap

This roadmap is the execution queue for post-baseline work. It prioritizes safety, documentation, tests, and release gates before capability breadth.

Every roadmap status change must update:

- `docs/PROJECT_STATE.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/COMPLETION_REPORT.md`
- `CHANGELOG.md` when user-visible behavior changes

## Current Batch

Durable project tracking and connector-foundation cleanup.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | SDLC release gate + roadmap reset | complete | M0-M11 complete | Release gate passed locally |
| 2 | Changelog, feature registry, roadmap, and `PROJECT_STATE.md` | complete | Release gate complete | Tracking docs and validation passed |
| 3 | Connector framework generalization | complete | Tracking docs existed; weather pattern available | No action execution; metadata/status only |
| 4 | Capability manifest + policy normalization | complete | Connector framework and tracking docs complete | Normalized manifest validation passed |
| 5 | Runtime doctor + connector dashboard | complete | Connector framework complete | Diagnostics passed without personal-data reads |
| 6 | Approval UI + universal dry-run/preflight | complete | Policy normalization complete | HIGH/CRITICAL rules remain strict; preflight tests pass |
| 7 | Prompt Ledger and Prompt Queue tracking | complete | Project tracking docs and completion report evidence | Ledger/queue/audit docs and prompt CLI validation passed |
| 8 | Prompt Pack import and splitting | complete | Prompt ledger/queue tracking | Import-only pack validation, splitting, ledger/queue/audit integration, and prompt pack tests pass |
| 9 | PromptOps Workbench v1 | complete | Prompt pack import and splitting | One-command import/next/copy/status workflow complete; runner disabled by default; autopilot stops at safety gates |
| 10 | Command Registry + Manual QA System | complete | PromptOps and tracking docs complete | Command catalog/test matrix/legacy/runbook generated; registry validation and CLI tests pass |

## Next Batch

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 7 | Source-grounded web research | complete | Web provider docs and prompt-injection tests | Web content remains `UNTRUSTED_WEB`; tests pass |
| 8 | Workspace file assistant | complete | File policy review | Approved roots, denylist, backups, audit, and tests pass |
| 9 | Memory v2 + safe context injection | complete | Memory policy and deletion lifecycle | Personal memory requires approval; context injection audited |
| 10 | Personal connector readiness gate | complete | Approval UI, dry-run, audit verification | Gate passed locally; stopped before personal-data reads |
| 11 | Calendar read-only connector | complete | Readiness gate passed | HIGH, selected range, approval required; live Calendar.app smoke still requires explicit approval |
| 12 | Contacts read-only connector | complete | Readiness gate passed | HIGH, selected scope, approval required; live Contacts.app smoke still requires explicit approval |
| 13 | Email draft-only assistant | complete | Email decision record and readiness gate | No sending, no delete/move/archive, no bulk ingestion |
| 14 | Messages/text draft-only assistant | complete | Safe path review | No Messages DB scraping, no sending; manual workspace fallback only |
| 15 | Daily briefing workflow v1 | complete | Weather and optional approved sources | No hidden personal access; calendar/email metadata skipped without approval |

## Later Batch

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 16 | Meeting prep workflow | complete | Calendar/contact/email draft-only foundations | Personal reads require approval |
| 17 | Email triage workflow, draft-only | complete | Email draft-only assistant hardened | No send/move/archive/delete |
| 18 | Self-improvement backlog generator | complete | Policy protections and diff/test flow | Read-only backlog/propose, brokered file reads, audited dry-run, cannot weaken safety or audit |
| 19 | Agent dashboard v1 | complete | Connector, audit, permission, memory views | Metadata/status only, secrets redacted, no personal-data reads |
| 20 | Feature review + release gate | complete | All selected batch work complete | Full tests, startup policy, manifest validation, docs validation, and tracking sync passed |

## Next Feature Set: Controlled Actions and Proactive Workflows

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Live validation and eval harness | complete | Current tracking release gate passed | Safe evals implemented; personal-data evals skipped by default; live runs opt-in |
| 2 | Unified Action Center | complete | Live validation harness scoped | Review/approval queue complete; actions do not execute directly and future execution must still go through ToolBroker |
| 3 | Calendar approved writes | complete | Action Center and per-action approval UX | CRITICAL per-action write drafts, exact preview, rollback notes, brokered stub execution; live native writes deferred |
| 4 | Reminders/tasks connector | complete | Connector decision notes and Action Center | Adapter/mock v1, selected-scope list approval, Action Center task creation, CRITICAL per-action writes; native provider deferred |
| 5 | Contacts approved edits | complete | Contacts read-only validated and Action Center ready | CRITICAL per-action draft/update/create stubs; field-level previews; live native provider and delete deferred |
| 6 | Email approved send | complete | Email draft-only live validation and Action Center ready | CRITICAL per-action Action Center send drafts, no bulk send, mock provider only; real provider deferred |
| 7 | Messages safe handoff / send decision | complete | Safe implementation decision record | Save/copy handoff only; automatic send remains deferred |
| 8 | Browser selected-tab / clipping connector | complete | Connector decision record and untrusted-content review | Explicit URL read/summarize/clip workflow complete; selected-tab native integration remains stubbed, disabled, and no history/cookie/profile access is added |
| 9 | Notes / knowledge capture | complete | Memory v2 and file policy review | Workspace-only capture inbox complete; no Apple Notes/private DB scraping; memory promotion goes through Memory v2 policy |
| 10 | Daily briefing v2 | complete | Live validation for v1 sources | Configurable opt-in sections complete; personal sections approval-gated; no hidden personal access or writes |
| 11 | Meeting follow-up workflow | complete | Meeting prep v1 and Action Center | Draft-only follow-up complete; suggested writes/sends become Action Center records only |
| 12 | Personal task extraction | complete | Email/messages/calendar selected-scope review | Extraction complete; task writes remain Action Center drafts only |
| 13 | Controlled self-improvement implementation loop | complete | Action Center, release gate, branch workflow | Branch-based implementation complete; cannot weaken policy, disable audit, grant permissions, or commit without approval |
| 14 | Scheduler / automation v1 | complete | Automation threat model and approval rules | Manual-run only; no background persistence; scheduled tool workflows still use ToolBroker; CRITICAL actions never execute automatically |
| 15 | Full feature maturity review | complete | Previous batch complete | Full tests, startup policy, capability manifest, safe eval, command registry validation, ToolBroker/default/approval scans, and docs sync passed |
| 16 | Native Skills Program foundation | queued | Prompt ledger/queue complete | Do not auto-install or enable unvetted skills |

## Completed Features

- M0-M11 baseline.
- LM Studio/Qwopus no-tool chat baseline.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger baseline.
- Weather connector pattern with Open-Meteo, NWS, WeatherKit stub, safe preferences, cache/rate limiting, alerts, and weather-only daily briefing.
- Web search/fetch/research mocked and provider-ready.
- Workspace file tools baseline.
- Memory baseline.
- Personal connector readiness gate.
- Calendar read-only selected-range connector.
- Calendar approved writes v1 with Action Center-gated draft/create/update/delete commands and no live external writes by default.
- Reminders / Tasks connector v1 with adapter/mock provider, brokered list/create/update/complete/delete tools, Action Center task creation, and no native Reminders writes by default.
- Contacts read-only selected-scope connector.
- Email metadata + selected-thread + draft-only assistant.
- Messages/text draft-only assistant with manual workspace fallback.
- Daily Briefing v1 with optional brokered weather, selected calendar range, email metadata, web topic search, dry-run, reminders stub, and no writes/sends.
- Meeting Prep v1 with brokered selected calendar event, optional approved contact lookup, optional web topic search, dry-run, and no writes/sends.
- Email Triage v1 with brokered metadata-only priority classification, optional selected-thread summary, draft-only reply, dry-run, and no send/delete/move/archive.
- Self-improvement backlog generator with brokered approved-file reads, dry-run, blocked safety-weakening suggestions, and ranked proposals.
- Agent Dashboard v1 with read-only `dashboard` and `status` commands.
- Unified Action Center v1 with `actions list/show/approve/deny/edit/clear-denied/export`, approval queue integration, redacted previews, one-time approval consumption, audit lifecycle events, and no direct execution path.
- Daily Briefing v2 with configurable opt-in weather, calendar, tasks, email metadata, web, memory preference, and suggested-action sections.
- Meeting Follow-Up v1 with brokered selected-event/workspace-notes reads and Action Center queued task/email/calendar suggestions.
- Personal Task Extraction v1 with brokered source reads and Action Center queued task drafts.
- Controlled Self-Improvement Implementation Loop v1 with approved proposal records, branch creation, brokered writes/tests/diff, and approval-gated commits.
- Scheduler / Automation v1 with explicit local schedule records, manual `schedule run`, audited lifecycle/run events, safe supported workflows, and no background runner.
- Prompt Ledger, Prompt Queue, and Prompt Pack tracking with reconstructed prompt statuses, queued/blocked prompt groups, prompt record directories, prompt pack splitting, prompt CLI commands, and prompt audit docs.
- PromptOps Workbench v1 with one-command prompt import from stdin/file/clipboard, next/copy/status/review commands, disabled-by-default runner, and safe-only autopilot guardrails.
- Command Registry + Manual QA System with 150 cataloged commands, generated command test matrix, legacy tracker, QA runbook, and read-only `commands` CLI inspection/validation commands.
- Disabled-by-default selected-scope calendar, contacts, email draft-only, and messages draft-only interfaces.
- Connector framework generalization.
- Feature maturity tracking.

## High-Risk Features Requiring Approval

- Calendar read-only selected date range.
- Calendar selected event read.
- Contacts read-only selected contact.
- Email metadata, selected thread read, summary, and draft reply.
- Messages selected thread read and draft reply.
- Memory storage of personal data.
- Filesystem delete and git commit.
- Any future calendar/contact write action.
- Any future email/text send action.

## Deferred Features

- Email/text sending.
- Live native Calendar write provider.
- Live native Reminders/Tasks provider.
- Contact writes.
- Browser selected-tab reader beyond safe stubs.
- WeatherKit JWT signing until decision record review.
- Live Messages connector until a safe permissioned path exists.
- Device location or IP geolocation.

## Blocked Features

- Messages live connector: blocked on safe permissioned implementation path.
- Broad personal-data workflows: blocked until approval UX, dry-run, audit review, and selected-scope live smoke are complete.
- Approved writes/sends: blocked until draft-only workflows and per-action approval UX are release-gated.

## Feature Order

1. SDLC release gate + roadmap reset.
2. Changelog, feature registry, roadmap, and `PROJECT_STATE.md`.
3. Connector framework generalization.
4. Capability manifest + policy normalization.
5. Runtime doctor + connector dashboard.
6. Approval UI + universal dry-run/preflight.
7. Source-grounded web research.
8. Workspace file assistant.
9. Memory v2 + safe context injection.
10. Personal connector readiness gate.
11. Calendar read-only connector.
12. Contacts read-only connector.
13. Email draft-only assistant.
14. Messages/text draft-only assistant.
15. Daily briefing workflow v1.
16. Meeting prep workflow.
17. Email triage workflow, draft-only.
18. Self-improvement backlog generator.
19. Agent dashboard v1.
20. Feature review + release gate.
21. Live validation and eval harness.
22. Unified Action Center.
23. Calendar approved writes.
24. Reminders/tasks connector.
25. Contacts approved edits.
26. Email approved send.
27. Messages safe handoff / send decision.
28. Browser selected-tab / clipping connector.
29. Notes / knowledge capture.
30. Daily briefing v2.
31. Meeting follow-up workflow.
32. Personal task extraction.
33. Controlled self-improvement implementation loop.
34. PromptOps Workbench v1.
35. Scheduler / automation v1.
36. Full feature maturity review.
