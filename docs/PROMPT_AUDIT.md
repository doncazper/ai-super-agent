# Prompt Audit

This audit is a best-effort reconstruction from repo evidence. It should be updated after major prompt batches and before long autonomous runs.

Completion evidence classifications: `complete_verified`, `likely_complete`, `partial`, `no_evidence`, `failed`, `blocked`, `superseded`, and `stale`.

## Audit Summary

| category | count | notes |
|---|---:|---|
| definitely completed | 254 | Inferred from implemented files, tests, docs, feature registry, maturity tracker, changelog, completion report, prompt tracker release-gate docs, prompt completion evidence, and local validation through the global launcher and remote/main duplicate cleanup passes. |
| likely completed | 0 | No separate likely bucket is currently needed; uncertain items are left queued or blocked. |
| queued but not confirmed | 4 | Queue now explicitly prioritizes `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01` before returning to standing feature work such as `news-provider-registry-status-commands` and platform manifest/startup follow-ups. |
| blocked by missing source files | 0 | Creative Media pack is now imported and complete through `MEDIA-12`; Secrets pack remains `needs_review` because it has not been imported/run in this pass. |
| blocked by approval gates | 0 | No queued prompt is currently blocked in prompt tracking. |
| superseded by later work | 1 | Superseded rows remain documented below where older tracking concepts were replaced by mature features. |

## Dirty-Tree Blocked Prompt Audit Snapshot

- snapshot_at: 2026-05-26 after `RUN-DIRTY-TREE-BLOCKED-PROMPTS-IN-ORDER-01`
- current_active_prompt: none
- completed_prompt: `RUN-DIRTY-TREE-BLOCKED-PROMPTS-IN-ORDER-01`
- evidence: repo root verified as `/Users/sambehdjou/Documents/AI Super Agent`; local `main` and `origin/main` both point at `148f10f`; duplicate copied-file scan found no `* 2.*` files; safety validations passed; `docs/reconciliation/DIRTY_TREE_BLOCKED_PROMPT_AUDIT.md` and `docs/reconciliation/BLOCKED_PROMPT_EXECUTION_PLAN.md` were added.
- decision: no feature prompt or pack was executed because the Daydream import/tracker set remains uncommitted active dirty work. Duplicate-file and remote/main blockers are resolved, but the tree is not clean enough to mix in another large prompt-pack execution.
- classification_summary: launcher/canonical/performance/secrets/media/codebug/NLCMD/QA are completed; AIHUB v2, AuthScan, Writing, Memory Kernel, Bug Intelligence, Self-Heal, and Daydream remain not-run or queued; AIHUB v1 is superseded by v2; stale queued `REDDIT-OAUTH-CONFIG-DOCTOR.md` needs separate reconciliation.
- validation: `git diff --check`, `./scripts/agent secrets scan`, `./scripts/agent git preflight`, `./scripts/agent commands validate`, and `make policy-check` passed.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## Duplicate Cleanup GH Auth Git Boundary Snapshot

- snapshot_at: 2026-05-26 after `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01`
- current_active_prompt: none
- completed_prompt: `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01`
- evidence: repo root verified as `/Users/sambehdjou/Documents/AI Super Agent`; fresh `* 2.*` duplicate scan found no files; `gh` exists but is not authenticated; normal `git push --dry-run` failed because local `main` has no upstream; explicit dry-run push to `origin/main` failed as non-fast-forward; added Git boundary report and updated remote-main, duplicate cleanup, artifact, project state, ledger, queue, audit, and completion docs.
- validation: secrets scan passed with placeholder-only tracked findings; git preflight passed for tracked scope; command registry validation passed with 603 commands; startup policy/capability validation passed; `git diff --check` passed.
- commit_push_status: no files were staged, committed, or pushed because local `main` and `origin/main` are unrelated and force push / unrelated-history merge / rebase are forbidden.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## Writing Naturalizer and Voice Polish Request Snapshot

- snapshot_at: 2026-05-26 after WRITE preflight
- requested_pack: `writing-naturalizer-voice-polish-v1`
- source_file: `prompts/packs/writing-naturalizer-voice-polish-v1.promptpack.md`
- import_status: not imported
- current_active_prompt: none
- WRITE-01 through WRITE-18: not queued, not active, not completed
- status: blocked before import/run
- blockers: dirty uncommitted launcher/cleanup worktree, newly untracked `prompts/packs/bug-intelligence-and-failure-capture-v1.promptpack.md`, local `main` has no upstream, `origin/main` is unrelated initial history, and repository rules require a clean commit/remote boundary plus import-only/no automatic whole-pack execution before starting another large prompt pack.
- validation: secrets scan passed with placeholder-only tracked findings; git preflight passed for tracked scope; command registry validation passed with 599 commands; startup policy/capability validation passed; `git diff --check` passed.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## GLOBAL-LAUNCHER-REPO-DISCOVERY-SWITCHING-01 Snapshot

- snapshot_at: 2026-05-26 after scoped launcher repo discovery/switching hardening
- current_active_prompt: none
- completed_prompt: `GLOBAL-LAUNCHER-REPO-DISCOVERY-SWITCHING-01`
- evidence: implemented strong launcher repo marker verification, current Git-root installer defaults, bounded safe candidate discovery, `--repo-status`, `--find-repos`, `--set-repo`, stricter `--repair-path`, generated-wrapper discovery parity, `last_repo_verification_status`, docs/registry/maturity/roadmap updates, and natural-language intent-index adjustment so unknown requests do not match launcher commands.
- validation: `tests/launcher` 40 passed; launcher plus command-registry tests 46 passed; full suite 1763 passed; command registry validation passed with 603 commands; startup policy/capability validation passed; `git diff --check` passed; installer dry-runs wrote nothing.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## Authorized Deep Scan and Source Acquisition Request Snapshot

