# Prompt Queue

This queue is the current recommended prompt order. Do not run prompts out of order without updating this file and `docs/PROMPT_LEDGER.md`.

## Current Queue

| prompt_id | title | category | status | prerequisite_prompt_ids | approval_gate | expected_outputs | tests_expected | notes |
|---|---|---|---|---|---|---|---|---|
| FULL-FEATURE-MATURITY-REVIEW | Full feature maturity review | release-gate | completed | SCHEDULER-V1 | none | Maturity/registry/project-state release sync after Scheduler v1 | Full tests, safe eval, policy/manifest/docs validation | Completed 2026-05-23; release gate passed after Open-Meteo city/state geocode hardening. |
| NATIVE-SKILLS-FOUNDATION | Native Skills Program foundation | native-skills | completed | FULL-FEATURE-MATURITY-REVIEW | no personal-data access | Native skills foundation docs/interfaces | Unit/docs validation and full suite | Completed 2026-05-23; docs/intake foundation only, no external skills installed or run. |
| SKILL-MARKETPLACE-SURVEY | Skill marketplace survey | native-skills | completed | NATIVE-SKILLS-FOUNDATION | none | Survey and decision notes | Docs validation and full suite | Completed 2026-05-23; research-only survey, matrix, and shortlist added. |
| NATIVE-SKILL-VETTER | Native skill vetter | native-skills | completed | SKILL-MARKETPLACE-SURVEY | none | Workspace-only static safety/quality vetter | Unit tests, startup validation, capability validation, command validation, full suite | Completed 2026-05-23; vetting remains separate from installation and execution. |
| NATIVE-SKILL-MANIFEST | Native skill manifest and loader | native-skills | completed | NATIVE-SKILL-VETTER | none | Metadata-only manifest/loader | Unit tests, docs validation, command validation, full suite | Completed 2026-05-23; manifests cannot auto-enable tools, execute code, install packages, or grant permissions. |
| SKILL-FINDER-NATIVE | Skill finder native skill | native-skills | completed | NATIVE-SKILL-MANIFEST | none | Skill finder | Unit tests, broker/audit tests, full suite | Completed 2026-05-23; local-only finder added with no external browse/install/execute behavior. |
| PDF-WORKSPACE-SKILL | PDF workspace native skill | native-skills | completed | NATIVE-SKILL-MANIFEST | workspace-only | PDF workspace skill | Unit tests, broker/audit tests, full suite | Completed 2026-05-23; read-only workspace PDF skill added, OCR/split/merge/writes deferred. |
| SESSION-LOGGING-REPLAY | Session logging and replay system | dogfood | completed | PDF-WORKSPACE-SKILL | no personal data by default | Session logging/replay | Unit/integration tests | Completed 2026-05-23; redacted session logging/replay added, raw reports gitignored, focused tests pass. |
| DOGFOOD-COMMAND-SUITES | Manual dogfood command suites | dogfood | completed | SESSION-LOGGING-REPLAY | none | Runbooks, suite YAML, CLI runner, and session integration | Unit/docs validation | Completed 2026-05-23; first manual `all_safe --session` dogfood run still recommended. |
| FEEDBACK-CAPTURE-RATINGS | Feedback capture and ratings | dogfood | completed | DOGFOOD-COMMAND-SUITES | no private content by default | Redacted session feedback capture | Unit tests | Completed 2026-05-23; feedback stores redacted session records and writes no memory. |
| SESSION-REVIEW-BUG-GENERATOR | Session review and bug generator | dogfood | completed | FEEDBACK-CAPTURE-RATINGS | none | Bug generator | Unit tests | Completed 2026-05-23; reads redacted logs/feedback only and creates local redacted bug records when requested. |
| REGRESSION-TEST-GENERATOR | Regression test generator from bugs | dogfood | queued | SESSION-REVIEW-BUG-GENERATOR | none | Test generator | Unit tests | Review before writing tests. |
| LIVE-TEST-RUNBOOK | Live test runbook and daily dogfood workflow | dogfood | queued | REGRESSION-TEST-GENERATOR | live services opt-in | Runbook | Docs validation | No personal live reads by default. |
| PRODUCT-QUALITY-DASHBOARD | Product quality dashboard | dogfood | queued | LIVE-TEST-RUNBOOK | none | Quality dashboard | Unit tests | Metadata/status only. |
| DOGFOOD-RELEASE-GATE | Dogfood system release gate | dogfood | queued | PRODUCT-QUALITY-DASHBOARD | none | Release gate evidence | Full tests | Stop on failures. |
| APPLE-MESSAGING-ROADMAP | Apple Messaging roadmap and decision records | messaging | queued | DOGFOOD-RELEASE-GATE | planning only | Decision records | Docs validation | No automation yet. |
| MESSAGE-CHANNEL-ABSTRACTION | Message channel abstraction | messaging | queued | APPLE-MESSAGING-ROADMAP | none | Abstraction/interface | Unit tests | No sends. |
| MESSAGE-SAFETY-ACTION-CENTER | Message safety policy and Action Center integration | messaging | queued | MESSAGE-CHANNEL-ABSTRACTION | HIGH/CRITICAL approval rules | Safety integration | Policy/approval tests | No send bypass. |
| LEAD-INBOX-ABSTRACTION | Lead Inbox abstraction | messaging | queued | MESSAGE-SAFETY-ACTION-CENTER | no broad ingestion | Lead inbox interface | Unit tests | No full history reads. |
| IOS-CONFIRMED-COMPOSE | iOS user-confirmed message compose bridge | messaging | queued | LEAD-INBOX-ABSTRACTION | user confirmation required | Compose bridge decision/stub | Unit/docs tests | No automatic send. |
| MACOS-MESSAGES-PROBE | macOS Messages automation feasibility probe | messaging | queued | IOS-CONFIRMED-COMPOSE | feasibility only | Probe report | Docs validation | No Messages DB scraping. |
| MESSAGES-DRAFT-HANDOFF-WORKFLOW | Messages draft/handoff workflow | messaging | queued | MACOS-MESSAGES-PROBE | approval for personal handoff | Draft/handoff polish | Unit tests | Existing v1 may satisfy; audit before work. |
| INCOMING-MESSAGE-STRATEGY | Incoming message strategy | messaging | queued | MESSAGES-DRAFT-HANDOFF-WORKFLOW | planning only | Strategy doc | Docs validation | No background readers. |
| MACOS-APPROVED-IMESSAGE-SEND | macOS approved iMessage send adapter | messaging | blocked | INCOMING-MESSAGE-STRATEGY | explicit approval and decision required | Send adapter only if approved | Security/approval tests | Blocked until safe path is approved. |
| APPLE-MESSAGES-BUSINESS | Apple Messages for Business provider strategy | messaging | queued | INCOMING-MESSAGE-STRATEGY | planning only | Provider strategy | Docs validation | No sends. |
| LEAD-RESPONSE-DRAFTING | Lead response drafting workflow | messaging | queued | APPLE-MESSAGES-BUSINESS | no sends | Drafting workflow | Unit tests | Draft-only. |
| APPROVED-LEAD-RESPONSE-SEND | Approved lead response send workflow | messaging | blocked | LEAD-RESPONSE-DRAFTING | explicit per-action send approval | Approved send workflow | Security/approval tests | Blocked until send provider is approved. |
| MESSAGING-DOGFOOD-SUITES | Messaging dogfood suites | messaging | queued | LEAD-RESPONSE-DRAFTING | no live send by default | Dogfood suite | Unit/docs tests | Send tests mocked only unless approved. |
| MESSAGING-RELEASE-GATE | Messaging release gate | messaging | queued | MESSAGING-DOGFOOD-SUITES | none | Release gate evidence | Full tests | Stop before unsafe sends. |
| WEB-ACQUISITION-LAYER | Web Acquisition Layer | web-acquisition | queued | MESSAGING-RELEASE-GATE | none | Provider acquisition layer | Unit tests | Public web only. |
| COST-AWARE-PROVIDER-POLICY | Cost-aware provider policy | web-acquisition | queued | WEB-ACQUISITION-LAYER | none | Cost policy | Policy tests | No surprise paid calls. |
| SECRET-CONFIG-DOCTOR | Secret/config doctor | provider-doctor | queued | COST-AWARE-PROVIDER-POLICY | none | Doctor checks | Unit tests | Redact secrets. |
| FREE-FIRST-WEB-ACQUISITION | Free-first web acquisition | web-acquisition | queued | SECRET-CONFIG-DOCTOR | none | Free-first provider path | Mock/unit tests | No scraping terms violations. |
| SERPAPI-FALLBACK | Optional SerpAPI fallback | web-acquisition | queued | FREE-FIRST-WEB-ACQUISITION | API key opt-in | Optional fallback provider | Mock/unit tests | Do not hard-code keys. |
| WEATHER-PROVIDER-SELECTOR | Weather provider selector | weather | queued | SERPAPI-FALLBACK | none | Selector polish | Unit tests | Existing selector may partly satisfy. |
| GMAIL-TELEGRAM-DOCTORS | Gmail/Telegram doctors | provider-doctor | queued | WEATHER-PROVIDER-SELECTOR | no personal reads | Provider diagnostics | Unit tests | Config only. |
| OVERNIGHT-RUNBOOK | Overnight self-improvement runbook | self-improvement | completed | GMAIL-TELEGRAM-DOCTORS | planning only | Runbook and `improve overnight-plan` | Unit/docs validation and full suite | Completed out of queue order by user request; no hidden persistence or unattended run approval. |
| OVERNIGHT-SAFE-6H | Safe 6-hour overnight self-improvement run | self-improvement | completed | OVERNIGHT-RUNBOOK | user-approved bounded safe-mode run | Bounded run | Full tests before/after | Completed bounded safe-mode run on `agent/overnight-2026-05-23`; safe docs/tests/diagnostics/tracking only, no background persistence or commits. Future overnight runs require explicit approval. |

