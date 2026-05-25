# Feature Roadmap

This roadmap is the execution queue for post-baseline work. It prioritizes safety, documentation, tests, and release gates before capability breadth.

Every roadmap status change must update:

- `docs/PROJECT_STATE.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/COMPLETION_REPORT.md`
- `CHANGELOG.md` when user-visible behavior changes

## Current Batch

Release Hardening Loop v2 is complete locally with YELLOW release readiness: tests, startup policy, capability manifest, command registry, safe eval, dogfood dry-run, quality bug review, release docs, and tracker reconciliation are complete, while a clean release candidate boundary and live/manual validation remain next. News Intelligence roadmap and source policy are now specified as a docs-only track for current headlines, topic search, timelines, source comparison, multilingual summaries, freshness controls, citations, and dogfood/eval coverage; no runtime news commands, provider calls, paid API defaults, browser automation, search/news history storage, full article-body storage, or paywall/login/CAPTCHA bypass were added. Cross-Platform Core + Platform Bridge architecture, Platform Capability Registry v1, Platform bridge base interfaces, platform-aware config/paths/detection scaffolding, read-only platform doctor/capability commands, macOS/iOS/Windows/web bridge stubs, the App Bridge API contract, and the current cross-platform release gate/future build guides are now complete locally for the current groundwork: the Python core remains platform-neutral, platform bridges are optional/lazy future adapters, platform-specific imports are forbidden at core startup, planned/stubbed platform capabilities remain disabled and non-executable, `NullPlatformBridge` fails closed for unavailable platforms, direct `execute_action()` calls are blocked, platform detection/config/path helpers perform no native imports or personal file scans, platform inspection commands route through SAFE ToolBroker/PolicyEngine/AuditLogger metadata tools, bridge stubs return only blocked or requires_setup/unavailable results without side effects, and the App Bridge contract is disabled by default, localhost/IPC-only, no-server-startup, pairing-gated, audit-correlated, and ApprovalManager-preserving. All future bridge actions must still route through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger. Manifest mapping and dedicated startup/lazy-load guardrails remain planned follow-up prompts and must land before real platform behavior. The generated artifact hygiene continuation adds narrow ignore rules and `docs/release/GENERATED_ARTIFACT_HYGIENE.md` so local eval/lead/messaging/iOS-compose/Reddit-export artifacts are separated from reviewable source changes, but it does not replace human release-boundary review. Tracker Hygiene, Indexing, and Compaction is complete as docs-only navigation/maintenance work and adds `docs/TRACKER_DASHBOARD.md`, `docs/TRACKER_INDEX.md`, `docs/TRACKER_MAINTENANCE.md`, `docs/TRACKER_ARCHIVE_POLICY.md`, and `docs/TRACKER_CONSISTENCY_REPORT.md` without runtime behavior changes. Prompt Tracker Maturity track is complete locally. Agent DNA / Cloneability is complete as docs/provenance work with validation and no runtime behavior change. `FREE-FIRST-WEB-ACQUISITION`, `SERPAPI-FALLBACK`, `WEATHER-PROVIDER-SELECTOR`, and `GMAIL-TELEGRAM-DOCTORS` were completed out of queue order by explicit user request. The Internet Access Graduation Track now resets future web work into a clean SDLC-compliant sequence for provider registry, SearXNG/Brave hardening, fetch/extraction hardening, source grounding, citation, cache/index, official APIs, dogfood/evals, and a final release gate. `APPLE-MESSAGING-ROADMAP` and `apple-messaging-roadmap-track` are complete as planning-only Apple Ecosystem + Lead Response / Messaging roadmap work. `MESSAGE-CHANNEL-ABSTRACTION`, `MESSAGE-SAFETY-ACTION-CENTER`, `LEAD-INBOX-ABSTRACTION`, and `MACOS-APPROVED-IMESSAGE-SEND` are complete as local foundations; the macOS send adapter remains disabled by default and requires live probe, allowlist, exact Action Center approval, and rate-limit gates.

## Cross-Platform Core + Platform Bridge Track

This track prepares the agent for macOS, iOS companion, Windows, and future app frontends without rewriting the Python core, coupling the core to one OS, or adding startup overhead. It must preserve CLI-only operation, ToolBroker-only execution, PolicyEngine gates, PermissionManager checks, ApprovalManager rules, AuditLogger evidence, conservative feature maturity, and disabled-by-default personal-data behavior.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Cross-platform architecture and roadmap | complete | Agent DNA / Cloneability and Runtime Orchestration | Documentation-only ADR, strategy, capability matrix, boundaries, performance policy, implementation guide, planned command tracking, and tracker updates; no runtime platform behavior |
| 2 | Platform capability registry | complete | Cross-platform architecture and roadmap | Data-driven registry only; no native imports, personal-data access, or action execution; 27 static planned/stubbed records tested |
| 3 | Platform bridge base interfaces | complete | Platform capability registry | Abstract interfaces, action payload/result envelopes, NullPlatformBridge, lazy registry, direct-execution guard, and tests; no real platform behavior |
| 4 | Platform-aware config, paths, and detection | complete | Bridge base interfaces | Safe detection/config/path helpers only; no personal file scans, directory creation, platform actions, or native framework imports |
| 5 | Platform doctor and capability commands | complete | Platform config/detection | Brokered read-only metadata commands; no permissions, personal data, native imports, app bridge server startup, or bridge actions |
| 6 | macOS/iOS/Windows bridge stubs | complete | Platform doctor/capability commands | Lazy stubs only; return blocked or requires_setup/unavailable for real actions; no native imports, personal-data reads, side effects, or app bridge server startup |
| 7 | App Bridge API contract | complete | Bridge stubs | Contract docs, payload schemas/models, validation tests, disabled defaults, localhost/IPC-only, no server startup, no remote access, no approval bypass |
| 8 | Platform capability manifest and ToolBroker mapping | planned | App Bridge API contract | Disabled placeholders, manifest validation, ToolBroker-only execution safeguards |
| 9 | Startup overhead and lazy-load guardrails | planned | Manifest mapping | Import-graph and startup side-effect tests; no native/heavy modules at core startup |
| 10 | Cross-platform release gate and future build guide | complete | Startup overhead guardrails planned; user requested current-groundwork gate now | Current groundwork release gate, maturity review, and future macOS/iOS/Windows/app frontend build guides complete. Manifest mapping and dedicated startup guardrails remain planned before real platform behavior |