- snapshot_at: 2026-05-26 after AUTHSCAN preflight
- requested_pack: `authorized-deep-scan-and-source-acquisition-v1`
- source_file: `prompts/packs/authorized-deep-scan-and-source-acquisition-v1.promptpack.md`
- import_status: not imported
- current_active_prompt: none
- AUTHSCAN-01 through AUTHSCAN-16: not queued, not active, not completed
- status: blocked before import/run
- blockers: dirty uncommitted launcher/cleanup worktree, newly untracked `prompts/packs/bug-intelligence-and-failure-capture-v1.promptpack.md`, local `main` has no upstream, `origin/main` is unrelated initial history, and repository rules require a clean commit/remote boundary before starting another large prompt pack.
- validation: secrets scan passed with placeholder-only tracked findings; git preflight passed for tracked scope; command registry validation passed with 599 commands; startup policy/capability validation passed; `git diff --check` passed.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01 Snapshot

- snapshot_at: 2026-05-26 after `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01`
- current_active_prompt: none
- completed_prompt: `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01`
- evidence: removed 182 exact duplicate copied files and 2 empty duplicate directories after hash/cmp checks; moved the one differing stale source copy to ignored duplicate-file quarantine; added `docs/reconciliation/DUPLICATE_FILE_CLEANUP_REPORT.md`; added `docs/git/REMOTE_MAIN_RECONCILIATION_PLAN.md`; updated artifact tracking, project state, prompt queue, prompt ledger, completion report, and changelog.
- remote_main_status: local `main` has no upstream; `origin/main` is `5115a76 Initial commit`; local `main` has no merge-base with `origin/main`; no merge, rebase, branch deletion, force push, commit, or push was performed.
- next_action: create a clean commit boundary and choose a human-approved remote-main plan before importing AIHUB or another large prompt pack.

## AI Ecosystem Intelligence v2 Re-Request Snapshot

- snapshot_at: 2026-05-26 after second AIHUB preflight
- requested_pack: `ai-ecosystem-intelligence-v2`
- source_file: `prompts/packs/ai-ecosystem-intelligence-v2.promptpack.md`
- import_status: not imported
- current_active_prompt: none
- AIHUB-01 through AIHUB-20: not queued, not active, not completed
- status: blocked before import/run
- blockers: dirty uncommitted launcher/cleanup worktree, newly untracked `prompts/packs/bug-intelligence-and-failure-capture-v1.promptpack.md`, local `main` has no upstream, `origin/main` is unrelated initial history, and repository rules require a clean commit/remote boundary before starting another large prompt pack.
- validation: secrets scan passed with placeholder-only tracked findings; git preflight passed for tracked scope; command registry validation passed with 599 commands; startup policy/capability validation passed; `git diff --check` passed.
- next_action: `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01`

## SOURCE-TRUTH-RECONCILE-01 Snapshot

- snapshot_at: 2026-05-25 after `SOURCE-TRUTH-RECONCILE-01`
- current_active_prompt: none
- evidence: added `docs/reconciliation/*`; reconciled stale queue/ledger rows for SKILL, CODEBUG, NLCMD, and QA prompts; changed recovered Media/Secrets pack imports to `needs_review`
- validation: command registry validation passed; policy-check passed; doctor passed; full suite passed with 1493 passed and 1 skipped; safe eval passed with 58 pass, 0 fail, 6 skipped; prompt audit passed with active_count 0 and blocked_count 0; safe dogfood dry-run passed
- next_action: after completion, return to `news-provider-registry-status-commands` unless the user chooses clean release-candidate boundary work first

## QA-FE-BE-01 Snapshot

- snapshot_at: 2026-05-25 after `QA-FE-BE-01`
- current_active_prompt: none
- completed_prompt: `QA-FE-BE-01`
- evidence: added `agent/qa/api_models.py`, `agent/qa/service.py`, service-backed `agent/qa/dashboard.py`, frontend/backend boundary docs, API contract docs, regression tests, command registry/test matrix updates, and tracker updates
- validation: boundary/dashboard tests 13 passed; QA tests 56 passed; full suite 1493 passed, 1 skipped; command registry validation passed; startup policy and capability manifest validation passed; `qa dashboard` and `qa status` smokes passed
- next_action: return to `news-provider-registry-status-commands` unless the user chooses release hardening or prompt-tracker cleanup first

## Creative Media Generation Controlled Batch Snapshot

- snapshot_at: 2026-05-25 after `MEDIA-12`
- requested_pack: `creative-media-generation-v1`
- expected_source_file: `prompts/packs/creative-media-generation-v1.promptpack.md`
- current_active_prompt: none
- status: completed_verified
- completed_in_batch: `MEDIA-01` through `MEDIA-12`
- queued_remaining_in_batch: none
- evidence: prompt pack validated/imported, `prompts/completed/MEDIA-01.md` through `MEDIA-12.md` exist, completion report contains MEDIA-01 through MEDIA-12 evidence, creative media docs/tests/commands exist, full suite passed with 1580 tests, focused media release suite passed with 77 tests, command registry validation passed with 529 commands, and policy-check passed.
- next_action: return to `news-provider-registry-status-commands` unless the user selects a separate future Creative Media provider implementation prompt.

## Command QA Controlled Batch Snapshot

- snapshot_at: 2026-05-25 after `QA-10`
- imported_pack: `command-qa-sandbox-self-heal-v1`
- current_active_prompt: none
- completed_in_batch: `QA-01` through `QA-10`
- queued_remaining_in_batch: none
- prompt_audit_result: active_count 0, completed_count 235, queued_count 3, blocked_count 0, superseded_count 1, completed_missing_evidence empty.
- tracker_fix: `QA-10` was marked complete with full-suite, command-registry, policy-check, command-QA eval, and dogfood dry-run evidence.
- next_action: return to the standing next prompt `news-provider-registry-status-commands`, or run clean release-candidate boundary work first if the user wants hardening before more feature expansion.

