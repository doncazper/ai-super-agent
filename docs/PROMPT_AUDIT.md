# Prompt Audit

This audit is a best-effort reconstruction from repo evidence. It should be updated after major prompt batches and before long autonomous runs.

Completion evidence classifications: `complete_verified`, `likely_complete`, `partial`, `no_evidence`, `failed`, `blocked`, `superseded`, and `stale`.

## Audit Summary

| category | count | notes |
|---|---:|---|
| definitely completed | 181 | Inferred from implemented files, tests, docs, feature registry, maturity tracker, changelog, completion report, prompt tracker release-gate docs, prompt completion evidence, and `./.venv/bin/python smart_agent.py prompts audit`. |
| likely completed | 0 | No separate likely bucket is currently needed; uncertain items are left queued or blocked. |
| queued but not confirmed | 3 | Queue still points at `news-provider-registry-status-commands` after the Native Skill System Hardening batch; native-skill-specific follow-up should be a reviewed lockfile/pinning workflow or clean release-candidate boundary prompt before external skill import/runtime work. |
| blocked by approval gates | 0 | No queued prompt is currently blocked in prompt tracking. |
| superseded by later work | 1 | Superseded rows remain documented below where older tracking concepts were replaced by mature features. |

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

- news-capability-manifest-provider-policy
- PLATFORM-CAPABILITY-MANIFEST-MAPPING
- PLATFORM-STARTUP-LAZYLOAD-GUARDRAILS

## Blocked By Approval Gates

- none.

## Missing Evidence

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

news-capability-manifest-provider-policy

Before running it:

1. Declare disabled/planned `news.*` capability manifest entries before runtime implementation.
2. Keep paid providers disabled by default and require explicit config/approval gates.
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