## News Intelligence Track

This track turns current/live public news work into a dedicated source-grounded module. It must remain free-first, cache-first, provider-policy-gated, citation-backed, freshness-aware, no-history-by-default, and no-bypass by default. All news/article/feed/sitemap/provider content is `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`, and current facts require source data.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | News Intelligence roadmap and source policy | complete | Internet Access Graduation Track and source-grounded research foundations | Documentation, source policy, provider strategy, freshness policy, source grounding, retention policy, decision record, planned command tracking, and tracker updates only; no runtime news commands or provider calls |
| 2 | News capability manifest entries and provider policy | complete | News Intelligence roadmap and source policy | Disabled/planned `news.*` capabilities, safe `NEWS_*` config defaults, provider policy selection/skipping, memory behavior, audit fields, no paid-provider defaults, and tests complete; no live provider calls or article fetching |
| 3 | News provider registry and status commands | planned | Capability manifest/provider policy | Metadata/status only; no provider calls; missing providers return setup hints |
| 4 | News cache and retention scaffolding | planned | Provider registry | Public-news metadata cache only; no search/news history or full article bodies by default |
| 5 | RSS/Atom and news sitemap headline acquisition | planned | Cache/retention scaffolding and existing web feed/sitemap support | Bounded headline/feed/sitemap discovery; no article-body fetch unless selected later |
| 6 | GDELT provider | planned | Provider registry and capability policy | Free public provider path with normalized results, rate limits, audit, and no history storage |
| 7 | Optional Media Cloud and NewsAPI providers | planned | GDELT provider and provider policy | Optional/configured/fallback only; paid/quota use gated by config/approval policy |
| 8 | News top/search/topic/source commands | planned | Provider registry and source grounding | Source-backed current headline/topic/source workflows with freshness and failure reporting |
| 9 | News brief/timeline/compare commands | planned | Top/search/topic/source commands | No fabricated citations/dates; separate facts from inference and report conflicts |
| 10 | Multilingual news summaries | planned | News source grounding and language layer | Generated translation labels, original source IDs, and sparse-data caveats |
| 11 | News dogfood/eval suite and release gate | planned | Runtime news workflows | Mock-first evals, no paid defaults, no bypass behavior, no fabricated citations, command registry and maturity review |

## Agent DNA / Cloneability Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | DNA-01 - Agent DNA foundation | complete | DNA pack import | Agent DNA and architecture principles created; no runtime behavior changed |
| 2 | DNA-02 - Clone blueprint and migration guide | complete | DNA-01 complete | Clone blueprint, model migration, platform migration, and rewrite checklist created |
| 3 | DNA-03 - Build history and provenance | complete | DNA-02 complete | Build history, provenance hierarchy, and decision index created |
| 4 | DNA-04 - Reconstructed prompt pack archive | complete | DNA-03 complete | Reconstructed pack archive created with exact-original caveats and confidence labels |
| 5 | DNA-05 - SPEC / SDLC / AGENTS alignment | complete | DNA-04 complete | README, SPEC, SDLC, and AGENTS aligned with cloneability rules |
| 6 | DNA-06 - Cloneability release gate | complete | DNA-05 complete | Cloneability release-gate and maturity review written; validation added |

## Prompt Tracker Maturity Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | PTM-01 - Prompt tracker state audit | complete | Prompt Tracker Maturity pack import | Repaired audit/gap docs and marked complete with evidence |
| 2 | PTM-02 - Prompt ledger / queue / audit schema hardening | complete | PTM-01 complete | Schema/templates/status rules hardened |
| 3 | PTM-03 - Prompt pack import and splitting | complete | PTM-02 complete | Import parser preserves embedded delimiter examples |
| 4 | PTM-04 - Prompt status CLI | complete | PTM-03 complete | Search/evidence/recovery status commands added |
| 5 | PTM-05 - Completion evidence auditor | complete | PTM-04 complete | Evidence classifier implemented without executing queued prompts |
| 6 | PTM-06 - PROJECT_STATE / FEATURE_MATURITY integration | complete | PTM-05 complete | Prompt state and maturity fields updated |
| 7 | PTM-07 - PromptOps Workbench | complete | PTM-06 complete | Runner remains disabled; autopilot safety gates retained |
| 8 | PTM-08 - Prompt tracker dogfood and QA suite | complete | PTM-07 complete | Prompt tracker dogfood suites and eval added |
| 9 | PTM-09 - Missed and superseded prompt recovery | complete | PTM-08 complete | Conservative recovery plan added; no auto-run |
| 10 | PTM-10 - Prompt tracker release gate | complete | PTM-09 complete | Release gate and maturity review artifacts added |