## CODEBUG Controlled Batch Snapshot

- snapshot_at: 2026-05-25 during `CODEBUG-06`
- imported_pack: `codebase-bug-review-and-hardening-v1`
- current_active_prompt: `CODEBUG-06`
- completed_in_batch: `CODEBUG-01`, `CODEBUG-02`, `CODEBUG-03`, `CODEBUG-04`, `CODEBUG-05`
- queued_remaining_in_batch: `CODEBUG-07`, `CODEBUG-08`
- prompt_audit_result: active_count 1, completed_count 212, queued_count 5, completed_missing_evidence empty.
- tracker_fix: `docs/PROMPT_QUEUE.md` CODEBUG rows were updated from imported `queued` defaults to the current controlled-batch statuses with evidence notes.
- next_action: continue to `CODEBUG-07` after `CODEBUG-06` is marked complete.

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
- PTM-01 through PTM-10
- SKILL-01 through SKILL-10
- COMMAND-REGISTRY-QA
- SCHEDULER-V1
- FULL-FEATURE-MATURITY-REVIEW
- INTERNET-DOGFOOD-EVAL-SUITE
- REDDIT-FORUM-INTELLIGENCE-TRACK
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
- REGRESSION-TEST-GENERATOR
- LIVE-TEST-RUNBOOK
- PRODUCT-QUALITY-DASHBOARD
- DOGFOOD-RELEASE-GATE
- COST-AWARE-PROVIDER-POLICY
- SECRET-CONFIG-DOCTOR
- FREE-FIRST-WEB-ACQUISITION
- SERPAPI-FALLBACK
- WEATHER-PROVIDER-SELECTOR
- GMAIL-TELEGRAM-DOCTORS
- APPLE-MESSAGING-ROADMAP
- apple-messaging-roadmap-track
- MESSAGE-CHANNEL-ABSTRACTION
- MESSAGE-SAFETY-ACTION-CENTER
- LEAD-INBOX-ABSTRACTION
- IOS-CONFIRMED-COMPOSE
- MACOS-MESSAGES-PROBE
- MESSAGES-DRAFT-HANDOFF-WORKFLOW
- INCOMING-MESSAGE-STRATEGY
- MACOS-APPROVED-IMESSAGE-SEND
- APPLE-MESSAGES-BUSINESS
- LEAD-RESPONSE-DRAFTING
- ORCH-01 through ORCH-10
- MESSAGING-DOGFOOD-SUITES
- MESSAGING-RELEASE-GATE
- INTERNET-ACCESS-RELEASE-GATE
- WEB-COST-AWARE-PROVIDER-POLICY
- WEB-ACQUISITION-LAYER-CORE
- WEB-ROBOTS-SITEMAP-FEED-SUPPORT
- WEB-SEARCH-PROVIDER-REGISTRY
- SEARXNG-PROVIDER
- BRAVE-PROVIDER
- SERPAPI-FALLBACK
- WEB-FETCH-EXTRACTION-HARDENING
- SOURCE-GROUNDED-RESEARCH-V1
- INTERNET-ROUTING-POLICY
- REDDIT-OAUTH-CONFIG-DOCTOR
- REDDIT-READ-ONLY-CONNECTOR
- REDDIT-SEARCH-WORKFLOWS
- REDDIT-THREAD-FETCH-NORMALIZATION
- REDDIT-SOURCE-GROUNDED-SUMMARIZATION
- REDDIT-RETENTION-CACHE-COMPLIANCE
- FORUM-LANGUAGE-DETECTION-TRANSLATION
- CROSS-LANGUAGE-FORUM-RESEARCH-WORKFLOW
- CROSS-PLATFORM-ARCHITECTURE-ROADMAP
- PLATFORM-CAPABILITY-REGISTRY
- PLATFORM-BRIDGE-BASE-INTERFACES
- PLATFORM-CONFIG-PATHS-DETECTION
- PLATFORM-DOCTOR-CAPABILITY-COMMANDS
- PLATFORM-BRIDGE-STUBS
- APP-BRIDGE-API-CONTRACT
- CROSS-PLATFORM-RELEASE-GATE
- news-intelligence-roadmap

## Queued But Not Confirmed

- news-provider-registry-status-commands
- PLATFORM-CAPABILITY-MANIFEST-MAPPING
- PLATFORM-STARTUP-LAZYLOAD-GUARDRAILS

## Blocked By Approval Gates

- none.

## Missing Evidence

