# Prompt Queue

This queue is the current recommended prompt order. Do not run prompts out of order without updating this file and `docs/PROMPT_LEDGER.md`.

## Current Queue

| prompt_id | title | category | status | prerequisite_prompt_ids | approval_gate | expected_outputs | tests_expected | notes |
|---|---|---|---|---|---|---|---|---|
| FULL-FEATURE-MATURITY-REVIEW | Full feature maturity review | release-gate | completed | SCHEDULER-V1 | none | Maturity/registry/project-state release sync after Scheduler v1 | Full tests, safe eval, policy/manifest/docs validation | Completed 2026-05-23; release gate passed after Open-Meteo city/state geocode hardening. |
| NATIVE-SKILLS-FOUNDATION | Native Skills Program foundation | native-skills | queued | FULL-FEATURE-MATURITY-REVIEW | no personal-data access | Native skills foundation docs/interfaces | Unit/docs validation | Run after the full maturity review. |
| SKILL-MARKETPLACE-SURVEY | Skill marketplace survey | native-skills | queued | NATIVE-SKILLS-FOUNDATION | none | Survey and decision notes | Docs validation | Planning-first. |
| NATIVE-SKILL-VETTER | Native skill vetter | native-skills | queued | SKILL-MARKETPLACE-SURVEY | none | Safety/quality vetter | Unit tests | Keep vetting separate from installation. |
| NATIVE-SKILL-MANIFEST | Native skill manifest and loader | native-skills | queued | NATIVE-SKILL-VETTER | none | Manifest/loader | Unit tests | Do not auto-enable unvetted skills. |
| SKILL-FINDER-NATIVE | Skill finder native skill | native-skills | queued | NATIVE-SKILL-MANIFEST | none | Skill finder | Unit tests | No external installs by default. |
| PDF-WORKSPACE-SKILL | PDF workspace native skill | native-skills | queued | NATIVE-SKILL-MANIFEST | workspace-only | PDF workspace skill | Mock/unit tests | Workspace-bounded only. |
| SESSION-LOGGING-REPLAY | Session logging and replay system | dogfood | queued | PDF-WORKSPACE-SKILL | no personal data by default | Session logging/replay | Unit/integration tests | Redact secrets. |
| DOGFOOD-COMMAND-SUITES | Manual dogfood command suites | dogfood | queued | SESSION-LOGGING-REPLAY | none | Runbooks and command suites | Docs validation | Manual first. |
| FEEDBACK-CAPTURE-RATINGS | Feedback capture and ratings | dogfood | queued | DOGFOOD-COMMAND-SUITES | no private content by default | Feedback capture | Unit tests | Workspace storage only unless approved. |
| SESSION-REVIEW-BUG-GENERATOR | Session review and bug generator | dogfood | queued | FEEDBACK-CAPTURE-RATINGS | none | Bug generator | Unit tests | Reads approved logs only. |
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
| OVERNIGHT-RUNBOOK | Overnight self-improvement runbook | self-improvement | queued | GMAIL-TELEGRAM-DOCTORS | planning only | Runbook | Docs validation | No hidden persistence. |
| OVERNIGHT-SAFE-6H | Safe 6-hour overnight self-improvement run | self-improvement | blocked | OVERNIGHT-RUNBOOK | explicit automation approval required | Bounded run | Full tests before/after | Blocked until scheduler/runbook approval. |

## Completed This Run

| prompt_id | status | result |
|---|---|---|
| PROMPT-LEDGER-QUEUE | completed | Prompt ledger, queue, audit docs, CLI commands, and validation tests added. |
| PROMPT-PACK-IMPORT | completed | Prompt pack parser, validator, splitter, import-only CLI commands, docs, and tests added. |
| PROMPTOPS-WORKBENCH | completed | PromptOps one-command import/next/copy/status/review workflow, disabled runner, safe autopilot guardrails, docs, and tests added. |
| COMMAND-REGISTRY-QA | completed | Command registry, manual QA matrix, legacy tracker, QA runbook, read-only commands CLI, docs, and validation tests added. |
| SCHEDULER-V1 | completed | Manual-run Scheduler / Automation v1 with explicit local schedule records, audited lifecycle/run events, safe workflow allowlist, no hidden persistence, and tests added. |
| FULL-FEATURE-MATURITY-REVIEW | completed | Full feature maturity review and release gate passed; full tests, startup policy, capability manifest, safe eval, command registry, personal-default, CRITICAL approval, ToolBroker-bypass, and docs sync checks completed. |