## Agent Runtime Orchestration Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | ORCH-01 - Runtime orchestration architecture | complete | Prompt pack import | Architecture and runtime docs created; no runtime behavior added beyond planning |
| 2 | ORCH-02 - Runtime models and state | complete | ORCH-01 complete | Lightweight dataclasses and state tests pass |
| 3 | ORCH-03 - Service registry and feature flags | complete | ORCH-02 complete | Lazy service registry and disabled risky defaults tested |
| 4 | ORCH-04 - Runtime kernel and lifecycle | complete | ORCH-03 complete | Kernel status/health is metadata-only and avoids LM Studio/tool/personal-data calls |
| 5 | ORCH-05 - Runtime event bus and state events | complete | ORCH-04 complete | In-process redacted event bus; untrusted policy/approval control denied |
| 6 | ORCH-06 - Workflow runner and job queue | complete | ORCH-05 complete | Metadata jobs only; HIGH approval-required and CRITICAL blocked |
| 7 | ORCH-07 - Scheduler policy | complete | ORCH-06 complete | Manual-run only; no background persistence and no CRITICAL automatic runs |
| 8 | ORCH-08 - Runtime CLI commands | complete | ORCH-07 complete | `runtime`, `jobs`, `workflows`, and `events` commands added and tested |
| 9 | ORCH-09 - Frontend bridge contract | complete | ORCH-08 complete | Contract only; no server/app bridge; approvals/tools/policy changes blocked |
| 10 | ORCH-10 - Runtime orchestration release gate | complete | ORCH-09 complete | Full tests, safe eval, startup policy, manifest validation, command registry validation, prompt pack validation, native skill validation, runtime smoke, prompt audit, and 2026-05-23 ORCH recovery validation passed |

## Completed Tracking and Connector Foundation Batch

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
| 11 | Live Session Logging and Replay | complete | Command Registry + Manual QA System | Redacted session capture/replay complete; raw reports ignored by git; manual dogfood QA pending |

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
| 2 | Unified Action Center | complete | Live validation harness scoped | Review/approval queue complete; actions do not execute directly, future execution must still go through ToolBroker, and export/audit payloads minimize sensitive bodies/drafts |
| 3 | Calendar approved writes | complete | Action Center and per-action approval UX | CRITICAL per-action write drafts, exact preview, rollback notes, brokered stub execution with Action Center action-id verification; live native writes deferred |
| 4 | Reminders/tasks connector | complete | Connector decision notes and Action Center | Adapter/mock v1, selected-scope list approval, brokered Action Center task drafts, CRITICAL per-action writes; native provider deferred |
| 5 | Contacts approved edits | complete | Contacts read-only validated and Action Center ready | CRITICAL per-action draft/update/create stubs; field-level previews; direct broker writes without verified Action Center action ids rejected; live native provider and delete deferred |
| 6 | Email approved send | complete | Email draft-only live validation and Action Center ready | CRITICAL per-action Action Center send drafts, low-level sends require verified Action Center action ids, no bulk send, mock provider only; real provider deferred |
| 7 | Messages safe handoff / send decision | complete | Safe implementation decision record | Save/copy handoff only; low-level tools require verified Action Center action ids; automatic send remains deferred |
| 8 | Browser selected-tab / clipping connector | complete | Connector decision record and untrusted-content review | Explicit URL read/summarize/clip workflow complete; selected-tab native integration remains stubbed, disabled, and no history/cookie/profile access is added |
| 9 | Notes / knowledge capture | complete | Memory v2 and file policy review | Workspace-only capture inbox complete; no Apple Notes/private DB scraping; file captures are untrusted by default with explicit `--trusted-user` opt-in; memory promotion goes through Memory v2 policy |
| 10 | Daily briefing v2 | complete | Live validation for v1 sources | Configurable opt-in sections complete; personal sections approval-gated; no hidden personal access or writes |
| 11 | Meeting follow-up workflow | complete | Meeting prep v1 and Action Center | Draft-only follow-up complete; suggested writes/sends become Action Center records only |
| 12 | Personal task extraction | complete | Email/messages/calendar selected-scope review | Extraction complete; task writes remain Action Center drafts only |
| 13 | Controlled self-improvement implementation loop | complete | Action Center, release gate, branch workflow | Branch-based implementation complete; cannot weaken policy, disable audit, grant permissions, or commit without approval |
| 14 | Scheduler / automation v1 | complete | Automation threat model and approval rules | Manual-run only; no background persistence; scheduled tool workflows still use ToolBroker; optional redacted `backup_create`; CRITICAL actions never execute automatically |
| 15 | Full feature maturity review | complete | Previous batch complete | Full tests, startup policy, capability manifest, safe eval, command registry validation, ToolBroker/default/approval scans, and docs sync passed |
| 16 | Native Skills Program foundation | complete | Prompt ledger/queue complete | Governance docs, intake criteria, candidate registry, and risk model created; no external skills installed or run |