- MATURITY-AUDIT-01 found prompt tracker disagreements on 2026-05-25: `news-capability-manifest-provider-policy` is complete in the ledger/project state but was still listed as queued here; `docs/PROMPT_QUEUE.md` and `docs/PROMPT_LEDGER.md` still contain stale imported `SKILL-*` queued rows despite completed native-skill release evidence; `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md` appears stale because Reddit OAuth/config doctor completion evidence exists. See `docs/productization/PROMPT_TRACKER_MISSED_PROMPTS_AUDIT.md`.
- PTM-01 through PTM-10 are complete with targeted tests, prompt tracker docs, and release-gate evidence.
- Apple Messaging/iMessage implementation prompts now have `MESSAGE-CHANNEL-ABSTRACTION` evidence for no-send schemas, registry, validation, previews, brokered metadata/draft inspection, CLI commands, command registry, and tests. `MESSAGE-SAFETY-ACTION-CENTER` adds brokered draft creation and CRITICAL Action Center send-action proposals with exact local previews, draft-edit approval invalidation, and audit redaction. `LEAD-INBOX-ABSTRACTION` adds a mock-only, brokered lead model/provider/classifier/draft/follow-up foundation with no real provider reads, sends, CRM sync, or memory writes by default. `IOS-CONFIRMED-COMPOSE` adds an agent-side local handoff payload/status/result interface with no iOS app and no silent send. `MACOS-MESSAGES-PROBE` adds metadata-only macOS feasibility probing with no private DB, Full Disk Access, account/message reads, UI Send scripting, or send path. `MESSAGES-DRAFT-HANDOFF-WORKFLOW` adds local draft-id handoff ergonomics, `messages draft`, `messages handoff`, draft-id save/copy approval flow, and no-send Lead Inbox draft creation. `INCOMING-MESSAGE-STRATEGY` adds a manual/mock inbound inbox with workspace-only imports, `UNTRUSTED_MESSAGE` labels, no `chat.db`/Full Disk Access/watcher/send, Lead Inbox candidate metadata, and draft-only replies. `MACOS-APPROVED-IMESSAGE-SEND` adds a disabled-by-default, allowlist/live-probe/Action-Center-gated macOS send adapter with no private DB, no Full Disk Access, no bulk/group/attachment sends, and unsupported fallback. `APPLE-MESSAGES-BUSINESS` adds a mock/local Apple Messages for Business provider stub with config-only doctor/status, local mock inbound Lead Inbox mapping, draft-only MessageDraft response creation, disabled future CRITICAL send, and no live provider calls, sends, private Messages DB access, Full Disk Access, hidden polling, credential printing, or memory writes. `APPROVED-LEAD-RESPONSE-SEND` adds CRITICAL exact-preview lead send proposals, no approval reuse, draft-edit invalidation, iOS compose handoff, manual fallback, macOS gate delegation, unsupported-channel fallback, and no bulk/auto-send/memory write.
- Agent Runtime Orchestration ORCH-01 through ORCH-10 are complete. Recovery on 2026-05-23 found stale queued ORCH rows in `docs/PROMPT_LEDGER.md`; those rows were corrected to completed entries while `docs/PROMPT_QUEUE.md`, completed prompt files, runtime docs, runtime tests, and completion report already showed completion.
- Web Acquisition Layer is superseded by `FREE-FIRST-WEB-ACQUISITION`, which has implementation/test/docs evidence for brokered cache, robots, sitemap, RSS/Atom, direct public URL acquisition, untrusted wrapping, blocked-page unavailability, and paid-provider skip defaults.
- Internet Access release gate and roadmap reset is complete as docs/tracking only. It adds no provider calls or live web behavior; it defines the future track for provider registry, SearXNG/Brave hardening, safe fetch/extraction, source grounding, citations, cache/index, official APIs, dogfood/evals, and final release gate.
- WEB-COST-AWARE-PROVIDER-POLICY is complete as a hardening pass after the Internet Access release gate. It adds brokered read-only provider policy inspection commands, exact free-first config defaults, deterministic decision fields, query redaction in audit logs, no query-history persistence, and no provider API calls.
- WEB-ACQUISITION-LAYER-CORE is complete as a central planning/status layer around the brokered acquisition tools. It adds `agent.web_acquisition` request/result/source/provider models, cost-aware provider-decision wrapping, no-fetch `web.source_status`, command registry coverage, and focused tests while preserving no paid defaults, no query/content memory, and no bypass behavior.
- WEB-ROBOTS-SITEMAP-FEED-SUPPORT is complete for core robots/sitemap/feed parser modules, alias capabilities, default limits, malformed/timeout/max-limit/blocklist/audit tests, and docs.
- WEB-ROBOTS-SITEMAP-FEED-SUPPORT-REFRESH is complete for RSS/Atom MIME allowlist hardening, sitemap/feed binary denial, TTL cache regressions, command registry evidence refresh, full-suite validation, and prompt audit with zero active prompts.
- WEB-SEARCH-PROVIDER-REGISTRY is complete for local v1 as a metadata-only provider framework. It adds `agent.web_acquisition.search`, normalized search result/response schemas, setup/unknown-provider errors, brokered `web.search_providers`, explicit provider setup hints, command registry rows, docs, and tests without adding live provider API calls.
- SEARXNG-PROVIDER is complete for local v1. It adds a configured/self-hosted-only SearXNG provider, disabled-by-default env config, JSON result normalization, setup hints for missing base URL or disabled JSON output, timeout/403/429/malformed-response handling, brokered `web.searxng.doctor`, connector status metadata, docs, and mocked tests without adding a public instance default, paid API use, query-history persistence, or live provider call in validation.
- BRAVE-PROVIDER is complete for local v1. It adds disabled-by-default Brave Search provider hardening, config-only `web.brave.doctor`, `connectors status brave`, explicit `web search --provider brave`, paid/quota policy gating, key/query redaction, mocked normalization/error/rate-limit/audit tests, and no search-history persistence.
- SERPAPI-FALLBACK was reverified/hardened on 2026-05-24. It now documents and tests disabled-by-default `SERPAPI_ENABLED=false`, explicit `web.search.serpapi`/`web search --provider serpapi`/`research --provider serpapi`, config-only `web.serpapi.doctor`, paid/quota gating with a nonzero daily cap, key/query redaction, mocked normalization/error/rate-limit/audit tests, no search-history persistence, and no CAPTCHA/paywall/login/anti-bot bypass behavior.
- WEB-FETCH-EXTRACTION-HARDENING is complete for local v1. It adds shared safe fetch/extraction helper modules, brokered `web fetch`, `web extract`, and `web metadata` commands, structured FetchResult fields, URL/domain/scheme validation, tracking stripping, timeout/redirect/content-type/size bounds, metadata extraction, script/event-handler stripping, prompt-injection wrapping, blocked/CAPTCHA-page unavailable reporting, and no web-content memory storage by default.
- SOURCE-GROUNDED-RESEARCH-V1 is complete for local v1. It hardens brokered `research` so returned answers include real source URLs, retrieved timestamps, provider metadata, coverage/limitations, fetch failures, snippet-only labeling, and no query/web-content memory persistence by default.
- INTERNET-ROUTING-POLICY is complete for local v1. It adds deterministic internet-routing metadata, read-only `router explain`, richer `preflight` route fields, current/live/source-required/citation/URL routing, stable/local/no-tools clean routing, prompt-injection-like routing suppression, command registry coverage, and tests without provider calls during routing.
- REDDIT-PROVIDER-POLICY-COMPLIANCE is complete for scaffold v1. It adds disabled-by-default Reddit config, OAuth-required compliance metadata, denied unauthenticated/web-fallback behavior, hard-false training policy, disabled capability manifest placeholders, retention/rate-limit docs, and regression tests without OAuth implementation, Reddit API calls, content fetch, scraping, write actions, permanent user-content storage, or new CLI commands.
- REDDIT-OAUTH-CONFIG-DOCTOR is complete for local diagnostics v1. It adds brokered `reddit doctor`, `reddit status`, explicit OAuth-only `reddit auth-check`, `connectors status reddit`, setup hints, secret redaction, tracked `.env` and repo-local token warnings, generic user-agent warnings, audit evidence, command registry rows, docs, and tests without fetching Reddit posts/comments/threads, scraping, writes, permanent user-content storage, or training use.
- REDDIT-READ-ONLY-CONNECTOR is complete for local mocked v1. It adds an official Data API-only client/provider, normalized Reddit models, brokered search/subreddit/post/comments/cache/retention commands, rate-limit metadata, author redaction by default, TTL cache/retention sweep, deleted/removed content handling, setup-required disabled/OAuth-missing behavior, command registry rows, docs, and tests without Reddit web scraping fallback, unauthenticated traffic, writes, content training, permanent user-content storage, or search-history persistence.
- REDDIT-SEARCH-WORKFLOWS is complete for local mocked v1. It adds brokered Reddit search options for subreddit, sort, time, limit, and advisory language; snippet-only result labels; source IDs and permalinks; local `reddit explain-result <source_id>` metadata lookup; setup-required disabled/OAuth-missing behavior; sensitive-query redaction; no search-history persistence; command registry rows; docs; and tests without Reddit web scraping fallback, unauthenticated traffic, writes, paid provider default, content training, permanent user-content storage, or live Reddit calls by default.
- REDDIT-THREAD-FETCH-NORMALIZATION is complete for local mocked v1. It adds brokered Reddit thread fetch and thread-export commands, URL/ID parsing, comment tree and flattened comments, source references, bounded max-comment handling, removed-comment handling, author redaction, workspace-only untrusted exports, command registry rows, docs, and tests without Reddit web scraping fallback, unauthenticated traffic, writes, content training, permanent thread storage, or live Reddit calls by default.
- REDDIT-SOURCE-GROUNDED-SUMMARIZATION is complete for local mocked v1. It adds deterministic Reddit thread/search summaries plus consensus, pros-cons, complaints, and buying-advice commands with source IDs/permalinks, fetched-thread versus snippet-only evidence labels, anecdotal caveats, deleted/removed and prompt-injection-like evidence exclusion, command registry rows, docs, and tests without Reddit web scraping fallback, unauthenticated traffic, writes, search-history persistence, summary memory writes, content training, or live Reddit calls by default.
- Standalone Gmail/Telegram live validation remains deferred; config-only Gmail/Telegram doctors are complete and do not read inboxes/chats or send messages.
- Future safe overnight self-improvement runs still require explicit user approval, even though the 2026-05-23 bounded run completed.