## Completed This Run

| prompt_id | status | result |
|---|---|---|
| PROMPT-LEDGER-QUEUE | completed | Prompt ledger, queue, audit docs, CLI commands, and validation tests added. |
| PROMPT-PACK-IMPORT | completed | Prompt pack parser, validator, splitter, import-only CLI commands, docs, and tests added. |
| PROMPTOPS-WORKBENCH | completed | PromptOps one-command import/next/copy/status/review workflow, disabled runner, safe autopilot guardrails, docs, and tests added. |
| COMMAND-REGISTRY-QA | completed | Command registry, manual QA matrix, legacy tracker, QA runbook, read-only commands CLI, docs, and validation tests added. |
| SCHEDULER-V1 | completed | Manual-run Scheduler / Automation v1 with explicit local schedule records, audited lifecycle/run events, safe workflow allowlist, no hidden persistence, and tests added. |
| FULL-FEATURE-MATURITY-REVIEW | completed | Full feature maturity review and release gate passed; full tests, startup policy, capability manifest, safe eval, command registry, personal-default, CRITICAL approval, ToolBroker-bypass, and docs sync checks completed. |
| NATIVE-SKILLS-FOUNDATION | completed | Native Skills Program foundation docs, intake process, criteria, candidate registry, risk model, template, tracking docs, and validation tests added without installing or running external skills. |
| SKILL-MARKETPLACE-SURVEY | completed | Skill marketplace survey, native candidate matrix, and top shortlist added as research-only docs without installing or running external skills. |
| NATIVE-SKILL-VETTER | completed | Native skill vetter v1 added with brokered workspace-only static analysis commands, tests, capability manifest entries, command registry updates, and docs. |
| NATIVE-SKILL-MANIFEST | completed | Metadata-only native skill manifest discovery, validation, registry, doctor/dashboard status, CLI commands, built-in vetter manifest, docs, and tests added. |
| SKILL-FINDER-NATIVE | completed | Brokered local-only native skill finder added with manifest/candidate/feature/maturity search, readiness and approval reporting, command registry updates, and tests. |
| PDF-WORKSPACE-SKILL | completed | Brokered read-only PDF workspace native skill added with info/text/summary/table commands, limits, untrusted-document labels, audit coverage, and tests. |
| CONTACTS-WRITES-HARDENING | completed | Contacts approved edits hardening verified low-level Action Center action-id enforcement, approved-preview argument matching, docs, and tests. |
| EMAIL-SEND-HARDENING | completed | Email approved send hardening verified low-level Action Center action-id enforcement, approved-reviewed-draft argument matching, docs, and tests. |
| MESSAGES-HANDOFF-HARDENING | completed | Messages safe handoff hardening verified low-level Action Center action-id enforcement, approved-reviewed-draft argument matching, docs, and tests. |
| BROWSER-CLIPPING-COMPAT | completed | Browser clipping compatibility pass added canonical `browser.read_url`, `browser.summarize_url`, and `browser.selected_tab` capability tracking while retaining legacy aliases; selected-tab remains a disabled stub. |
| KNOWLEDGE-CAPTURE-TRUSTED-FILE | completed | Knowledge Capture file imports now default to `UNTRUSTED_DOCUMENT` and can be explicitly marked `TRUSTED_USER` with `--trusted-user`; broker/audit behavior remains unchanged. |
| PRIVACY-CENTER-V1 | completed | Privacy Center / Data Inventory v1 added metadata-only local privacy status, inventory, redacted export, confirmed brokered memory deletion, audit summary, and permissions views. |
| LOCAL-STARTUP-ERGONOMICS | completed | Local startup ergonomics added a Python 3.11 guard, local `scripts/agent` launcher, LM Studio model setup docs, command registry entry, and tests. |
| BACKUP-RESTORE-MIGRATION-V1 | completed | Backup / Restore / Migration v1 added brokered redacted backup create/list/inspect/verify/export/restore, manifest integrity checks, approval-gated restore, policy-weakening restore blocks, docs, and tests. |
| MODEL-ROUTER-PROMPT-EVALS | completed | Model-router benchmark and prompt quality evals added safe fixture-backed model/router/prompt commands, report output, docs, and tests. |
| SCHEDULER-V1-BACKUP-CREATE | completed | Scheduler / Automation v1 now includes optional redacted-only `backup_create` schedules that call brokered `backup.create`, audit tool calls, and reject unredacted args. |
| SELF-IMPROVE-COMMIT-ACTION-CHECKPOINT | completed | Controlled self-improvement now has an explicit `improve create-action-for-commit` checkpoint that runs brokered tests/diff and queues a pending Action Center commit action without committing. |
| OVERNIGHT-RUNBOOK | completed | Overnight self-improvement safe-mode runbook, report template, report directory, planner command, docs, and tests added without approving or running unattended automation. |
| FULL-RELEASE-GATE-MATURITY-REVIEW | completed | Full release gate and feature maturity review passed locally with full tests, startup policy, manifest validation, safe eval, command/native-skill validation, ToolBroker/default/approval scans, and docs sync. |
| OVERNIGHT-SAFE-6H | completed | Approved bounded safe-mode run completed two low-risk cycles: tracking sync plus overnight report-template validation; full suite passed and no approval/personal-data/package/network/persistence gate was hit. |
| SESSION-REVIEW-BUG-GENERATOR | completed | Session review and local redacted bug generator added with `session review`, `bugs list/show/export`, P0 safety classification, docs, command registry entries, and tests. |