## Native Skills Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Native Skills Program foundation | complete | Full feature maturity review | Docs/intake foundation only; no external skills installed or run |
| 2 | Skill marketplace survey | complete | Native Skills Program foundation | Research-only survey, matrix, and shortlist complete; no external skills installed or run |
| 3 | Native skill vetter | complete | Skill marketplace survey | Static workspace-only vetter complete; no external code execution, dependency install, or skill enablement |
| 4 | Native skill manifest and loader | complete | Native skill vetter | Metadata-only discovery complete; manifests cannot grant permissions, execute code, or auto-enable tools |
| 5 | Skill finder native skill | complete | Native skill manifest | Local-only finder complete; external marketplace search remains out of scope |
| 6 | PDF workspace native skill | complete | Native skill manifest | Read-only workspace PDF skill complete; OCR/split/merge/writes deferred |
| 7 | Skill roots, scopes, and precedence | complete | Native skill manifest | Metadata-only roots and deterministic shadowing diagnostics complete; no external skill execution or trusted override by unreviewed roots |
| 8 | Skill manifest schema and dependency gating hardening | complete | Skill roots, scopes, and precedence | Strict schema and detection-only dependency checks complete; no package installs, script execution, provider calls, connector calls, or permission grants |
| 9 | Skill provenance, trust metadata, and lockfile | complete | Skill manifest schema and dependency gating hardening | Metadata-only provenance/trust/lockfile diagnostics complete; no auto-update, install, marketplace call, or lockfile write command |
| 10 | Skill inspection and vetting CLI hardening | complete | Skill provenance, trust metadata, and lockfile | Static approved-path inspection, vetting, scoring, and latest report lookup complete; no external scripts, binaries, package installs, network access, plugin runtime, or skill enablement |
| 11 | Per-profile skill allowlists | complete | Skill inspection and vetting CLI hardening | Advisory profile visibility rules complete for default/research/coding/personal_assistant/lead_response/locked_down/experimental; profiles do not enable skills or bypass policy |
| 12 | Skill compatibility matrix | complete | Per-profile skill allowlists | Metadata-only compatibility matrix complete across manifest-derived platform/runtime/setup records; no skill execution, native platform imports, provider calls, dependency installs, or platform behavior enablement |
| 13 | Skill conflict detector | complete | Skill compatibility matrix | Metadata-only conflict detector complete; no skill execution, auto-resolution, dependency install, provider call, plugin runtime, or policy change |
| 14 | Skill test and dogfood harness | complete | Skill conflict detector | Metadata-only safe harness, eval cases, and dogfood suites complete; no external skill execution |
| 15 | Skill docs generator | complete | Skill test and dogfood harness | Metadata-only docs generator and catalog complete; dry-run default, manual notes preserved, missing docs reported, no external skill execution |
| 16 | Native skill system release gate | complete | Skill docs generator | Local metadata-only release gate passed; reviewed real lockfile/pinning workflow and manual external-skill intake validation remain future work |

## Next Product Feature Track

This track is the next product-facing feature set to keep synchronized before implementation work resumes. Completed rows are already present in the repo and remain subject to future live validation or provider-specific decision records.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Golden eval suite + quality scorecards | complete | Current release-gate sync passed | Data-backed safe evals and scorecards added; personal-data evals skipped unless explicitly approved; live LM Studio remains opt-in |
| 2 | Unified Action Center v1 | complete | Approval UI and dry-run foundation | Action Center is review-only, does not execute actions directly, and minimizes sensitive export/audit payloads |
| 3 | Tasks / Reminders connector v1 | complete | Action Center and task connector decision notes | Provider access disabled by default; reads HIGH approval; brokered draft-create queues Action Center only; writes CRITICAL per-action; native provider deferred |
| 4 | Calendar approved writes v1 | complete | Action Center and calendar read-only | Disabled by default; CRITICAL per-action; direct broker writes without verified Action Center actions are rejected; live native writes deferred |
| 5 | Contacts approved edits v1 | complete | Action Center and contacts read-only | Disabled by default; CRITICAL per-action; low-level writes require verified Action Center action ids; live native edits deferred |
| 6 | Email approved send v1 | complete | Action Center and email draft-only | Disabled by default; CRITICAL per-action; low-level sends require verified Action Center action ids; mock provider only |
| 7 | Messages safe handoff v1 | complete | Messages draft-only and send decision record | No automatic send; save/copy handoff only with verified Action Center action ids |
| 8 | Browser selected-tab / clipping v1 | complete | Web fetch and workspace file policy | Explicit URL workflow complete; selected-tab native integration remains stubbed |
| 9 | Notes / knowledge capture v1 | complete | Workspace file policy and Memory v2 | Workspace-only capture; explicit trusted-user file marker added; Apple Notes integration deferred |
| 10 | Privacy Center / data inventory v1 | complete | Dashboard, connector registry, audit/memory metadata | Metadata/status only; no personal connector reads; redacted export; memory deletion requires confirmation and uses brokered `memory.clear` |
| 11 | Backup / restore / migration v1 | complete | Workspace file policy and audit review | Brokered redacted archive create/list/inspect/verify/export plus approval-gated restore with integrity and policy-weakening checks |
| 12 | Model-router benchmark and prompt quality evals | complete | Eval harness and model diagnostics | Fixture-backed benchmark complete; live LM Studio answer-quality smoke remains opt-in and no provider secrets are logged |
| 13 | Scheduler / automation v1 | complete | Automation threat model and approval rules | Manual-run only; no hidden persistence; optional redacted `backup_create`; CRITICAL actions never automatic |
| 14 | Controlled self-improvement implementation loop | complete | Action Center, release gate, branch workflow | Approved proposal required; brokered test/diff checkpoint can queue commit action; commit approval-gated |
| 15 | Overnight self-improvement runbook | complete | Scheduler v1 and self-improvement loop | Safe-mode runbook, report template, `improve overnight-plan`, and one approved bounded docs/tests/tracking run complete; no background autonomy granted |
| 16 | Full release gate + maturity review | complete | This product feature track | Full tests, startup policy, manifest validation, safe eval, command registry/native skill validation, ToolBroker/default/approval scans, and docs sync passed on 2026-05-23 |
| 17 | Cost-aware provider policy | complete | Connector framework, web/weather provider docs | Free-first provider selection policy, config defaults, decision record, connector docs, audit/redaction tests; no new provider API calls added |
| 18 | Secret/config doctor | complete | Cost-aware provider policy | Redacted config-only doctor for SerpAPI, WeatherAPI, Gmail, and Telegram; focused `gmail doctor/scopes` and `telegram doctor/status` commands warn on broad scopes, repo-local token paths, and missing chat allowlists/defaults; no API calls, inbox/chat reads, sends, or paid-provider default promotion |
| 19 | Free-first Web Acquisition Layer v1 | complete | Cost-aware provider policy and secret/config doctor | Brokered cache/robots/sitemap/RSS/direct URL acquisition commands complete; paid providers skipped by default; CAPTCHA/anti-bot/login bypass remains forbidden |
| 20 | Optional SerpAPI fallback provider | complete | Free-first Web Acquisition Layer v1 | Brokered `web.search.serpapi`, `web search --provider serpapi`, `research --provider serpapi`, and config-only `web serpapi doctor` complete with mocked tests; requires `SERPAPI_API_KEY`, `SERPAPI_ENABLED=true`, `ALLOW_PAID_APIS=true`, and `MAX_PAID_API_CALLS_PER_DAY>0`; not default under `free_first` |
| 21 | Cost-aware weather provider selector | complete | Cost-aware provider policy and weather connector | Auto mode selects Open-Meteo for current/forecast, NOAA/NWS for U.S. alerts, and WeatherAPI only when configured and explicitly selected or paid-provider allowed; provider decisions are audited and keys redacted |