## Superseded

- H9-WEATHER-BRIEFING is superseded by DAILY-BRIEFING-V2 for broader daily briefing behavior.
- C1-CLI-APPROVAL-UI and C2-DRY-RUN-PREFLIGHT are superseded for current planning purposes by APPROVAL-UI-FOUNDATION and ACTION-CENTER.
- WEB-ACQUISITION-LAYER is superseded by FREE-FIRST-WEB-ACQUISITION for the implemented acquisition core.

## Next Recommended Prompt

news-provider-registry-status-commands

Before running it:

1. Reconcile prompt tracker stale rows first if the user wants tracker hygiene before feature work.
2. Keep the news provider registry/status milestone metadata-only: no live provider calls, article fetching, paid API default, history storage, or bypass behavior.
3. Do not fetch articles, call providers, scrape paywalls/login/CAPTCHA-protected pages, or add browser automation.
4. Preserve no search/news history and no full article-body storage by default.
5. Preserve ToolBroker, PolicyEngine, ApprovalManager where needed, and AuditLogger gates for all future runtime news work.

## Imported Prompt Packs

| pack_id | imported_at | prompt_ids | status | notes |
|---|---|---|---|---|
| prompt-tracker-maturity-v1 | 2026-05-23 | PTM-01 through PTM-10 | complete | Imported, split, PTM-01 repaired, and PTM-02 through PTM-10 executed sequentially. Parser now preserves embedded delimiter examples; prompt bodies were verified as preserved exactly and no prompt pack was auto-executed. |
## Prompt Pack Import: Agent Runtime Orchestration

- imported_at: 2026-05-23T21:24:19+00:00
- pack_id: agent-runtime-orchestration-v1
- pack_title: Agent Runtime Orchestration Track
- mode: controlled_batch_until_blocked
- prompt_count: 10
- prompt_ids: ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-05, ORCH-06, ORCH-07, ORCH-08, ORCH-09, ORCH-10
- queue_position: top of docs/PROMPT_QUEUE.md
- execution: controlled batch requested by user; ORCH-01 through ORCH-10 are now completed with prompt files under `prompts/completed/` and release-gate evidence in `docs/COMPLETION_REPORT.md`.

