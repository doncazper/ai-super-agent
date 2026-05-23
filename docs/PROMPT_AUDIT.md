# Prompt Audit

This audit is a best-effort reconstruction from repo evidence. It should be updated after major prompt batches and before long autonomous runs.

## Audit Summary

| category | count | notes |
|---|---:|---|
| definitely completed | 75 | Inferred from implemented files, tests, docs, feature registry, maturity tracker, changelog, and completion report. |
| likely completed | 0 | No separate likely bucket is currently needed; uncertain items are left queued or blocked. |
| queued but not confirmed | 24 | Dogfood follow-ups, messaging planning, web acquisition, and provider doctor prompts remain queued. |
| blocked by approval gates | 2 | macOS approved iMessage send adapter and approved lead response send require explicit safety/approval gates. |
| superseded by later work | 2 | Weather-only briefing is superseded by Daily Briefing v2; early C1/C2 approval prompts are superseded for planning by the unified approval/Action Center foundation. |

## Definitely Completed

- BASELINE-M0-M11
- A0-LIVE-SMOKE-READINESS
- A1-RUNTIME-POLISH
- B1-WEB-SEARCH
- B2-WEB-FETCH-RESEARCH
- C1-CLI-APPROVAL-UI
- C2-DRY-RUN-PREFLIGHT
- D1-CALENDAR-READ
- D2-CONTACTS-READ
- E1-EMAIL-DRAFT
- E2-MESSAGES-DRAFT
- F1-INTEGRATION-HARNESS
- G1-HARDENING-REGRESSION
- H1-WEATHER-ABSTRACTION through H13-WEATHERKIT
- POST-TRACKING
- CONNECTOR-FRAMEWORK
- CAPABILITY-MANIFEST
- RUNTIME-DOCTOR
- APPROVAL-UI-FOUNDATION
- SOURCE-WEB-RESEARCH
- FILES-WORKSPACE
- MEMORY-V2
- PERSONAL-READINESS
- ACTION-CENTER
- CALENDAR-WRITES
- TASKS-CONNECTOR
- CONTACTS-WRITES
- EMAIL-SEND
- MESSAGES-HANDOFF
- BROWSER-CLIPPING
- KNOWLEDGE-CAPTURE
- DAILY-BRIEFING-V2
- MEETING-FOLLOWUP
- TASK-EXTRACTION
- SELF-IMPROVE-LOOP
- PROMPT-LEDGER-QUEUE
- PROMPT-PACK-IMPORT
- PROMPTOPS-WORKBENCH
- COMMAND-REGISTRY-QA
- SCHEDULER-V1
- FULL-FEATURE-MATURITY-REVIEW
- NATIVE-SKILLS-FOUNDATION
- SKILL-MARKETPLACE-SURVEY
- NATIVE-SKILL-VETTER
- NATIVE-SKILL-MANIFEST
- SKILL-FINDER-NATIVE
- PDF-WORKSPACE-SKILL
- CONTACTS-WRITES-HARDENING
- EMAIL-SEND-HARDENING
- MESSAGES-HANDOFF-HARDENING
- BROWSER-CLIPPING-COMPAT
- KNOWLEDGE-CAPTURE-TRUSTED-FILE
- PRIVACY-CENTER-V1
- LOCAL-STARTUP-ERGONOMICS
- BACKUP-RESTORE-MIGRATION-V1
- MODEL-ROUTER-PROMPT-EVALS
- SCHEDULER-V1-BACKUP-CREATE
- SELF-IMPROVE-COMMIT-ACTION-CHECKPOINT
- OVERNIGHT-RUNBOOK
- FULL-RELEASE-GATE-MATURITY-REVIEW
- OVERNIGHT-SAFE-6H
- SESSION-LOGGING-REPLAY
- DOGFOOD-COMMAND-SUITES
- FEEDBACK-CAPTURE-RATINGS
- SESSION-REVIEW-BUG-GENERATOR

## Queued But Not Confirmed

- REGRESSION-TEST-GENERATOR
- LIVE-TEST-RUNBOOK
- PRODUCT-QUALITY-DASHBOARD
- DOGFOOD-RELEASE-GATE
- APPLE-MESSAGING-ROADMAP
- MESSAGE-CHANNEL-ABSTRACTION
- MESSAGE-SAFETY-ACTION-CENTER
- LEAD-INBOX-ABSTRACTION
- IOS-CONFIRMED-COMPOSE
- MACOS-MESSAGES-PROBE
- MESSAGES-DRAFT-HANDOFF-WORKFLOW
- INCOMING-MESSAGE-STRATEGY
- APPLE-MESSAGES-BUSINESS
- LEAD-RESPONSE-DRAFTING
- MESSAGING-DOGFOOD-SUITES
- MESSAGING-RELEASE-GATE
- WEB-ACQUISITION-LAYER
- COST-AWARE-PROVIDER-POLICY
- SECRET-CONFIG-DOCTOR
- FREE-FIRST-WEB-ACQUISITION
- SERPAPI-FALLBACK
- WEATHER-PROVIDER-SELECTOR
- GMAIL-TELEGRAM-DOCTORS

## Blocked By Approval Gates

- MACOS-APPROVED-IMESSAGE-SEND: blocked until a safe permissioned path and explicit approval are documented.
- APPROVED-LEAD-RESPONSE-SEND: blocked until send-provider strategy and per-action approval UX are complete.

## Missing Evidence

- Regression-test generation from reviewed bug records still needs implementation evidence.
- Apple Messaging/iMessage strategy prompts have no implementation evidence yet beyond the existing messages safe handoff v1 and its Action Center verification hardening.
- Web Acquisition Layer and cost-aware provider prompts have no implementation evidence yet.
- Gmail/Telegram doctors have no implementation evidence yet.
- Future safe overnight self-improvement runs still require explicit user approval, even though the 2026-05-23 bounded run completed.

## Superseded

- H9-WEATHER-BRIEFING is superseded by DAILY-BRIEFING-V2 for broader daily briefing behavior.
- C1-CLI-APPROVAL-UI and C2-DRY-RUN-PREFLIGHT are superseded for current planning purposes by APPROVAL-UI-FOUNDATION and ACTION-CENTER.

## Next Recommended Prompt

REGRESSION-TEST-GENERATOR

Before running it:

1. Read only approved redacted bug reports from `bugs/`.
2. Do not turn bug text directly into policy-weakening instructions.
3. Generate tests only after reviewing candidate bugs.
4. Update `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and this audit after completion.