## Internet Access Graduation Track

This track supersedes ad hoc web-provider ordering for future work. Completed rows remain current repo evidence, but the broader goal is a mature web acquisition and source-grounded research system with no paid defaults, no bypass behavior, no browser profile access, and no query/content memory storage by default.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Cost-aware provider policy | complete | Connector framework | Defaults remain `free_first`, `ALLOW_PAID_APIS=false`, `MAX_PAID_API_CALLS_PER_DAY=0`, `SEARCH_STORE_HISTORY=false`; brokered `web providers`, `web provider-policy`, and `web provider-decision` expose deterministic selection without provider calls |
| 2 | Web Acquisition Layer core | complete for local v1 | Cost-aware provider policy | Central `agent.web_acquisition` request/source/provider planning package exists; cache/feed/sitemap/direct URL paths are brokered, `web source-status` provides no-fetch URL inspection, and paid providers are skipped by default |
| 3 | Robots/sitemap/feed support | complete for local v1 | Web Acquisition Layer core | Core parser modules, brokered commands, alias capabilities, 500 sitemap URL / 50 feed item defaults, blocklist/timeout/malformed-input tests, and docs are in place; blocked/CAPTCHA/login/anti-bot pages return unavailable, not bypass attempts |
| 4 | Search provider registry | complete for local v1 | Internet Access release gate and roadmap reset | Metadata-only registry, provider interface, normalized search schemas/errors, brokered `web search-providers`, and explicit provider setup hints are in place; no new live provider implementation added |
| 5 | SearXNG provider | complete for local v1 | Search provider registry | Configured self-hosted base URL only, disabled by default, JSON results normalized, setup/doctor command added, mocked error/rate-limit/audit tests pass; no public instance default and live instance validation remains opt-in |
| 6 | Brave provider hardening | complete for local v1 | Search provider registry | Optional quota-limited provider requires `BRAVE_SEARCH_API_KEY`, `BRAVE_SEARCH_ENABLED=true`, and paid/quota policy opt-in; mocked normalization/error/rate-limit/audit tests pass; live key validation remains opt-in |
| 7 | SerpAPI optional fallback | complete for explicit fallback | Cost-aware provider policy | Requires `SERPAPI_API_KEY`, `SERPAPI_ENABLED=true`, explicit provider selection, paid-API allowance, and a nonzero daily paid-call cap; `web serpapi doctor` is config-only; never default under `free_first` |
| 8 | Safe fetch/extraction hardening | complete for local v1 | Acquisition core and provider registry | Brokered `web fetch`, `web extract`, and `web metadata` selected-URL workflows now validate URL/scheme/domain, strip tracking parameters, enforce timeout/redirect/content-type/size bounds, sanitize scripts/event handlers, extract readable text and metadata, wrap prompt-injection text as untrusted data, audit domains/result status, and return blocked/CAPTCHA pages as unavailable without bypass |
| 9 | Source-grounded research workflow | complete for local v1 | Safe fetch/extraction hardening | Brokered research command supports `--provider`, `--max-sources`, `--freshness`, and `--no-fetch`; reports source sections, snippet-only/fetch-failed evidence, conflict/coverage limitations, retrieved timestamps, provider policy, and no fabricated citations |
| 10 | Router: internet only when needed | complete for local v1 | Source-grounded workflow | Deterministic router emits `needs_internet`, reason, sources, provider policy, tools, risk hint, and clarification fields; no-tools disables internet; prompt-injection-like text cannot force web routing; stable/local prompts stay clean |
| 11 | Citation/source attribution | complete for local v1 | Source-grounded workflow | Stable source IDs, metadata-only source bundles, citation spans, claim attribution, failed-source separation, and `research sources/export-sources/verify-sources --last` are in place with local tests; live source validation remains opt-in |
| 12 | Cache/dedupe/local lightweight index | complete for local v1 | Source grounding and provider strategy | TTL-bounded public web cache, content-hash/URL dedupe, local metadata index, brokered cache/index commands, no raw query history, no personal/authenticated content, and no full content storage by default |
| 13 | Official API connector framework | complete for local framework/stub v1 | Provider registry | Provider interfaces, registry/domain matching, GitHub/Wikipedia/arXiv/Reddit stubs, brokered official API commands, mocked normalization, docs, and tests are in place; no live API calls by default |
| 14 | Web dogfood/eval suite | complete for local/mock-first v1 | Provider registry and source grounding | `internet_core`, `web_providers`, `web_fetch`, `web_research`, and `web_blocked_sources` suites plus `eval_cases/internet` added; live web/provider checks remain opt-in |
| 15 | Internet Access release gate | complete for local v1 | Selected track items complete | Full tests, startup policy, manifest validation, docs/command validation, cost-policy checks, no-bypass scans, dry-run dogfood, and fixture-backed `eval run --internet` recorded; live provider validation remains environment-gated |