## Recovery Note: Agent Runtime Orchestration

- recovery_at: 2026-05-23 14:59 PDT
- recovery_report: `docs/runtime/ORCH_BATCH_RECOVERY_REPORT.md`
- result: no partial ORCH prompt remained; ORCH-01 through ORCH-10 were already completed.
- tracking_fix: stale queued ORCH rows in `docs/PROMPT_LEDGER.md` were replaced with completed rows.
- safe_continuation: validation-only release-gate confirmation completed; `MACOS-MESSAGES-PROBE`, `MESSAGES-DRAFT-HANDOFF-WORKFLOW`, `INCOMING-MESSAGE-STRATEGY`, `MACOS-APPROVED-IMESSAGE-SEND`, `APPLE-MESSAGES-BUSINESS`, and `LEAD-RESPONSE-DRAFTING` are complete and `MESSAGING-DOGFOOD-SUITES` is next.
## Prompt Pack Import

- imported_at: 2026-05-23T22:05:13+00:00
- pack_id: agent-dna-cloneability-v1
- pack_title: Agent DNA, Clone Blueprint, and Build Provenance
- mode: controlled_batch_until_blocked
- prompt_count: 6
- prompt_ids: DNA-01, DNA-02, DNA-03, DNA-04, DNA-05, DNA-06
- execution: controlled batch by explicit user request; DNA-01 through DNA-06 are complete with docs/provenance evidence and no runtime behavior change.
- completed_prompt_files: `prompts/completed/DNA-01.md` through `prompts/completed/DNA-06.md`
- reconstructed_prompt_archive: `prompts/packs/reconstructed/`
- next_prompt_id: MESSAGING-DOGFOOD-SUITES

## Forum Intelligence Release Gate

- completed_at: 2026-05-25
- prompt_id: FORUM-INTELLIGENCE-RELEASE-GATE
- result: complete_verified
- validation: full suite 1034 passed, 2 skipped; focused docs/command/forum/prompt tests 30 passed; startup policy ok; capability manifest ok with 185 capabilities; command registry ok with 382 commands; fixture-backed `eval run --forums` passed 5 forum checks and skipped 5 personal-data checks by design; all five forum dogfood suites dry-ran ok.
- safety evidence: Reddit and V2EX were disabled/unconfigured locally, so no live provider content reads ran; Reddit retention/cache/privacy reports were count-only with zero entries; no-bypass/no-write scans found policy docs, denial tests, disabled/forbidden metadata, and no enabled scraping/login/cookie/session/CAPTCHA bypass or Reddit posting/commenting/voting/DM/moderation capability.
- next_prompt_id: none; recommended continuation is Release Hardening Loop v2 or an explicitly scoped safe live provider validation batch after provider configuration.
## Prompt Pack Import

- imported_at: 2026-05-25T09:50:27+00:00
- pack_id: native-skill-system-hardening-v1
- pack_title: Native Skill System Hardening Track
- mode: controlled_batch_until_blocked
- prompt_count: 10
- prompt_ids: SKILL-01, SKILL-02, SKILL-03, SKILL-04, SKILL-05, SKILL-06, SKILL-07, SKILL-08, SKILL-09, SKILL-10
- execution: import_only; no prompt executed automatically.
## Prompt Pack Import

- imported_at: 2026-05-25T15:32:48+00:00
- pack_id: brain-runtime-independence-v1
- pack_title: Brain Runtime Independence Track
- mode: controlled_batch_until_blocked
- prompt_count: 11
- prompt_ids: BRAIN-01, BRAIN-02, BRAIN-03, BRAIN-04, BRAIN-05, BRAIN-06, BRAIN-07, BRAIN-08, BRAIN-09, BRAIN-10, BRAIN-11
- execution: import_only; no prompt executed automatically.
## Brain Runtime Independence Batch Progress

- updated_at: 2026-05-25T17:45:00+00:00
- pack_id: brain-runtime-independence-v1
- completed_prompt_ids: BRAIN-01, BRAIN-02, BRAIN-03, BRAIN-04, BRAIN-05, BRAIN-06, BRAIN-07, BRAIN-08, BRAIN-09, BRAIN-10, BRAIN-11
- active_prompt_id: none
- next_prompt_id: news-provider-registry-status-commands
- evidence: BRAIN-01 docs/command/full-suite validation complete; BRAIN-02 provider-interface/registry/full-suite validation complete; BRAIN-03 LM Studio provider refactor/full-suite validation complete; BRAIN-04 llama.cpp server provider focused validation complete; BRAIN-05 Ollama provider focused validation complete; BRAIN-06 llama-cpp-python in-process provider validation complete; BRAIN-07 MLX provider strategy/stub validation complete; BRAIN-08 model health/benchmark/eval validation complete with full-suite evidence; BRAIN-09 provider fallback/router validation complete; BRAIN-10 MCP decision/adapter-stub validation complete; BRAIN-11 release gate complete with focused tests, command registry validation, policy-check, provider/MCP smokes, safe benchmark/eval smokes, optional import guard, release-gate docs, maturity review, and full suite 1285 passed / 1 skipped.
- stop_conditions_hit: none so far.
## Prompt Pack Import

- imported_at: 2026-05-25T17:28:14+00:00
- pack_id: hermes-inspired-safe-autonomy-v1
- pack_title: Hermes-Inspired Safe Autonomy Groundwork Track
- mode: controlled_batch_until_blocked
- prompt_count: 13
- prompt_ids: HERMES-01, HERMES-02, HERMES-03, HERMES-04, HERMES-05, HERMES-06, HERMES-07, HERMES-08, HERMES-09, HERMES-10, HERMES-11, HERMES-12, HERMES-13
- execution: import_only; no prompt executed automatically.