## Reddit + Multilingual Forum Intelligence Track

This track starts from documentation and compliance policy. It must remain read-only, source-grounded, retention-bounded, no-scraping, no-bypass, no-training, no paid-provider-by-default, and ToolBroker-only before any runtime forum connector is added.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 0 | Reddit/forum architecture, policy, and roadmap | complete | Internet Access dogfood/eval release gate | Planning docs created; no Reddit API calls, scraping, forum-content storage, training, browser automation, or CLI commands added |
| 1 | Reddit provider policy and compliance scaffolding | complete | Reddit/forum architecture, policy, and roadmap | Disabled-by-default config, OAuth-required metadata checks, hard-false training flag, no web fallback, manifest placeholders, retention/rate-limit docs, and tests added; no API calls or scraping |
| 2 | Reddit OAuth/config doctor | complete for local diagnostics | Reddit provider policy and compliance scaffolding | Brokered `reddit doctor`, `reddit status`, explicit `reddit auth-check`, and `connectors status reddit` added; no Reddit posts/comments/threads fetched, secrets redacted, auth-check mocked locally and live validation remains opt-in |
| 3 | Reddit official read-only connector | complete for local mocked v1 | Reddit provider policy and OAuth/config doctor | OAuth/config gated official Data API client, normalized read-only models, brokered search/subreddit/post/comments/cache/retention commands, no unauthenticated web scraping substitute, all content `UNTRUSTED_WEB`; live API validation remains opt-in |
| 4 | Reddit search workflows | complete for local mocked v1 | Reddit connector and retention defaults | Search commands support subreddit/sort/time/limit/advisory-language options, snippet-only labels, source IDs, setup hints, no-history cache keys, and local explain-result metadata lookup; live API validation remains opt-in |
| 5 | Reddit thread fetch and conversation normalization | complete for local mocked v1 | Reddit connector and search workflows | Brokered `reddit thread` / `reddit thread-export`, official API-only thread fetch, normalized comment tree and flattened comments, source references, truncation/collapse metadata, removed-comment handling, author redaction, workspace-only `UNTRUSTED_DOCUMENT` export; live API validation remains opt-in |
| 6 | Reddit source-grounded summaries | complete for local mocked v1 | Reddit search/thread fetch and citation policy | Brokered `reddit summarize-thread`, `summarize-search`, `consensus`, `pros-cons`, `complaints`, and `buying-advice` commands produce deterministic source-grounded sections with source IDs/permalinks, snippet-only vs fetched-thread labels, anecdotal caveats, deleted/removed exclusion, prompt-injection exclusion, and no summary memory writes; live API validation remains opt-in |
| 7 | Reddit retention/cache compliance | complete for local mocked v1 | Reddit connector and source grounding | Brokered `reddit cache status`, `cache clear`, `retention status`, `retention sweep`, and `privacy-report`; TTL-bounded public cache only, author metadata disabled by default, deleted/removed content not retained, query-like fields redacted before cache write, privacy reports count-only, and live provider retention QA remains opt-in |
| 8 | Language detection + translation | complete for local tested v1 | Multilingual strategy | Local heuristic detection, brokered language commands, local-model translation setup-required fallback, model-generated labels, source IDs/chunks preserved, and no memory write; live local-model quality QA remains opt-in |
| 9 | Cross-language research workflow | complete for local mocked v1 | Language layer and forum source grounding | Brokered `forums research` and `forums compare` commands source configured providers, report unavailable/setup-gated sources, label translations as generated, preserve source IDs/original snippets, write no memory, and avoid cultural/statistical consensus claims; live Reddit/V2EX/web provider validation remains opt-in/future |
| 10 | Global forum provider registry | complete for local tested v1 | Forum access policy | Static provider metadata, brokered provider/status/doctor/capabilities commands, discovery-only site filters, no personal/logged-in/network status reads, no write capabilities, and command registry/test coverage added; live provider connectors remain separate |
| 11 | V2EX connector | complete for local mocked v1 | Provider registry and language layer | Brokered documented API-only read connector with disabled-by-default config, optional redacted token, normalized forum models, local rate limit/TTL cache, optional language workflow, no member/profile/notification/write access, and live validation still opt-in |
| 12 | Chinese forum discovery/search/fetch | complete for local mocked v1 | Provider registry, V2EX connector, safe web fetch | Brokered `cn-forums` provider/search/fetch/research commands use approved search-provider site filters and safe selected-URL fetch only; blocked/login/CAPTCHA pages report unavailable, content is `UNTRUSTED_WEB`, language detection/optional local translation are integrated, no cookies/browser sessions or memory writes are used, and live provider validation remains opt-in |
| 13 | Forum dogfood/eval suite | complete for local/mock-first v1 | Reddit/V2EX/language/discovery milestones | Default-disabled dogfood suites and fixture-backed `eval run --forums` cover source grounding, generated translation labels, retention, no-bypass, no paid defaults, no memory write, provider-call audit evidence, and prompt-injection fixtures; live provider checks remain opt-in |
| 14 | Forum Intelligence release gate | complete locally | Dogfood/eval suite | Full tests, startup policy, capability manifest, command registry validation, forum dogfood dry-runs, fixture-backed forum evals, safe Reddit/V2EX status checks, retention/cache/privacy checks, and no-scraping/no-write/no-training scans passed locally; live provider and translation-quality validation remain opt-in/config-gated |