## Hermes-Inspired Safe Autonomy Batch Progress

- updated_at: 2026-05-25T18:24:00+00:00
- pack_id: hermes-inspired-safe-autonomy-v1
- completed_prompt_ids: HERMES-01, HERMES-02, HERMES-03, HERMES-04, HERMES-05, HERMES-06, HERMES-07, HERMES-08, HERMES-09, HERMES-10, HERMES-11, HERMES-12, HERMES-13
- active_prompt_id: none
- next_prompt_id: news-provider-registry-status-commands
- evidence: HERMES-01 architecture/docs tests and policy-check complete; HERMES-02 gateway/channel scaffold tests, CLI smokes, command validation, and policy-check complete; HERMES-03 Telegram/mobile status scaffold tests, CLI smokes, command validation, and policy-check complete; HERMES-04 repeated-task skill proposal tests passed with 8 focused and 41 combined focused tests, command registry ok with 453 commands, policy-check passed, and proposal CLI smokes used a temporary report path; HERMES-05 skill improvement proposal tests passed with 9 focused and 50 combined focused tests, command registry ok with 458 commands, and policy-check passed; HERMES-06 scheduler UX tests and existing scheduler policy tests passed with 21 focused tests, command registry ok with 464 commands, and policy-check passed; HERMES-07 subagent isolation tests passed with 9 focused tests, command registry ok with 468 commands, and policy-check passed; HERMES-08 sandbox abstraction tests passed with 10 focused tests and 23 combined tests, command registry ok with 471 commands, and policy-check passed; HERMES-09 model switching/session-continuity tests passed with 19 focused and command registry ok with 474 commands; HERMES-10 memory continuity tests passed with 20 focused and command registry ok with 478 commands; HERMES-11 authorized web boundary tests passed with 24 focused and command registry ok with 481 commands; HERMES-12 safe autonomy dogfood/eval tests passed with 32 focused, safe autonomy eval and dogfood dry-run passed, and command registry ok with 484 commands; HERMES-13 release gate passed with full suite 1380 passed/1 skipped, 74 focused tests, safe autonomy eval, dogfood dry-run, policy-check, command registry validation, and active_count 0 prompt audit.
- stop_conditions_hit: none so far.
## Prompt Pack Import

- imported_at: 2026-05-25T19:29:34+00:00
- pack_id: codebase-bug-review-and-hardening-v1
- pack_title: Full Codebase Bug Review and Hardening Track
- mode: controlled_batch_until_blocked
- prompt_count: 8
- prompt_ids: CODEBUG-01, CODEBUG-02, CODEBUG-03, CODEBUG-04, CODEBUG-05, CODEBUG-06, CODEBUG-07, CODEBUG-08
- execution: import_only; no prompt executed automatically.

## Codebase Bug Review and Hardening Batch Progress

- updated_at: 2026-05-25T20:45:00+00:00
- pack_id: codebase-bug-review-and-hardening-v1
- completed_prompt_ids: CODEBUG-01, CODEBUG-02, CODEBUG-03, CODEBUG-04, CODEBUG-05, CODEBUG-06, CODEBUG-07, CODEBUG-08
- active_prompt_id: none
- next_prompt_id: clean-release-candidate-boundary-and-prompt-tracker-reconciliation
- evidence: CODEBUG-01 baseline docs and validation complete; CODEBUG-02 safety-control tests passed with 61 focused tests; CODEBUG-03 fixed closed-pipe `commands list` traceback and command registry tests passed; CODEBUG-04 runtime/brain tests passed with 148 focused tests plus full suite; CODEBUG-05 connector/workflow tests passed with 440 focused tests; CODEBUG-06 prompt/tracker/docs tests passed with 66 focused tests and CODEBUG queue rows reconciled; CODEBUG-07 static scan/report completed with no scoped immediate code fix; CODEBUG-08 release gate passed with full suite 1387 passed / 1 skipped, docs-focused tests 43 passed, command registry validation with 484 commands, policy-check, safe eval 40 pass / 0 fail / 6 skipped, and all_safe dogfood dry-run.
- stop_conditions_hit: none.
- remaining_follow_up: clean release-candidate boundary, broader prompt tracker reconciliation, dedicated docs validation command gap, and subprocess/file-deletion allowlist review.
## Prompt Pack Import

- imported_at: 2026-05-25T19:52:09+00:00
- pack_id: natural-language-command-understanding-v1
- pack_title: Natural Language Command Understanding Track
- mode: controlled_batch_until_blocked
- prompt_count: 10
- prompt_ids: NLCMD-01, NLCMD-02, NLCMD-03, NLCMD-04, NLCMD-05, NLCMD-06, NLCMD-07, NLCMD-08, NLCMD-09, NLCMD-10
- execution: import_only; no prompt executed automatically.
## Prompt Pack Import

- imported_at: 2026-05-25T20:51:30+00:00
- pack_id: command-qa-sandbox-self-heal-v1
- pack_title: Command QA Sandbox and Self-Healing Loop
- mode: controlled_batch_until_blocked
- prompt_count: 10
- prompt_ids: QA-01, QA-02, QA-03, QA-04, QA-05, QA-06, QA-07, QA-08, QA-09, QA-10
- execution: import_only; no prompt executed automatically.
## Prompt Pack Import

- imported_at: 2026-05-25T22:15:16+00:00
- pack_id: creative-media-generation-v1
- pack_title: Creative Media Generation Track
- mode: controlled_batch_until_blocked
- prompt_count: 12
- prompt_ids: MEDIA-01, MEDIA-02, MEDIA-03, MEDIA-04, MEDIA-05, MEDIA-06, MEDIA-07, MEDIA-08, MEDIA-09, MEDIA-10, MEDIA-11, MEDIA-12
- execution: import_only; no prompt executed automatically.
## Prompt Pack Import

- imported_at: 2026-05-26T00:00:44+00:00
- pack_id: secrets-and-api-key-management-v1
- pack_title: Secrets and API Key Management Track
- mode: controlled_batch_until_blocked
- prompt_count: 8
- prompt_ids: SECRETS-01, SECRETS-02, SECRETS-03, SECRETS-04, SECRETS-05, SECRETS-06, SECRETS-07, SECRETS-08
- execution: import_only; no prompt executed automatically.

## Secrets and API Key Management Batch Progress

- updated_at: 2026-05-26T01:10:00+00:00
- pack_id: secrets-and-api-key-management-v1
- completed_prompt_ids: SECRETS-01, SECRETS-02, SECRETS-03, SECRETS-04, SECRETS-05, SECRETS-06, SECRETS-07, SECRETS-08
- active_prompt_id: none
- next_prompt_id: news-provider-registry-status-commands
- evidence: SECRETS-01 policy/docs tests passed; SECRETS-02 registry/redaction tests and command validation passed; SECRETS-03 resolver/env-loader tests and command validation passed; SECRETS-04 provider doctor tests, command validation, policy-check, and full suite 1602 passed after scoped fixes; SECRETS-05 Keychain dry-run/status tests and smokes passed; SECRETS-06 scanner/preflight tests plus tracked/staged scan/preflight smokes passed; SECRETS-07 docs/scanner tests and provider-doctor smoke passed; SECRETS-08 release gate passed with full suite 1616 tests, `tests/secrets` 31 tests, command registry 541 commands, policy-check, tracked/staged scans, and Git preflight.
- stop_conditions_hit: none.
- remaining_follow_up: clean release-candidate boundary review before commit/push, external scanner parity if desired, real Keychain adapter only under a future explicit approval-gated prompt, and live provider credential validation only if configured and explicitly requested.
## Prompt Pack Import

- imported_at: 2026-05-26T00:56:39+00:00
- pack_id: performance-bottleneck-scanner-v1
- pack_title: Performance Bottleneck Scanner and Optimization Advisor
- mode: controlled_batch_until_blocked
- prompt_count: 11
- prompt_ids: PERF-01, PERF-02, PERF-03, PERF-04, PERF-05, PERF-06, PERF-07, PERF-08, PERF-09, PERF-10, PERF-11
- execution: controlled batch by explicit user request. PERF-01 through PERF-11 complete with evidence.
- evidence: PERF-01 docs tests passed; PERF-02 model/report tests passed; PERF-03 static scanner tests passed; PERF-04 startup scanner tests passed; PERF-05 safe benchmark tests passed; PERF-06 test profiler tests and full suite passed; PERF-07 recommendation tests passed; PERF-08 baseline tests passed; PERF-09 patch planner tests passed; PERF-10 dashboard tests and read-only CLI smokes passed; PERF-11 release gate passed with full suite 1665, focused performance tests 49, command registry validation 561, policy-check, safe static/startup/benchmark/test-profile/recommendation/baseline/dashboard smokes, release docs, and maturity review.
- stop_conditions_hit: none.
- remaining_follow_up: clean release-candidate boundary review before commit/push; manual/live validation; human review of static findings before any optimization patch.
## Prompt Pack Import

- imported_at: 2026-05-26T04:45:51+00:00
- pack_id: canonical-runtime-gateway-hardening-v1
- pack_title: Canonical Runtime State, Agent Gateway / Runtime Kernel, and External Review Hardening
- mode: controlled_batch_until_blocked
- prompt_count: 11
- prompt_ids: CANON-01, CANON-02, CANON-03, CANON-04, CANON-05, CANON-06, CANON-07, CANON-08, CANON-09, EXTREV-01, CANON-10
- execution: import_only; no prompt executed automatically.

## Prompt Batch Progress

- updated_at: 2026-05-26T06:35:00+00:00
- pack_id: canonical-runtime-gateway-hardening-v1
- completed_verified: CANON-01, CANON-02, CANON-03, CANON-04, CANON-05, CANON-06, CANON-07, CANON-08, CANON-09, EXTREV-01, CANON-10
- active_prompt_id: none
- next_prompt_id: news-provider-registry-status-commands
- queued_remaining: none for this pack
- evidence: completion report entries, completed prompt files, full suite 1723 passed, focused release-gate tests 58 passed, command registry validation, policy-check, prompt audit, and all_safe dogfood dry-run evidence.
- blockers: none for CANON-10. Repo-level blockers remain: large dirty worktree, clean release-candidate boundary review, external secret scan gap, and live/manual validation gaps.
## Prompt Pack Import

- imported_at: 2026-05-26T07:54:41+00:00
- pack_id: daydream-lab-idle-research-v1
- pack_title: Daydream Lab — Idle Research, Curiosity Engine, and Prompt-Pack Incubator
- mode: controlled_batch_until_blocked
- prompt_count: 24
- prompt_ids: DAYDREAM-01, DAYDREAM-02, DAYDREAM-03, DAYDREAM-04, DAYDREAM-05, DAYDREAM-06, DAYDREAM-07, DAYDREAM-08, DAYDREAM-09, DAYDREAM-10, DAYDREAM-11, DAYDREAM-12, DAYDREAM-13, DAYDREAM-14, DAYDREAM-15, DAYDREAM-16, DAYDREAM-17, DAYDREAM-18, DAYDREAM-19, DAYDREAM-20, DAYDREAM-21, DAYDREAM-22, DAYDREAM-23, DAYDREAM-24
- execution: import_only; no prompt executed automatically.