## Overnight Self-Improvement Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Overnight self-improvement runbook | complete | Scheduler v1, PromptOps, controlled self-improvement loop | Planning-only runbook and planner complete; no hidden persistence, background runner, or 6-hour run approval |
| 2 | Safe 6-hour overnight self-improvement run | complete | Overnight runbook complete and explicitly approved by user | Completed bounded safe-only docs/tests/diagnostics/tracking run on `agent/overnight-2026-05-23`; no background persistence, personal-data access, package install, send/write path, policy weakening, or commit; future overnight runs require separate explicit approval |
| 3 | Overnight self-improvement release gate | planned | Any approved overnight run completes | Full tests, audit review, diff review, prompt/action review, and no policy weakening |

## Dogfood and QA Track

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Live Session Logging and Replay | complete | Command Registry + Manual QA System | Redacted capture/replay tested locally; no AuditLogger replacement; no personal-data defaults |
| 2 | Manual dogfood command suites | complete | Live Session Logging and Replay | Curated YAML suites and `dogfood list/show/run` commands complete; release gate passed with `all_safe --dry-run`; first full `all_safe --session` run still recommended |
| 3 | Feedback capture and ratings | complete | Manual dogfood command suites | Redacted session feedback capture complete; no memory writes and unsafe feedback escalates severity |
| 4 | Session review and bug generator | complete | Feedback capture and ratings | Redacted session review and local bug generation complete; no auto-fixes, no external sends, no personal-data connector reads |
| 5 | Regression test generator from bugs | complete | Session review and bug generator | Validated with `BUG-0002` scaffold generation; generated tests remain skipped until converted to concrete assertions |
| 6 | Live test runbook and daily dogfood workflow | complete | Manual dogfood suites, session logging, feedback capture, and session review | Daily/weekly runbooks, checklist template, and planning commands complete; no personal-data live reads by default |
| 7 | Product Quality Dashboard | complete | Session logging, feedback capture, bug generator, eval reports, feature maturity, and live test runbook | Read-only CLI dashboard complete; release gate passed over synthetic session/bug/regression evidence |
| 8 | Live Dogfood + Session Review release gate | complete | Session logging, feedback capture, session review, regression generator, product quality dashboard | Full tests, policy/manifest/docs validation, safe dogfood dry-run, synthetic session, feedback, bug, regression scaffold, quality dashboard, and redaction checks passed |

## Apple Ecosystem + Lead Response Track

This track is planning and safety first. It does not enable personal-data reads, private database access, message sends, hidden polling, background automation, or connector execution by itself.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Apple ecosystem architecture decision | complete | Dogfood release gate and provider doctor tracking | Planning-only decision record created; future Calendar/Reminders use EventKit or a permissioned native bridge; no runtime behavior added |
| 2 | Lead Inbox abstraction | complete | Apple ecosystem architecture decision | Mock-only runtime foundation added with brokered lead list/classify/draft/follow-up commands, MessageDraft creation, Action Center follow-up task drafts, no real provider reads, no sends, and selected full reads disabled by default |
| 3 | Calendar/Reminders connector hardening | planned | Apple ecosystem architecture decision, existing calendar/tasks connectors | Selected-scope only; HIGH reads and CRITICAL writes keep Action Center gates |
| 4 | Contacts connector hardening | planned | Apple ecosystem architecture decision, contacts read/write foundations | Selected contact/field scope only; no bulk export or silent edits |
| 5 | Gmail lead-source adapter | planned | Secret/config doctor and LeadInbox abstraction | Metadata/read-selected/draft-first only; no inbox bulk ingestion |
| 6 | Telegram lead-source adapter | planned | Secret/config doctor and LeadInbox abstraction | Selected lead/chat scope only; no chat reads or sends by token presence |
| 7 | Apple Messages for Business strategy and provider stub | complete | Apple ecosystem architecture decision, Lead Inbox abstraction | Strategy and local mock provider stub complete; `apple-business doctor/status/mock-inbound/draft-response` create no live provider calls or sends |
| 8 | Personal iMessage bridge strategy | specified | Apple Messages strategy | Consumer Messages/iMessage auto-send remains deferred; no Messages DB scraping or Full Disk Access |
| 9 | Messages draft/handoff hardening | complete for v1 | Existing Messages safe handoff v1 | Added local draft-id workflow, `messages draft`, `messages handoff`, draft-id save/copy approval flow, and Lead Inbox draft capability; automatic send remains deferred |
| 10 | Lead response draft workflow | complete | LeadInbox abstraction | Draft-only workflow implemented with summarize/classify/draft/suggest-followup/suggest-meeting; no sends, no memory writes, and no calendar events |
| 11 | Lead follow-up task workflow | planned | Lead response draft workflow and tasks connector | Suggested tasks become Action Center items only |
| 12 | Lead scheduling workflow | planned | Lead response workflow, calendar availability, contacts selected-scope | Suggested meeting times only until approved actions exist |
| 13 | Approved lead response send | complete for local v1 | Lead drafting, provider strategy, Action Center release gate, explicit user approval | Added CRITICAL exact-preview send-action creation, `leads send --from-action` orchestration, iOS compose handoff, manual fallback, macOS gate delegation, no approval reuse, no bulk/auto-send; live provider sends remain disabled/unvalidated |
| 14 | Auto-response policy design | deferred | Approved send workflow live validation and explicit future decision | Narrow templates only if separately approved; no autonomous handling |
| 15 | Apple ecosystem release gate | planned | All selected Apple/lead features complete | Full tests, startup policy, manifest validation, docs validation, default-disabled scan, and approval/audit review |

## Apple Ecosystem + Messaging

This track narrows the Apple ecosystem plan to messaging/iMessage decisions. It distinguishes iOS user-confirmed compose, macOS Messages automation feasibility, disabled-by-default approved macOS send, and Apple Messages for Business. It does not enable message reads by default, Messages database access, broad Full Disk Access, background automation, bulk sending, or silent sending.

| Order | Feature / Task | Status | Prerequisites | Approval / Gate |
|---:|---|---|---|---|
| 1 | Message channel abstraction | complete | `apple-messaging-roadmap-track` complete | Channel-neutral schemas, registry metadata, brokered draft preview/validation; no private reads, direct/silent sends, credentials, or hidden polling |
| 2 | Message safety policy | complete | Message channel abstraction | Draft creation and send-action proposals are brokered; sends are CRITICAL Action Center records with exact local previews, no approval reuse, draft-edit invalidation, no send executor, and bulk sending FORBIDDEN in v1 |
| 3 | Lead Inbox abstraction | complete | Existing LeadInbox decision record | Channel-neutral mock Lead Inbox foundation added; no provider reads, no private Messages database access, no sends, and future approved response send remains blocked |
| 4 | iOS user-confirmed compose bridge | complete | Message channel abstraction and safety policy | Agent-side mock/interface bridge creates expiring local handoff payloads and records returned compose results; no iOS app or silent send adapter exists |
| 5 | macOS Messages automation probe | complete | Explicit future approval | Metadata-only `messages probe` implemented through ToolBroker; no send, private database read, Full Disk Access, account scrape, or UI Send scripting |
| 6 | Draft/handoff workflow | complete for v1; hardening planned | Existing Messages safe handoff v1 | Manual selected text/workspace fallback; save/copy via Action Center when risky |
| 7 | Incoming message strategy | complete for manual/mock v1 | Message channel abstraction | Manual workspace import and mock inbox only; no hidden polling, broad history reads, contact harvesting, private database scraping, Full Disk Access, auto-reply, or send |
| 8 | macOS approved iMessage send adapter | complete for disabled-by-default v1 | macOS probe, Action Center gate, explicit user prompt | CRITICAL per-action approval only; no approval reuse; requires connector enablement, allowlist, recent live-send probe, rate limit, and clear unsupported fallback |
| 9 | Apple Messages for Business connector stub | complete for mock v1 | Provider/business setup decision and mock adapter | Local provider model, config-only doctor/status, mock inbound-to-LeadInbox mapping, and draft-response are complete; live provider/API/webhook/send remains future approval-gated work |
| 10 | Lead response drafting | complete | Lead response workflow | Draft-only workflow implemented; lead content remains untrusted data, follow-up tasks are pending actions only, and meeting suggestions create no events |
| 11 | Approved lead response send | complete for local v1 | Provider strategy, Action Center, explicit send decision | CRITICAL exact-preview send-action orchestration implemented; iOS compose handoff and manual fallback do not silently send; macOS/provider sends remain disabled unless adapter gates pass |
| 12 | Messaging dogfood suite | complete | Draft/handoff and strategy docs | Added default-disabled messaging dogfood suites for core, handoff, iOS compose, macOS probe, send dry-run, and lead response; no live sends by default, live send probe excluded, and personal data uses fixtures/mock/preflight only |
| 13 | Messaging release gate | complete | Selected messaging features complete | Full tests, startup policy, capability manifest validation, docs validation, command registry validation, safe messaging dogfood, dry-run send suite, macOS metadata probe, default-disabled scan, approval/audit review, private Messages DB/FDA scan, and no-live-send confirmation passed on 2026-05-23 |

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
- Reminders / Tasks connector v1 with adapter/mock provider, brokered list/draft-create/create/update/complete/delete tools, Action Center task creation, and no native Reminders writes by default.
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
- Overnight self-improvement runbook, `improve overnight-plan` safe-mode planner, and the 2026-05-23 approved bounded docs/tests/tracking run; future overnight runs still require explicit approval.
- Scheduler / Automation v1 with explicit local schedule records, manual `schedule run`, audited lifecycle/run events, safe supported workflows including redacted `backup_create`, and no background runner.
- Prompt Ledger, Prompt Queue, and Prompt Pack tracking with reconstructed prompt statuses, queued/blocked prompt groups, prompt record directories, prompt pack splitting, prompt CLI commands, and prompt audit docs.
- PromptOps Workbench v1 with one-command prompt import from stdin/file/clipboard, next/copy/status/review commands, disabled-by-default runner, and safe-only autopilot guardrails.
- Command Registry + Manual QA System with 150 cataloged commands, generated command test matrix, legacy tracker, QA runbook, and read-only `commands` CLI inspection/validation commands.
- Disabled-by-default selected-scope calendar, contacts, email draft-only, and messages draft-only interfaces.
- Connector framework generalization.
- Feature maturity tracking.
- Native Skills Program foundation with intake process, selection criteria, risk model, candidate registry, and record template.
- Skill marketplace survey and native candidate shortlist with category scoring, defer list, and first-implementation recommendation.

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
37. Native Skills Program foundation.
38. Skill marketplace survey.
39. Native skill vetter.
40. Native skill manifest and loader.
41. Apple ecosystem architecture decision.
42. Lead Inbox abstraction.
43. Calendar/Reminders connector hardening.
44. Contacts connector hardening.
45. Gmail lead-source adapter.
46. Telegram lead-source adapter.
47. Apple Messages for Business strategy.
48. Personal iMessage bridge strategy.
49. Messages draft/handoff hardening.
50. Lead response draft workflow.
51. Lead follow-up task workflow.
52. Lead scheduling workflow.
53. Approved lead response send.
54. Auto-response policy design.
55. Apple ecosystem release gate.
41. Skill finder native skill.
42. PDF workspace native skill.
