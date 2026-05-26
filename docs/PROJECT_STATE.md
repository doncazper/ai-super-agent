# Project State

This is the durable resume file for Codex runs in this repository. Read it before making changes and update it before ending a run.

## Purpose

Build a local Mac AI agent with safety-first governance, ToolBroker-only tool execution, explicit policy/permission/approval/audit controls, and resumable SDLC documentation.

## Current Overall Phase

Brain Runtime Independence `BRAIN-01` through `BRAIN-11` are complete by explicit user request. The local release gate validates the provider-neutral brain runtime scaffold: BrainProvider interface, lazy model registry, LM Studio provider wrapping, disabled local-provider scaffolds, mock benchmark/eval reports, fallback/router metadata, disabled MCP stubs, command registry, startup/capability validation, and optional import guards. No default-provider change, paid/cloud API default, MCP enablement, listener startup, model/runtime install, model download, personal-data enablement, high-risk tool execution, no-tools regression, ToolBroker flow change, unverified tool-call support, or safety-control bypass was added. LM Studio dependency is partially optional, not fully removed, because normal live chat still uses the existing LM Studio-compatible path until future gateway wiring. Hermes-inspired Safe Autonomy `HERMES-01` through `HERMES-13` are complete locally after recovering the skipped HERMES-09 sequence. The track now includes architecture/policy docs, gateway/channel process scaffolding, Telegram/mobile status scaffolding, repeated-task skill proposal commands, skill improvement proposal commands, scheduler UX/dry-run commands, subagent isolation metadata/mock dry-run commands, sandbox backend abstraction/mock dry-run commands, model switching/session-continuity metadata, redacted memory continuity/context-preview commands, authorized web automation boundary docs, mock-first safe autonomy dogfood/eval suites, and a local release gate/maturity review. It remains local-tested groundwork only: no runtime autonomy, external channel connections, bot polling, webhook/listener startup, background persistence, personal-data access/carryover, send/write behavior, browser automation, real subagent launch, subagent write permissions, direct subagent tool calls, CRITICAL subagent execution, arbitrary sandbox command execution, networked sandbox execution, Docker/VM/browser/cloud execution, cloud/private-data execution, automatic skill creation/import/enablement/execution, automatic skill modification, lockfile update, package installation, OS scheduler persistence, unattended HIGH/CRITICAL workflows, or safety-control bypass was added. Release Hardening Loop v2 completed locally with YELLOW release readiness. News Intelligence is now specified as a docs-first track with source policy, provider strategy, freshness controls, source grounding, retention policy, architecture decision, planned command tracking, disabled/planned capability manifest entries, safe config defaults, provider-policy selection logic, and conservative risk/threat notes; no runtime news command, provider call, article fetch, paid provider default, search-history storage, or full article-body persistence exists yet. Cross-Platform Core + Platform Bridge architecture is specified, Platform Capability Registry v1 exists as portable static metadata, platform bridge base interfaces exist, platform-aware config/paths/detection scaffolding exists with safe disabled/lazy defaults, read-only platform doctor/capability commands exist through brokered SAFE metadata tools, lazy macOS/iOS companion/Windows/web bridge stubs now exist as fail-closed implementation seams, the App Bridge API contract exists as disabled-by-default schema/docs scaffolding for future native/local frontends, and the current cross-platform release gate/future build guides are complete for the current groundwork. Runtime platform behavior remains future work. The repo has green local tests and validation, release audit/blocker/plan docs, tracker navigation docs, and generated artifact hygiene, but it still needs a human-reviewed clean release candidate boundary plus broader live/manual validation before broad feature expansion. Current tracker summaries are indexed from `docs/TRACKER_DASHBOARD.md` and `docs/TRACKER_INDEX.md`.

## Current Batch

No active prompt batch. Dirty-tree blocked prompt audit completed and stopped before feature execution. The Daydream Lab Idle Research pack remains imported and split into queued prompts only; no Daydream prompt was executed automatically.

## Current Task

`RUN-DIRTY-TREE-BLOCKED-PROMPTS-IN-ORDER-01` audited prompt packs previously blocked by dirty Git state, duplicate copied files, or remote/main confusion. Duplicate and remote/main blockers are resolved, but feature execution stopped because the Daydream import/tracker set remains uncommitted active dirty work.

## Current Status

Daydream is imported but queued-only. Local `main` now tracks `origin/main` at the same commit. The next boundary problem is not remote divergence; it is the dirty tree containing the Daydream import/tracker updates and the dirty-tree blocked prompt audit docs.

## Current Branch

`main`

## Last Known Good Commit

`148f10f Add launcher hardening and git boundary cleanup`

## Last Test Result

Dirty-tree blocked prompt audit with `./.venv/bin/python` available as Python 3.12.13: repo root verified, duplicate copied-file scan found no `* 2.*` files, local `main` and `origin/main` both point at `148f10f`, `./scripts/agent secrets scan` passed with placeholder-only tracked findings, `./scripts/agent git preflight` passed, `./scripts/agent commands validate` passed with 603 commands, `make policy-check` passed startup policy/capability validation, and `git diff --check` passed. Full pytest was not run because no runtime/source implementation changed and feature execution stopped.

## Startup Policy Status

startup policy ok.

## Prompt Tracking

- active_prompt_id: none
- next_prompt_id: CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01
- active_prompt_pack: none
- prompt_queue_status: Dirty-tree blocked prompt audit completed; Daydream remains imported/queued only; no feature prompt was executed.
- last_prompt_audit_result: 2026-05-26 dirty-tree blocked prompt audit classified launcher/canonical/performance/secrets/media/codebug/NLCMD/QA as completed, AIHUB v2/AuthScan/Writing/Memory Kernel/Bug Intelligence/Self-Heal as not imported/run, Daydream as imported/queued only, AIHUB v1 as superseded, and stale queued Reddit OAuth as needs separate reconciliation.
- current_prompt_batch: none.
- prompt_blockers: Large prompt-pack execution remains blocked by the dirty tree containing Daydream import/tracker updates plus this audit/plan work. Remote/main is no longer the current blocker.
- prompt_resume_instructions: No active prompt. First run the clean commit boundary flow for the Daydream import/tracker and dirty-tree audit docs, then start the next eligible pack in order. Do not force push, run queued packs wholesale, install packages, run live providers, call paid APIs, download models, access personal data, create web servers, start background services, rewrite runtime architecture, commit, or push without an explicit safe flow.

## Command QA Frontend/Backend Boundary

- `agent.qa.service.QAService` now owns read-only QA status/coverage/failure/bug/regression/maturity summaries and safe action wrappers for plan creation, safe batch runs, bug generation, regression generation, and self-heal planning.
- `agent.qa.api_models` defines JSON-serializable service/action envelopes and summary models for future frontends.
- `agent.qa.dashboard` is now a presentation adapter over the service boundary; `qa dashboard` and `qa status` report `backend_boundary=agent.qa.service.QAService`.
- Read-only service/dashboard calls do not execute commands. `run_safe_batch()` supports only Tier 0, Tier 1, and sandboxed Tier 3, and blocks HIGH/CRITICAL/FORBIDDEN or personal-data candidates before delegating to the existing safe runner.
- Docs added: `docs/qa/QA_FRONTEND_BACKEND_BOUNDARY.md` and `docs/qa/QA_DASHBOARD_API_CONTRACT.md`.

## Global Launcher

- `scripts/install-smartagent-launcher` now installs or repairs a user-level launcher alias, defaulting to `smartagent` in `$HOME/bin`, without sudo or system path writes.
- `agent.launcher` contains config models, diagnostics, wrapper generation, safe repair helpers, and a lightweight launcher CLI.
- `smartagent` launches `./scripts/agent --interactive`; `smartagent <args>` passes args to `./scripts/agent`; `smartagent --doctor` runs launcher-only diagnostics.
- Installer default repo selection now uses the current Git root from `git rev-parse --show-toplevel` when run from inside a clone, and falls back to the current directory only if it passes strong repo verification.
- Repo verification requires `smart_agent.py`, `scripts/agent`, at least two strong optional markers, and matching Git root when `.git` exists. It does not require LM Studio or live providers.
- Repo switching/status commands now include `smartagent --repo-status`, `smartagent --find-repos`, `smartagent --set-repo "/path/to/repo"`, and `smartagent --repair-path`.
- Repo discovery is bounded to configured/last-known/current/common user-owned paths plus explicit input; it does not scan the whole home directory and does not silently choose among multiple valid repos.
- Level 1 repairs are bounded to config refresh, unambiguous repo-path repair, Python selection metadata, and executable-bit fixes. Level 2 `.venv` repair/package install and shell profile edits require explicit flags. Level 3 destructive/system repairs are manual-only.
- Docs and command registry/test matrix rows were added in `docs/SMARTAGENT_GLOBAL_LAUNCHER.md`, README, `docs/COMMAND_REGISTRY.md`, and `docs/COMMAND_TEST_MATRIX.md`.

## Full Feature Status, Maturity, and Prompt-Tracker Audit Completed

- Current maturity ranking: strongest areas are Safety Control Plane, Command Registry, PromptOps, Workspace/Memory, Weather/Web local scaffolds, Native Skills metadata, and Safe Autonomy metadata. Weakest areas are News runtime providers, real platform bridge behavior, live/manual provider validation, clean release boundary, and prompt tracker reconciliation.
- Top blockers: large dirty worktree, stale prompt tracker rows, missing queued prompt files for some planned prompts, stale queued Reddit prompt file, generated artifact hygiene, and limited live/manual validation.
- Top next maturity queue: prompt tracker reconciliation, clean release-candidate boundary, generated artifact hygiene, static safety bypass scan, and current all-safe dogfood evidence.
- Prompt packs incomplete or needing review: Apple platform compatibility, command QA/self-heal, and natural-language command understanding prompt packs have file evidence but no completion evidence verified in this audit.
- Prompts likely missed or stale: stale SKILL queued rows, stale `news-capability-manifest-provider-policy` queue reference in older audit text now corrected, and stale `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md`.
- Recommended first prompt to run next: `news-provider-registry-status-commands`.
- Recommended first dogfood suite: `dogfood run all_safe --dry-run` for preview, then a controlled `all_safe --session` only if live/web commands are intentionally allowed by the user.

## Cross-Platform Core + Platform Bridge Track

This track is underway after the docs-only architecture milestone and metadata-only capability registry. It must keep the Python core platform-neutral, CLI-only mode functional, platform bridges optional/lazy/disabled by default, platform-specific imports out of core startup, and all future actions routed through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.

1. Cross-platform architecture and roadmap. Complete as docs-only work.
2. Platform capability registry. Complete as metadata-only registry with 27 static planned/stubbed records.
3. Platform bridge base interfaces. Complete as interface-only work with NullPlatformBridge and lazy registry.
4. Platform-aware config, paths, and detection. Complete as config/path/detection scaffolding with safe defaults and tests.
5. Platform doctor and capability commands. Complete as brokered read-only metadata CLI commands.
6. macOS/iOS/Windows/web bridge stubs. Complete as lazy fail-closed stubs with no native imports, personal-data reads, side effects, or platform actions.
7. App Bridge API contract. Complete as disabled-by-default contract/schema/docs scaffolding with no server, frontend, remote access, personal-data access, or approval bypass.
8. Platform capability manifest and ToolBroker mapping.
9. Startup overhead and lazy-load guardrails.
10. Cross-platform release gate and future build guide. Complete for current groundwork by explicit user request; manifest mapping and dedicated startup guardrails still remain required before real platform behavior.

## Next Feature Set: Controlled Actions and Product Quality

This is the next product-feature track to keep visible before starting implementation. Items already built remain marked complete in `docs/FEATURE_ROADMAP.md`; planned items must still get their own mini-SDLC, tests, docs, and release gates.

1. Golden eval suite + quality scorecards. Complete for local tested v1; live LM Studio/provider validation remains opt-in.
2. Unified Action Center v1.
3. Tasks / Reminders connector v1.
4. Calendar approved writes v1.
5. Contacts approved edits v1.
6. Email approved send v1.
7. Messages safe handoff v1.
8. Browser selected-tab / clipping v1.
9. Notes / knowledge capture v1.
10. Privacy Center / data inventory v1. Complete for local tested v1; metadata-only inventory and redacted export.
11. Backup / restore / migration v1. Complete for local tested v1; restore live smoke should use a disposable project copy only.
12. Model-router benchmark and prompt quality evals. Complete for local tested v1; live LM Studio answer-quality smoke remains opt-in.
13. Scheduler / automation v1. Complete for manual-run v1, including optional redacted `backup_create`.
14. Controlled self-improvement implementation loop.
15. Overnight self-improvement runbook and one approved bounded safe-mode run. Complete for planning-only runbook, `improve overnight-plan`, and the 2026-05-23 docs/tests/tracking run; future overnight runs require separate explicit approval.
16. Full release gate + maturity review. Complete locally; live validation remains opt-in where noted.

## Internet Access Graduation Track

This is the next active web/research hardening track. It is docs/tracking first and must remain free-first, cache-first, ToolBroker-only, and no-bypass by default.

1. Cost-aware provider policy. Complete and hardened with brokered `web providers`, `web provider-policy`, and `web provider-decision` inspection commands.
2. Web Acquisition Layer core. Complete for local v1 via `FREE-FIRST-WEB-ACQUISITION` plus central `agent.web_acquisition` models/router and brokered `web source-status` inspection.
3. Robots/sitemap/feed support. Complete for local v1, including core parser modules, alias capabilities, 500 sitemap URL / 50 feed item defaults, and focused safety tests.
4. Search provider registry. Complete for local v1 as `WEB-SEARCH-PROVIDER-REGISTRY`; metadata-only registry and brokered inspection command added.
5. SearXNG provider. Complete for local v1 as `SEARXNG-PROVIDER`; configured self-hosted base URL only, disabled by default, no public instance fallback, mocked provider tests pass, and live instance validation remains opt-in.
6. Brave provider hardening. Complete for local v1 as `BRAVE-PROVIDER`; disabled by default, requires API key plus paid/quota policy opt-in, mocked provider tests pass, and live key validation remains opt-in.
7. SerpAPI optional fallback. Complete for explicit paid-policy-gated fallback and reverified/hardened with `SERPAPI_ENABLED=true` plus daily-cap gates and config-only doctor.
8. Safe fetch/extraction hardening. Complete for local v1.
9. Source-grounded research workflow hardening. Complete for local v1.
10. Router internet-only-when-needed behavior. Complete for local v1.
11. Citation/source attribution. Complete for local v1.
12. Cache/dedupe/local lightweight index. Complete for local v1.
13. Official API connector framework. Complete for local framework/stub v1.
14. Web dogfood/eval suite. Complete for local/mock-first v1; live web/provider checks opt-in.
15. Internet Access final release gate. Complete for local v1; live provider validation remains opt-in and environment-gated.

## News Intelligence Track

This future track graduates generic web/research current-events work into dedicated news commands and provider policy. It must remain source-grounded, freshness-aware, free-first, cache-first, no-history-by-default, no-full-article-body-by-default, no-paid-provider-by-default, and no-bypass by default.

1. News Intelligence roadmap and source policy. Complete as docs/tracking only.
2. News capability manifest entries and provider policy. Complete as disabled/planned manifest entries, safe config defaults, provider-policy helpers, and tests only.
3. News provider registry and status commands. Recommended next.
4. News cache and retention scaffolding.
5. RSS/Atom and news sitemap headline acquisition.
6. GDELT provider.
7. Optional Media Cloud and NewsAPI providers.
8. News top/search/topic/source commands.
9. News brief/timeline/compare commands.
10. Multilingual news summaries.
11. News dogfood/eval suite and release gate.

## Reddit + Multilingual Forum Intelligence Track

1. Reddit/forum architecture, policy, and roadmap. Complete.
2. Reddit provider policy and compliance scaffolding. Complete.
3. Reddit OAuth/config doctor. Complete for local diagnostics.
4. Reddit official read-only connector. Complete for local mocked v1.
5. Reddit search workflows. Complete for local mocked v1.
6. Reddit thread fetch and conversation normalization. Complete for local mocked v1.
7. Reddit source-grounded summaries. Complete for local mocked v1.
8. Reddit retention/cache compliance. Complete for local mocked v1.
9. Language detection + translation. Complete for local tested v1.
10. Cross-language research workflow. Complete for local mocked v1.
11. Global forum provider registry. Complete for local tested v1.
12. V2EX connector. Complete for local mocked v1.
13. Chinese forum discovery/search/fetch. Complete for local mocked v1.
14. Forum dogfood/eval suite. Complete for local/mock-first v1; live provider checks remain opt-in.
15. Forum Intelligence release gate. Complete locally; live Reddit, V2EX, Chinese forum discovery, and translation quality validation remain opt-in/config-gated.

## Overnight Self-Improvement Track

- `OVERNIGHT-RUNBOOK` is complete and planning-only.
- `OVERNIGHT-SAFE-6H` completed for this explicitly approved bounded run on `agent/overnight-2026-05-23`; future overnight runs require separate explicit approval.
- No hidden persistence, background services, package installs, personal-data access, or approval-gated actions may run automatically.

## Last Updated Timestamp

2026-05-26 07:44 UTC / 2026-05-26 00:44 PDT

## Last Completed Work

- `DUPLICATE-CLEANUP-GH-AUTH-GIT-BOUNDARY-01` completed locally. Verified the repo root is `/Users/sambehdjou/Documents/AI Super Agent`; fresh duplicate search found no remaining `* 2.*` files; `gh` exists but is not authenticated; `git push --dry-run` failed due missing upstream; explicit dry-run push to `origin/main` failed as non-fast-forward; local `main` and `origin/main` remain unrelated with no merge-base. Added `docs/git/DUPLICATE_CLEANUP_GH_AUTH_GIT_BOUNDARY_REPORT.md` and updated duplicate cleanup, remote-main, artifact, prompt tracker, project state, and completion docs. No files were staged, committed, pushed, deleted, imported, or run as queued prompt packs.

- Global Launcher repo discovery/switching hardening is complete for this scoped run. Implemented strong repo marker verification, current-Git-root installer defaults, bounded candidate discovery, `--repo-status`, `--find-repos`, `--set-repo`, stricter `--repair-path`, generated-wrapper discovery parity, launcher config `last_repo_verification_status`, docs, registry/maturity/roadmap updates, intent-index classification to avoid natural-language unknown-route pollution, and launcher/full-suite validation. No sudo/system writes, package installs, shell profile edits, whole-home scans, live provider calls, personal-data access, commit, or push were performed.
- AI Ecosystem Intelligence v2 pack request was re-inspected and blocked before import/run. The source pack exists at `prompts/packs/ai-ecosystem-intelligence-v2.promptpack.md` and contains `AIHUB-01` through `AIHUB-20`, but there are still no queued/active/completed AIHUB prompt files. The duplicate `* 2.*` blocker is resolved, but the repo remains unsuitable for a 20-prompt feature batch because the launcher/cleanup work is uncommitted, `prompts/packs/bug-intelligence-and-failure-capture-v1.promptpack.md` is newly untracked, local `main` has no upstream, and `origin/main` is unrelated initial history. Validation for the blocked preflight used `./.venv/bin/python` 3.12.13: secrets scan passed with placeholder-only tracked findings, git preflight passed for tracked scope, command registry validation passed with 599 commands, policy-check passed, and `git diff --check` passed. No AIHUB import, prompt split, queued prompt files, runtime code, Hugging Face provider, model/dataset/Space handling, live provider call, commit, or push was performed.

- `REMOTE-MAIN-RECONCILE-AND-DUPLICATE-FILE-CLEANUP-01` completed locally. Removed 179 byte-for-byte `* 2.*` duplicate files, removed 3 additional exact duplicate copy files, removed 2 empty duplicate provider directories, and quarantined the one differing stale source copy under ignored `docs/reconciliation/duplicate_file_quarantine/`. Added `docs/reconciliation/DUPLICATE_FILE_CLEANUP_REPORT.md`, `docs/git/REMOTE_MAIN_RECONCILIATION_PLAN.md`, and updated artifact tracking, prompt tracking, changelog, project state, and completion report. Remote diagnosis: local `main` has no upstream; `origin/main` is unrelated `5115a76 Initial commit`; no merge-base exists; no merge, rebase, force push, commit, or push was performed. AIHUB was not imported or run.

- `GLOBAL-LAUNCHER-SELF-REPAIR-AND-LAUNCH-01` completed locally. Added `agent/launcher/`, `scripts/install-smartagent-launcher`, launcher tests, global launcher docs, README setup guidance, command registry/test matrix rows, feature registry/maturity/roadmap updates, changelog, project state, and completion report updates. Validation used `./.venv/bin/python` 3.12.13: launcher tests 29 passed; focused launcher/startup/command-registry tests 38 passed; command registry validation passed with 599 commands; policy-check passed; installer dry-run/repair-wrapper dry-run smokes passed; `git diff --check` passed. No real install, shell profile edit, `.venv` creation, package install, model/provider call, personal-data access, commit, or push was performed.

- AI Ecosystem Intelligence v2 pack request was inspected and blocked before import/run. The pack exists at `prompts/packs/ai-ecosystem-intelligence-v2.promptpack.md`, but no AIHUB prompt files are queued/active/completed. A duplicate untracked `prompts/packs/ai-ecosystem-intelligence-v2.promptpack 2.md` file is also present and should be reviewed during cleanup. Blockers are the unreviewed duplicate `* 2.*` files, unrelated remote `main` history, missing upstream on local `main`, and repository rules against automatic whole-pack execution. No Hugging Face connector, AI source registry, provider policy, model/dataset/Space/card normalization, supply-chain scanning, watchlist, dogfood/eval, release gate, commit, or push was performed.

- Self-Healing Rollback Maturity pack request was inspected and blocked before import/run. The pack exists at `prompts/packs/self-healing-rollback-maturity-v1.promptpack.md`, but no SELFHEAL prompt files are queued/active/completed. Blockers are the unreviewed duplicate `* 2.*` files, unrelated remote `main` history, missing upstream on local `main`, and repository rules against automatic whole-pack execution. No self-heal roadmap files, recovery capsule, rollback system, patch sandbox, safety lint, test ladder, dashboard, release gate, commit, or push was performed.

- Agent Memory Kernel and Tracker Intelligence pack request was inspected and blocked before import/run. The pack exists at `prompts/packs/agent-memory-kernel-tracker-intelligence-v1.promptpack.md`, but no MEMKERNEL prompt files are queued/active/completed. Blockers are the unreviewed duplicate `* 2.*` files, unrelated remote `main` history, missing upstream on local `main`, and repository rules against automatic whole-pack execution. No runtime feature, memory ingestion, tracker overwrite, commit, or push was performed.

- Canonical Runtime Gateway Hardening `CANON-10` completed on `checkpoint/large-working-tree-20260523`.
- Added `docs/runtime/CANONICAL_RUNTIME_RELEASE_GATE.md`, `docs/runtime/CANONICAL_RUNTIME_MATURITY_REVIEW.md`, `docs/reviews/EXTERNAL_REVIEW_HARDENING_RELEASE_GATE.md`, and release-gate docs tests. Full suite passed with 1723 tests, focused release-gate tests passed with 58 tests, command registry validation passed with 589 commands, policy-check passed, doctor commands passed, and all_safe dogfood dry-run passed. No server, background service, runtime rewrite, package install, model download, live provider call, personal-data enablement, send/write enablement, commit, or push was performed.

- Canonical Runtime Gateway Hardening `EXTREV-01` completed on `checkpoint/large-working-tree-20260523`.
- Added external architecture review parity findings, hardening plan, parity checklist, planned-only audit verifier/export command registry rows, release-gate docs, and docs tests. Audit receipt runtime implementation remains a planned follow-up, not a completed command.

- Canonical Runtime Gateway Hardening `CANON-09` completed on `checkpoint/large-working-tree-20260523`.
- Added read-only tracker sync preview and conflict commands, migration/sync policy docs, prompt tracker integration docs, command registry/test matrix rows, and tests. Canonical runtime state is now documented as the machine-readable active-work view while prompt ledger/queue/audit remain history, planned-order, and reconciliation views. No auto-overwrite, broad tracker rewrite, provider call, or tracker mutation was added.

- Canonical Runtime Gateway Hardening `CANON-08` completed on `checkpoint/large-working-tree-20260523`.
- Added read-only canonical dashboard and handoff metadata commands, docs, and tests. The dashboard summarizes canonical state, active prompt/job/workflow/action, next prompt, validation evidence, tracker conflicts, dirty worktree summary, safety status, gateway/kernel status, recovery hints, and handoff recommendations. It writes no files, mutates no trackers, executes no tools, calls no providers, starts no server, and resumes nothing.

- Canonical Runtime Gateway Hardening `CANON-07` completed on `checkpoint/large-working-tree-20260523`.
- Added brokered read-only backup roundtrip/policy/restore-check commands, restore hardening docs, capability manifest entries, command registry/test matrix rows, and tests for dry-run no-write behavior, restore hash checks, pre-restore copies, CRITICAL approval reuse refusal, unredacted secret refusal, and path traversal refusal. Restore remains HIGH approval-gated and live restore smoke remains disposable-workspace-only.

- Canonical Runtime Gateway Hardening `CANON-04` completed on `checkpoint/large-working-tree-20260523`.
- Added checkpoint and recovery report contracts, preview-only recovery behavior, read-only recovery/checkpoint commands, docs, tests, and command registry rows. Recovery preview does not auto-resume; active approval gates remain active; CRITICAL resumes require fresh explicit approval; prompt-pack recovery depends on prompt tracker evidence. No rollback executor, checkpoint writer command, tracker mutation, commit, or push was added.

- Canonical Runtime Gateway Hardening `CANON-03` completed on `checkpoint/large-working-tree-20260523`.
- Added Agent Gateway / Runtime Kernel boundary contracts, gateway request/response envelope previews, kernel/frontend status commands, docs/ADR, tests, and command registry rows. No Fastify/TypeScript gateway, local web server, listener, native UI, external tool exposure, direct tool execution, approval bypass, policy/capability mutation, CLI replacement, commit, or push was added.

- Canonical Runtime Gateway Hardening `CANON-02` completed on `checkpoint/large-working-tree-20260523`.
- Added durable execution record contracts for prompt/job/workflow/command/QA/self-heal/approval-gated/future media/future secret-scan records, read-only record list/show/latest/validate commands, docs, tests, and command registry rows. No queued prompt execution, background worker, executor, tracker mutation, raw secret/personal-data storage, web server, commit, or push was added.

- Canonical Runtime Gateway Hardening `CANON-01` completed on `checkpoint/large-working-tree-20260523`.
- Added read-only canonical runtime state model, source-of-truth hierarchy, reconciliation preview conflict markers, docs/ADR, targeted tests, and `runtime canonical-state`, `runtime source-of-truth`, and `runtime reconcile-preview` commands. No provider calls, tool execution, personal-data access, tracker mutation, web server, background service, package install, model download, commit, or push was added.

- Created `docs/HANDOFF_TO_CHATGPT.md` as a reporting-only handoff summary for ChatGPT. No runtime behavior, feature implementation, queued prompt execution, commit, or push was performed. The handoff records the current dirty git state, completed Performance Bottleneck Scanner pack, active prompt status, next prompt options, changed files, command/test evidence, source-of-truth conflicts, safety status, blockers, upload recommendations, and safe next actions.

- Secrets and API Key Management `SECRETS-08` release gate completed on `checkpoint/large-working-tree-20260523`.
- Added `docs/secrets/SECRETS_RELEASE_GATE.md` and `docs/secrets/SECRETS_MATURITY_REVIEW.md`, completed SECRETS-01 through SECRETS-08, and recorded the safe reliance boundary: local setup guidance, redaction, resolver/provider diagnostics, Keychain dry-run strategy, scanner, and Git preflight are safe to rely on for best-effort local hygiene; real Keychain access, live credential validation, external scanner parity, secret rotation, and commit/push decisions remain manual/future.
- Validation passed with `./.venv/bin/python` 3.12.13: full suite 1616 passed; `tests/secrets` 31 passed; startup policy and capability manifest validation passed via `make policy-check`; command registry validation passed with 541 commands; tracked/staged `secrets scan` and `git preflight` passed with no likely real secret findings.
- Remaining blocker: the worktree is large and dirty from multiple prior batches; run a clean release-candidate boundary review before staging, committing, or pushing.

- Native Skill System Hardening `SKILL-10` release gate completed on `checkpoint/large-working-tree-20260523`.
- Added native skill system release-gate and maturity-review docs, completed the metadata-only hardening batch through `SKILL-10`, and recorded the safe reliance boundary: metadata review/vetting/docs/evidence are safe; external skill installation/execution remains not approved.
- Validation passed with `./.venv/bin/python`: full suite 1205 passed, 1 skipped; startup policy and capability manifest validation passed; command registry ok with 428 commands; native skill manifests 3 valid; conflict detection 0 conflicts; docs-check current with 0 missing docs; native skill evals 3 pass and 5 personal-data skips; native skill dogfood suites 6/6 passed in a redacted session.
- Remaining blocker: reviewed real `native_skills.lock` and lockfile write/pinning workflow are deferred; manual external-skill intake/live QA remains required before any external skill user-ready claim.

- Native Skill System Hardening `SKILL-09` docs generator completed on `checkpoint/large-working-tree-20260523`.
- Added metadata-only docs generator, dry-run default docs generation, explicit `--write` catalog update, generated catalog, docs-check, docs-generation guide/template, command registry rows, and tests.
- Validation passed with `./.venv/bin/python`: focused docs generator tests 8 passed; broader docs-generator/harness/command tests 23 passed; docs/prompt/release artifact tests 11 passed; startup policy and capability manifest validation passed; command registry ok with 428 commands; native skill manifests 3 valid; full suite 1205 passed, 1 skipped.

- News capability manifest entries and provider policy completed on `checkpoint/large-working-tree-20260523`.
- Added 18 disabled/planned `news.*` capability manifest entries covering provider status, search/top/feed/sitemap/GDELT/optional paid provider placeholders, article fetch/extract placeholders, brief/timeline/compare/multilingual/cache/dogfood placeholders, all with risk/trust/default/approval/provider/rate-limit/memory/audit/docs/status metadata.
- Added safe `NEWS_*` config defaults and `agent.news` provider-policy helpers that select or skip candidates only; no provider network calls, article fetch/extract runtime, paid API default, search-history storage, full article-body persistence, or command execution path was added.
- Validation passed: News capability/provider-policy tests 10 passed; focused News/docs/maturity tests 28 passed; startup policy ok; capability manifest ok; command registry ok with 398 commands; full suite 1119 passed, 1 skipped.

- News Intelligence roadmap and source policy completed on `checkpoint/large-working-tree-20260523`.
- Created `docs/news/NEWS_INTELLIGENCE_TRACK.md`, `NEWS_SOURCE_POLICY.md`, `NEWS_PROVIDER_STRATEGY.md`, `NEWS_FRESHNESS_POLICY.md`, `NEWS_SOURCE_GROUNDING.md`, `NEWS_RETENTION_POLICY.md`, and `docs/decisions/news_intelligence_architecture.md`.
- Added planned/stubbed command registry entries for `news providers`, `news top`, `news search`, `news topic`, `news source`, `news brief`, `news timeline`, `news compare`, `news multilingual`, `news cache status`, and `news dogfood`.
- No runtime news commands, provider API calls, paid API defaults, article fetching, browser automation, search/news history storage, full article-body storage, fabricated source/citation path, or paywall/login/CAPTCHA/anti-bot bypass was added.
- Validation passed: News docs tests 5 passed; feature-registry regression plus News docs tests 6 passed; startup policy ok; capability manifest ok; command registry ok with 398 commands; full suite 1109 passed, 1 skipped.

- Chinese forum discovery/search layer completed on `checkpoint/large-working-tree-20260523`.
- Added `agent.forums.chinese_discovery`, brokered `cn_forums.providers`, `cn_forums.search`, `cn_forums.fetch`, and `cn_forums.research` tools, CLI commands, capability manifest entries, docs, command registry/test matrix updates, and tests.
- Discovery uses approved search-provider site filters for Zhihu, Baidu Tieba, Douban Groups, Xiaohongshu, Weibo, V2EX, and NGA; selected public URL fetches go through safe fetch policy only; blocked/login/CAPTCHA pages return unavailable; fetched content is `UNTRUSTED_WEB`; language detection and optional local-model translation are integrated.
- No platform-specific scraping, private/logged-in reads, cookies, browser sessions, CAPTCHA/anti-bot bypass, paid provider default, readable search-history persistence, long-term forum-content storage, forum-content training, or memory write was added.
- Validation passed: Chinese forum discovery tests 9 passed; docs/command/maturity/prompt tests 23 passed; startup policy ok; capability manifest ok with 185 capabilities; command registry ok with 377 commands; `cn-forums providers` CLI smoke passed without network calls; full suite 1027 passed, 2 skipped.

- V2EX read-only connector completed on `checkpoint/large-working-tree-20260523`.
- Added documented API-only V2EX client/provider/cache/normalizer modules, brokered `v2ex.status`, `v2ex.nodes.get`, `v2ex.node_topics`, `v2ex.topic.get`, `v2ex.topic_replies`, `v2ex.latest`, and `v2ex.hot` tools, CLI commands, connector status metadata, capability manifest entries, docs, and tests.
- V2EX remains disabled by default with optional redacted token config, no write/member/profile/notification endpoints, no scraping fallback, no logged-in/private reads, no CAPTCHA/anti-bot bypass, `UNTRUSTED_WEB` labels, TTL cache only, author metadata redacted by default, and no memory write.
- Validation passed: focused V2EX connector tests 9 passed; connector/forum/command/maturity/prompt tests 52 passed; connector regression tests 28 passed; startup policy ok; capability manifest ok; command registry ok with 373 commands; full suite 1018 passed, 2 skipped.

- Multilingual detection and translation layer completed on `checkpoint/large-working-tree-20260523`.
- Added `agent.language` detection, normalization, romanization, translation, and term extraction modules plus brokered `language.detect`, `language.translate_text`, `language.summarize_multilingual`, and `language.extract_terms` tools.
- Added CLI commands `language detect`, `language translate`, `language translate-file`, and `language glossary`; file commands read workspace files through brokered `filesystem.read`; translations are labeled `MODEL_GENERATED_TRANSLATION`; source IDs/chunks are preserved; source text remains `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`; no translations/source text are written to memory.
- No external/paid translation API, forum scraping, personal-data default enablement, content training, permanent forum/source storage, send/write action, or live provider call by default was added.
- Focused validation passed: `tests/test_language_layer.py` 9 passed with `./.venv/bin/python` 3.12.13. Final broader validations are recorded in the completion report for this run.

- Reddit retention/cache compliance completed on `checkpoint/large-working-tree-20260523`.
- Added `reddit.cache_status`, `reddit.retention_status`, and `reddit.privacy_report` brokered tools plus `reddit cache status`, `reddit retention status`, and `reddit privacy-report` CLI commands.
- Cache entries remain TTL-bounded and now report source/content-hash metadata; cache writes are disabled when TTL policy cannot be guaranteed; author metadata is stripped by default; deleted/removed payloads are not cached; query-like fields are redacted before cache write; privacy reports return counts and policy flags only.
- No Reddit API fetch expansion, web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation action, CAPTCHA/login/anti-bot bypass, paid provider default, content training, search-history persistence, permanent storage, or live Reddit call by default was added.
- Validation passed: focused Reddit retention/read-only/provider policy tests 30 passed; focused Reddit workflow retention/search/thread/summarization tests 33 passed; docs/tracking/command tests 28 passed; full suite 984 passed, 2 skipped; startup policy ok; capability manifest ok; command registry ok with 356 commands.

- Reddit source-grounded summarization completed on `checkpoint/large-working-tree-20260523`.
- Added `reddit.summarize_thread`, `reddit.summarize_search`, `reddit.consensus`, `reddit.pros_cons`, `reddit.complaints`, and `reddit.buying_advice` brokered tools plus `reddit summarize-thread`, `reddit summarize-search`, `reddit consensus`, `reddit pros-cons`, `reddit complaints`, and `reddit buying-advice` CLI commands.
- Summaries preserve Reddit source IDs/permalinks, label fetched-thread versus snippet-only evidence, include required consensus/disagreement/complaint/praise/caveat/source/fetch-limitation sections, exclude deleted/removed and prompt-injection-like comments from evidence, and do not write summaries to memory.
- No Reddit web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation action, CAPTCHA/login/anti-bot bypass, paid provider default, content training, search-history persistence, permanent summary memory storage, or live Reddit call by default was added.
- Validation passed: focused Reddit summarization/provider policy tests 15 passed; focused Reddit workflow suite 55 passed; docs/tracking/command tests 28 passed; full suite 974 passed, 2 skipped; startup policy ok; capability manifest ok; command registry ok with 353 commands; prompt audit ok with zero active prompts and 149 completed prompts.

- Reddit thread fetch and conversation normalization completed on `checkpoint/large-working-tree-20260523`.
- Added `reddit.fetch_thread` and `reddit.thread_export` brokered tools, `reddit thread` / `reddit thread-export` CLI commands, thread comment-tree plus flattened-comment normalization, source references/permalinks, max-comment truncation, collapse-depth metadata, removed-comment handling, workspace-only exports labeled `UNTRUSTED_DOCUMENT`, command registry entries, docs, and regression tests.
- No Reddit web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation action, CAPTCHA/login/anti-bot bypass, paid provider default, content training, permanent memory storage, or live Reddit call by default was added.
- Validation passed: focused Reddit thread/read-only/provider policy tests 26 passed; docs/prompt/command/thread tests 29 passed; full suite 967 passed, 2 skipped; startup policy ok; capability manifest ok; command registry ok with 347 commands; prompt audit ok with zero active prompts and 148 completed prompts.

- Reddit search workflows completed on `checkpoint/large-working-tree-20260523`.
- Added polished `reddit search` options for subreddit, sort, time, limit, and advisory language; added snippet-only evidence labels, stable source IDs/permalinks, query-hashed cache keys, local `reddit explain-result <source_id>` metadata lookup, setup-required disabled/OAuth-missing behavior, and rate-limit error handling.
- No Reddit web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation action, CAPTCHA/login/anti-bot bypass, paid provider default, content training, permanent user-content storage, search-history persistence, or live Reddit call by default was added.
- Validation passed: focused Reddit search/read-only/provider tests, command/manifest/policy validations, CLI smokes, prompt audit, and full suite 961 passed, 2 skipped.

- Reddit read-only connector v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `agent/forums/reddit/client.py`, `models.py`, `provider.py`, `normalizer.py`, `errors.py`, `retention.py`, brokered Reddit read-only tools, CLI commands for search/subreddit/post/comments/cache/retention, capability manifest entries, command registry/test matrix updates, docs, and tests.
- No Reddit web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation action, CAPTCHA/login/anti-bot bypass, content training, permanent user-content storage, author metadata storage by default, or search-history persistence was added. Live Reddit API validation remains opt-in and credential/config dependent.
- Validation passed: focused Reddit connector tests, command/manifest/policy validations, prompt audit, and full suite 951 passed, 2 skipped.

- Reddit + Multilingual Forum Intelligence Track planning completed on `checkpoint/large-working-tree-20260523`.
- Created `docs/decisions/reddit_forum_intelligence_track.md`, forum access/Reddit/multilingual/Chinese/source-grounding/retention policy docs, and prompt completion evidence for `REDDIT-FORUM-INTELLIGENCE-TRACK`.
- Updated feature roadmap, registry, maturity, risk register, threat model, test plan, release checklist, prompt ledger/queue/audit, changelog, completion report, and project state.
- No runtime Reddit API calls, Chinese forum scraping, CAPTCHA/login/robots/anti-bot bypass, forum-content training, permanent forum storage by default, personal-data default enablement, paid API default, or CLI command changes were added.
- Validation passed in this run: focused docs/prompt validation 18 passed; startup policy ok; capability manifest ok with 143 capabilities; command registry ok with 334 commands; full suite 919 passed, 2 skipped; prompt audit ok with `REDDIT-PROVIDER-POLICY-COMPLIANCE` next.

- Internet Access dogfood/eval suite and release gate completed on `checkpoint/large-working-tree-20260523`.
- Added `internet_core`, `web_providers`, `web_fetch`, `web_research`, and `web_blocked_sources` dogfood suites; added recursive `eval_cases/internet/source_grounding.json`; added fixture-backed `eval run --internet` and `eval report --internet`; added `docs/web/INTERNET_DOGFOOD_RUNBOOK.md`; updated command registry/test matrix, README, dogfood docs, feature/risk/threat/test/release tracking, prompt tracking, changelog, and completion report.
- No live provider call, paid API default, browser automation, CAPTCHA/login/paywall/anti-bot bypass, personal-data tool enablement, search/web-content memory storage, or ToolBroker/PolicyEngine/AuditLogger bypass was added.
- Validation passed in this run: focused internet dogfood/eval tests 19 passed; targeted internet/command registry tests 10 passed; docs/prompt tracking/command docs tests 22 passed; full suite 918 passed, 2 skipped; `eval run --internet` passed 5 and skipped 5 personal-data evals; all five new dogfood suites dry-run ok; startup policy ok; capability manifest ok with 143 capabilities; command registry ok with 334 commands; prompt audit ok with `REDDIT-FORUM-INTELLIGENCE-TRACK` next.

- Official API Connector Framework v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `agent.web_acquisition.official_apis` interfaces, models, registry/domain matching, GitHub/Wikipedia/arXiv/Reddit provider stubs, brokered `web official-apis`, `web api-status <provider>`, and `web api-search <provider> "<query>"` commands, capability manifest entries, docs, tests, and command registry updates.
- No live API calls by default, no credentials committed, no high-risk personal connector implementation, no write operations, no Reddit web scraping fallback, no search-history/web-content memory storage, no paid API default, no CAPTCHA/login/paywall/anti-bot bypass, and no ToolBroker/PolicyEngine/AuditLogger bypass were added.
- Validation passed in this run: focused official API tests 9 passed; targeted official API/command tests 14 passed; targeted web/search/cache/official API tests 74 passed; feature/prompt docs tests 17 passed; full suite 913 passed, 2 skipped; startup policy ok; capability manifest ok with 143 capabilities; command registry ok with 332 commands; prompt audit ok with `INTERNET-DOGFOOD-EVAL-SUITE` next.

- Internet routing policy completed on `checkpoint/large-working-tree-20260523`.
- Added deterministic internet routing metadata in `agent.core.router`, read-only `router explain`, richer `preflight` route output, current/live/source-required/citation/URL routing, stable/local/no-tools clean routing, and prompt-injection-like routing suppression.
- Updated docs at `docs/web/INTERNET_ROUTING_POLICY.md`, README, command registry/test matrix, eval cases, feature registry, maturity tracker, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- No provider call during routing, LLM router default, user-message rewrite, query-history persistence, web-content memory storage, paid API default, CAPTCHA/login/paywall/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/PolicyEngine/AuditLogger bypass was added.
- Validation passed in this run: focused router/preflight tests 34 passed; targeted router/preflight/model-quality/command-registry tests 48 passed; final full suite 889 passed, 2 skipped; startup policy ok; capability manifest validation ok with 134 capabilities; command registry validation ok with 321 commands; prompt audit ok with `CITATION-SOURCE-ATTRIBUTION` next.

- Source-grounded research workflow v1 completed on `checkpoint/large-working-tree-20260523`.
- Hardened `research` to search through provider policy, optionally fetch selected sources, summarize only returned data, include real source URLs with retrieved timestamps and provider metadata, report snippet-only/fetched-page evidence, coverage limitations, and blocked/unavailable fetch failures, and keep `memory_written=false` / `query_history_persisted=false`.
- Added `--max-sources`, `--freshness`, broader explicit provider handling, `--no-fetch` behavior coverage, docs at `docs/web/SOURCE_GROUNDED_RESEARCH.md`, README research examples, command registry/test matrix updates, feature maturity/roadmap/risk/threat/test/release tracking, prompt completion evidence, and completion report updates.
- No new provider API implementation, live provider call, paid API default, fabricated citation path, web/search memory persistence, CAPTCHA/login/paywall/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/PolicyEngine/AuditLogger bypass was added.
- Validation passed in this run: focused source-grounded workflow tests 14 passed; targeted workflow/web/command tests 128 passed; feature/prompt docs tests 17 passed after updating the next-prompt allowlist; full suite 879 passed, 2 skipped; startup policy ok; capability manifest validation ok with 134 capabilities; command registry validation ok with 320 commands; prompt audit ok with `INTERNET-ROUTING-POLICY` next.

- SerpAPI fallback provider hardening completed on `checkpoint/large-working-tree-20260523`.
- Added disabled-by-default `SERPAPI_ENABLED=false`, `SERPAPI_TIMEOUT_SECONDS`, `SERPAPI_MAX_RESULTS`, stricter paid/quota gating requiring `ALLOW_PAID_APIS=true` and `MAX_PAID_API_CALLS_PER_DAY>0`, config-only `web serpapi doctor`, connector status metadata, setup/error normalization, SerpAPI provider-selection docs, and mocked tests.
- Updated `.env.example`, README provider setup, `docs/web/providers/serpapi.md`, `docs/web/PROVIDER_SELECTION.md`, search-provider docs, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- No paid API default, live provider call in validation, query-history persistence, web-content memory storage, CAPTCHA/login/paywall/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/AuditLogger bypass was added.
- Validation passed in this run: focused SerpAPI/provider/search/connector/workflow tests 94 passed; focused docs/prompt/command/provider tests 116 passed; full suite 869 passed, 2 skipped; startup policy ok; capability manifest validation ok with 132 capabilities; command registry validation ok with 317 commands; prompt audit ok with `WEB-FETCH-EXTRACTION-HARDENING` next; config-only SerpAPI doctor/status and setup-required explicit search smokes passed without provider calls.

- Brave provider v1 completed on `checkpoint/large-working-tree-20260523`.
- Added disabled-by-default `BraveSearchProvider` with `BRAVE_SEARCH_API_KEY`, `BRAVE_SEARCH_ENABLED=false`, `BRAVE_SEARCH_TIMEOUT_SECONDS`, `BRAVE_SEARCH_MAX_RESULTS`, `BRAVE_SEARCH_SAFE_SEARCH`, web/news result normalization, setup hints, timeout/401/403/429/malformed-response handling, config-only `web brave doctor`, and `connectors status brave`.
- Updated `.env.example`, README provider setup, `docs/web/providers/brave.md`, search-provider docs, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- No paid API default, live provider call in validation, query-history persistence, web-content memory storage, CAPTCHA/login/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/AuditLogger bypass was added.
- Validation passed in this run: focused provider/search/connector tests 65 passed; focused docs/prompt/command tests 92 passed; full suite 864 passed, 2 skipped; startup policy ok; capability manifest validation ok with 131 capabilities; command registry validation ok with 316 commands; prompt audit ok with `WEB-FETCH-EXTRACTION-HARDENING` next; config-only Brave doctor/status and setup-required explicit search smokes passed without provider calls.

- SearXNG provider v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `SearXngSearchProvider` with configured/self-hosted-only `SEARXNG_BASE_URL`, disabled-by-default `SEARXNG_ENABLED=false`, JSON result normalization, setup hints, timeout/403/429/malformed-response handling, config-only `web searxng doctor`, and `connectors status searxng`.
- Updated `.env.example`, README provider setup, `docs/web/providers/searxng.md`, search-provider docs, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- No public SearXNG instance default, live provider call in validation, paid API use, query-history persistence, web-content memory storage, CAPTCHA/login/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/AuditLogger bypass was added.
- Validation passed in this run: focused provider/search/connector tests 58 passed; focused docs/prompt/config tests 34 passed; focused prompt tracking regression rerun 5 passed; full suite 857 passed, 2 skipped after fixing the next-prompt expectation; startup policy ok; capability manifest validation ok with 130 capabilities; command registry validation ok with 314 commands; prompt audit ok with `BRAVE-PROVIDER` next; config-only SearXNG doctor/status and setup-required explicit search smokes passed without provider calls.

- Search Provider Registry v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `agent.web_acquisition.search` provider interface, metadata registry, normalized result/response models, setup/unknown-provider error normalization, brokered `web.search_providers`, generalized explicit `web search "<query>" --provider <provider>` setup-hint behavior, and `docs/web/SEARCH_PROVIDER_REGISTRY.md`.
- Updated command registry/test matrix, README, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- No live provider API call, paid-provider default, public SearXNG default, query-history persistence, web-content memory storage, CAPTCHA/login/anti-bot bypass, browser automation, personal-data tool enablement, or ToolBroker/AuditLogger bypass was added.
- Validation passed in this run: focused search/web tests 33 passed; focused command/maturity/prompt tests 22 passed; full suite 848 passed, 2 skipped; startup policy ok; capability manifest validation ok with 129 capabilities; command registry validation ok with 312 commands; prompt audit ok with `SEARXNG-PROVIDER` next.

- Internet Access release gate and roadmap reset completed on `checkpoint/large-working-tree-20260523`.
- Added `docs/decisions/internet_access_graduation_track.md`, `docs/web/WEB_ACCESS_POLICY.md`, `docs/web/INTERNET_PROVIDER_STRATEGY.md`, `docs/web/SOURCE_GROUNDING_REQUIREMENTS.md`, and `docs/web/BLOCKED_SOURCE_POLICY.md`.
- Updated roadmap, feature registry, feature maturity, prompt tracking, risk register, threat model, test plan, release checklist, changelog, README, and completion report for the clean Internet Access Graduation Track.
- No runtime provider implementation, live web call, paid API use, CAPTCHA/anti-bot/login-wall bypass, browser automation, browser profile access, or web query/content memory storage was added.
- Validation passed in this run: focused docs validation 12 passed, focused prompt/docs validation 17 passed, full suite 820 passed and 2 skipped, startup policy ok, capability manifest validation ok, command registry validation ok with 306 commands, and prompt audit ok with `WEB-SEARCH-PROVIDER-REGISTRY` next.

- Messaging / iMessage release gate completed on `checkpoint/large-working-tree-20260523`.
- Validation passed: final full suite 819 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok; focused docs/dogfood/prompt tests 30 passed before prompt completion; focused maturity/prompt tests 16 passed after queue advancement; safe messaging dogfood and dry-run suites returned ok.
- The macOS Messages metadata probe ran safely on this Mac and reported Messages.app metadata only: app found, AppleScript metadata available, `send_capability_known=false`, no private Messages database access, no Full Disk Access requirement, no message content read, and no send.
- Capability manifest scan confirms `messaging.send_approved`, `messages.macos.live_send_probe`, `messages.macos.send_approved`, `apple_business.message.send_approved`, `lead.send_approved`, and `email.send_approved` are default-disabled CRITICAL capabilities with `approval_required=per_action` and `approval_reuse_allowed=false`.
- Live send remains unavailable/unvalidated; current safe paths are draft/handoff, iOS compose payload generation for future user-confirmed compose, mock Apple Business inbound/draft, lead-response dry-run orchestration, and macOS metadata probing.

- Messaging Dogfood Suites completed on `checkpoint/large-working-tree-20260523`.
- Added default-disabled `messaging_core`, `messaging_handoff`, `messaging_ios_compose`, `messaging_macos_probe`, `messaging_send_dry_run`, and `lead_response` suites.
- Added `messaging ios-compose-record-result` CLI wrapper for the existing brokered iOS compose result recorder so mock sent/cancelled/failed handoff outcomes can be dogfooded.
- Updated dogfood/session/bug-triage docs plus command registry/test matrix and source-of-truth tracking docs.
- The suites exclude `messages macos live-send-probe`, avoid direct `send --from-action` outside preflight checks, keep `all_safe` free of live sends, use fixtures/mock/preflight data, and do not access private Messages data.
- Validation passed: focused dogfood/command/iOS-compose/maturity tests 37 passed; feature-maturity/prompt-tracking docs tests 16 passed; messaging dry-run suite smokes ok; full suite 819 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 306 commands.

- Approved Lead Response Send workflow v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `leads create-send-action`, `leads send --from-action`, `leads handoff`, and `leads mark-responded`.
- Send proposals are CRITICAL exact-preview Action Center records with no approval reuse; draft edits invalidate prior send approvals.
- `leads send --from-action` routes only through existing channel gates: iOS compose creates user-confirmed handoff payloads, manual handoff returns save/copy fallback, macOS Messages delegates to its disabled-by-default probe/allowlist/rate-limit adapter, and unsupported channels return structured fallbacks.
- Bulk lead responses, attachments, auto-send, private Messages database access, Full Disk Access, hidden polling, and memory writes are forbidden in v1.
- Validation passed: targeted lead inbox tests 19 passed; focused lead/messaging tests 62 passed; command/maturity/prompt tracking tests 21 passed; full suite 816 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 305 commands.

- Lead Response Drafting workflow v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `leads summarize`, `leads suggest-followup`, and `leads suggest-meeting` CLI paths alongside the existing classify/draft-response flow.
- Lead response drafts now include source, channel, classification, summary, assumptions, editable draft metadata, and explicit no-send/no-memory/no-calendar flags.
- Follow-up suggestions queue pending Action Center `tasks.create` records only; no real task is created.
- Meeting suggestions return reply guidance only; no calendar availability is read and no event is created.
- Lead content remains `UNTRUSTED_MESSAGE`; instruction-like source text is omitted from draft context and cannot request tools, approvals, policy changes, sends, or memory writes.
- Validation passed: targeted lead response tests 11 passed; focused lead/command/maturity tests 27 passed; full suite 808 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 301 commands.

- Apple Messages for Business provider strategy and connector stub completed on `checkpoint/large-working-tree-20260523`.
- Added `agent/messaging/providers/apple_business.py` with a disabled-by-default provider model, setup/status/doctor reporting, mock inbound Lead Inbox mapping, conversation status, and draft-only `MessageDraft` response creation.
- Added brokered `apple_business.doctor`, `apple_business.status`, `apple_business.inbound.receive`, `apple_business.message.draft_response`, and `apple_business.conversation.status`; future `apple_business.message.send_approved` remains CRITICAL, default-disabled, per-action/no-reuse, and unregistered as an executable send tool.
- Added `python smart_agent.py apple-business doctor`, `apple-business status`, `apple-business mock-inbound`, `apple-business draft-response <lead_id>`, and `apple-business conversation-status <lead_id>`.
- Mock inbound content is labeled `UNTRUSTED_MESSAGE`, stored locally under `./workspace/leads/apple_business`, mapped to Lead Inbox records, and never written to memory by default; draft responses create local drafts only and do not create send actions.
- No live provider calls, provider credentials, hidden webhook polling, personal iMessage automation, private Messages database access, Full Disk Access request, send execution, auto-response path, credential printing, or memory write path was added.
- Validation passed: Apple Business provider tests 7 passed; focused Apple Business/Lead Inbox/Messaging/Command/Maturity tests 41 passed; connector/privacy regression tests 23 passed; full suite 806 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 298 commands.

- macOS approved iMessage send adapter v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `agent/messaging/macos_send.py` with status, local recipient allowlist, CRITICAL live-send probe, CRITICAL approved-send execution, local probe/send status files, and rate-limit history.
- Added brokered `messages.macos.status`, `messages.macos.allowed_recipients.manage`, `messages.macos.live_send_probe`, and `messages.macos.send_approved`.
- Added `python smart_agent.py messages macos status`, `messages macos allow-recipient`, `messages macos live-send-probe --to`, and `messages send --from-action`.
- Send remains disabled by default via `MACOS_MESSAGES_ENABLED=false`, `MACOS_MESSAGES_ALLOW_SEND=false`, and disabled manifest entries for CRITICAL send/probe.
- Sends require a `channel=macos_messages` local draft, a `messages.macos.send_approved` Action Center item, exact preview match, CRITICAL no-reuse approval, allowlisted recipient, recent passing live-send probe, daily rate limit, and ToolBroker execution.
- No private Messages database read, Full Disk Access request, UI scripting of Send buttons, background responder, attachments, group/bulk send, non-allowlisted send, memory write, or fake success path was added.
- Validation passed: targeted macOS/message tests 42 passed; docs/command tests 23 passed; focused prompt/macos/command/maturity tests 33 passed; full suite 799 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 293 commands.

- Incoming message strategy and manual/mock inbox v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `agent/messaging/inbound.py`, manual/mock inbox providers, brokered `messages.inbox.import_manual`, `messages.inbox.list`, `messages.inbox.show`, and `messages.inbox.draft_reply`.
- Added `python smart_agent.py messages import --from-file ./workspace/incoming_message.md`, `messages inbox list`, `messages inbox show <message_id>`, and `messages inbox draft-reply <message_id>`.
- Manual imports are constrained to `./workspace`, block private Messages database paths such as `~/Library/Messages/chat.db`, label content `UNTRUSTED_MESSAGE`, store local records under `./workspace/messaging/inbound`, expose Lead Inbox candidate metadata, and create local `MessageDraft` replies only.
- No automatic send, no auto-reply, no background watcher, no Full Disk Access dependency, no real Gmail/Telegram/Apple Messages provider read, no CRM sync, and no memory write was added.
- Validation passed: targeted incoming message tests 7 passed; focused messaging/lead tests 49 passed; connector-status regression tests 11 passed; docs/command validation tests 27 passed; full suite 787 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 290 commands.

- Messages draft/handoff workflow v1 completed on `checkpoint/large-working-tree-20260523`.
- Added `python smart_agent.py messages draft --to ... --body ...` for local manual-handoff draft creation through brokered `messaging.draft.create`.
- Updated `messages draft-from-text` to store a local draft record under `./workspace/messaging/drafts/` and include draft-id handoff next steps while preserving the existing Action Center save/copy path.
- Added `python smart_agent.py messages handoff <draft_id>` to create reviewed save/copy handoff Action Center items for an existing local draft.
- Added draft-id execution ergonomics for `messages save-draft <draft_id>` and `messages copy-draft <draft_id>`; they execute only when a matching approved Action Center item exists and otherwise return approval instructions.
- Added brokered `messages.draft_from_lead` and `messages.open_handoff_instructions`; both are no-send, no-memory, ToolBroker-audited handoff helpers.
- No automatic send, Messages database access, Full Disk Access dependency, bulk sending, or memory write was added.
- Validation passed: targeted Messages safe handoff tests 16 passed; focused messaging/lead/probe tests 50 passed; full suite 780 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 286 commands; command/dogfood validation tests 16 passed; prompt audit clean with `INCOMING-MESSAGE-STRATEGY` next.

- macOS Messages automation feasibility probe completed on `checkpoint/large-working-tree-20260523`.
- Added `agent/messaging/macos_probe.py` for platform detection, standard Messages.app detection, harmless AppleScript app id/version metadata checks, permission-denied interpretation, structured result serialization, and connector-status metadata.
- Added brokered `messages.probe` and `python smart_agent.py messages probe` / `messages probe --explain-permissions`.
- Live local CLI smoke returned only app metadata, wrote `data/macos_messages_probe.json`, and audited the probe; it did not read `~/Library/Messages`, request Full Disk Access, inspect account status, read message content, press Send, or execute any send verb.
- `messages.probe` is a metadata-only `messages_probe` capability and is excluded from personal `messages` connector enablement; the personal `messages` connector remains disabled by default.
- Validation passed: targeted probe tests 8 passed; focused connector invariant tests 11 passed; docs validation 11 passed; full suite 776 passed, 2 skipped; startup policy ok; capability manifest ok; command registry ok with 281 commands; prompt audit clean with `MESSAGES-DRAFT-HANDOFF-WORKFLOW` next.

- iOS user-confirmed compose bridge v1 completed on `agent/overnight-2026-05-23`.
- Added `agent/messaging/ios_compose.py` and `agent/messaging/handoff_payloads.py` for local handoff payload creation, status inspection, and result recording.
- Added brokered `messaging.ios_compose.create_handoff`, `messaging.ios_compose.record_result`, and `messaging.ios_compose.status` capabilities.
- Added `python smart_agent.py messaging ios-compose-payload <draft_id>` and `python smart_agent.py messaging ios-compose-status <draft_id>`.
- Handoff payloads live under `./workspace/messaging/ios_compose/payloads`, include expiration, nonce, integrity hash, risk level, approval status, exact recipient, and exact body, and never send.
- Approved-action payload creation verifies the current draft fingerprint against the Action Center preview; compose-only mode remains user-confirmed through iOS compose UI.
- Result recording accepts `sent`, `queued`, `cancelled`, or `failed`; the agent only marks completion when iOS reports `sent` or `queued`, and expired payloads cannot record sent/queued.
- No iOS app project, deep-link transport, attachment support, silent send adapter, Messages database read, Full Disk Access request, bulk send path, or memory write was added.
- Targeted validation passed: iOS compose bridge tests 7 passed; focused messaging tests 24 passed.

- ORCH batch recovery completed on `checkpoint/large-working-tree-20260523`.
- Wrote `docs/runtime/ORCH_BATCH_RECOVERY_REPORT.md`.
- Confirmed ORCH-01 through ORCH-10 were already complete; no partial ORCH prompt and no not-started ORCH prompt remained.
- Corrected stale queued ORCH rows in `docs/PROMPT_LEDGER.md` to completed evidence rows.
- Updated `docs/PROMPT_AUDIT.md` so `MACOS-MESSAGES-PROBE` remains the next recommended prompt.
- Revalidated ORCH runtime controls without rerunning implementation: targeted runtime tests 31 passed; safe eval 21 passed, 0 failed, 8 skipped; full suite 766 passed, 2 skipped; startup policy, capability manifest, command registry, native skill, prompt pack, and prompt audit validations passed.
- No runtime behavior, personal-data access, send/write capability, background persistence, package install, commit, or push was added.

- Lead Inbox abstraction v1 completed on `agent/overnight-2026-05-23`.
- Added `agent/leads/` models, source registry, mock provider, classifier, and brokered lead tools.
- Added `python smart_agent.py leads list`, `leads show`, `leads classify`, `leads draft-response`, and `leads create-followup`.
- `leads list/classify/draft-response/create-followup` use synthetic mock records only; no Gmail, Telegram, Apple Messages for Business, personal iMessage, web-form, CRM, or provider adapter is contacted.
- `leads show` models future selected full lead reads and remains HIGH risk plus disabled by default.
- `leads draft-response` creates local `MessageDraft` files only and does not create send actions or send.
- `leads create-followup` creates pending Action Center `tasks.create` records only and does not create a real task.
- Lead text is `UNTRUSTED_MESSAGE`, instruction-like content is filtered from drafts, no lead content is written to memory by default, and future lead sends remain CRITICAL per-action/no-reuse.
- Validation passed: targeted Lead Inbox tests 9 passed; focused privacy/lead regression 10 passed; lead/command registry tests 14 passed; full suite 759 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 279 commands.

- Agent Runtime Orchestration v1 completed on `agent/overnight-2026-05-23`.
- Imported and split `prompts/packs/agent-runtime-orchestration-v1.promptpack.md` into ORCH-01 through ORCH-10 under `prompts/queued/` and placed them at the top of `docs/PROMPT_QUEUE.md`.
- Added runtime architecture and contract docs under `docs/runtime/` plus `docs/decisions/agent_runtime_orchestration.md`.
- Added lightweight `agent/runtime/` control-plane modules for models, state, service registry, feature flags, kernel/lifecycle, event bus, job queue, workflow runner, scheduler policy, and frontend bridge contract.
- Added metadata-only commands: `runtime status`, `runtime doctor`, `runtime services`, `runtime features`, `runtime health`, `jobs list`, `jobs show`, `workflows list`, `workflows run`, and `events tail`.
- Verified runtime commands do not call LM Studio, execute tools, read personal connectors, enable personal-data features, or start background persistence.
- Release gate passed: full suite 750 passed, 2 skipped; safe eval 21 passed, 0 failed, 8 skipped; startup policy ok; capability manifest validation ok; command registry validation ok; prompt pack validation ok; native skill validation ok; prompt audit clean.

- Python runtime and developer command standardization completed on `agent/overnight-2026-05-23`.
- Verified `smart_agent.py` still enforces Python 3.11+ before importing agent modules and updated the setup guidance to prefer Python 3.12 plus `./scripts/agent`.
- Updated `scripts/agent` to prefer `AI_AGENT_PYTHON`, then `./.venv/bin/python`, then `python3.12`, and otherwise print a clear setup error instead of falling through to Apple Python 3.9.
- Added `Makefile` shortcuts for `doctor`, `test`, `policy-check`, `command-check`, and no-tool `run`.
- Kept `pyproject.toml` at `requires-python = ">=3.11"` and made existing PDF runtime/test dependencies explicit (`pypdf`, `reportlab`) so fresh `.venv` installs include the packages required by the suite.
- Updated README setup docs, AGENTS runtime rules, command registry/test matrix, changelog, project state, and completion report.
- Validation passed: `.venv/bin/python --version` reported Python 3.12.13; startup ergonomics and command registry tests 8 passed; full `.venv` suite 719 passed, 2 skipped; bundled Codex Python full suite 729 passed, 1 skipped; `make policy-check` passed; `make command-check` passed; `LMSTUDIO_MODEL=qwopus3.6-35b-a3b-v1@q5_k_m make doctor` passed.
- No agent behavior, model/provider logic, ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, or personal-data defaults were changed.

- Message Safety Policy and Action Center integration completed on `agent/overnight-2026-05-23`.
- Added brokered `messaging.draft.create`, `messaging.draft.preview`, and `messaging.action.create_send` capabilities plus `python smart_agent.py messaging draft-create` and `messaging create-send-action`.
- Local drafts are stored only under `./workspace/messaging/drafts`; creating/replacing drafts invalidates stale pending/approved send actions for the same draft.
- Send proposals create CRITICAL `messaging.send_approved` Action Center records with exact local previews, explicit per-action approval, no approval reuse, rollback-impossible notes, allowlist status, and rate-limit status.
- No `messaging.send_approved` ToolBroker tool, send adapter, private Messages database access, Full Disk Access request, personal-data default enablement, bulk/group send support, attachment sending, hidden polling, or memory write was added.
- Validation passed: targeted messaging/action tests 17 passed; focused action/message/command docs tests 31 passed and 6 passed; full suite 729 passed, 1 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 259 commands; prompt audit reports `LEAD-INBOX-ABSTRACTION` next.

- Message Channel Abstraction v1 completed on `agent/overnight-2026-05-23`.
- Added `agent/messaging/` channel-neutral models, registry, validation, previews, and brokered channel/draft inspection tools.
- Added `messaging.channels`, `messaging.draft_show`, and `messaging.draft_validate` capabilities plus `python smart_agent.py messaging channels`, `messaging draft show`, and `messaging draft validate` CLI paths.
- All channels report `supports_send=false`; no `messaging.send` tool, real send adapter, Messages database read, Full Disk Access request, personal-data tool enablement, bulk/group send support, hidden polling, or memory write was added.
- Validation passed: targeted message-channel tests 9 passed; focused command/docs validation 23 passed; full suite 721 passed, 1 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 257 commands; prompt audit reports `MESSAGE-SAFETY-ACTION-CENTER` next.

- Apple Messaging / iMessage roadmap track planning addendum completed on `agent/overnight-2026-05-23`.
- Created decision records for Apple messaging architecture, iOS user-confirmed compose, macOS Messages automation strategy, and personal iMessage vs business messaging.
- Updated Apple Messages for Business planning to emphasize Apple/business/provider setup, API/webhook-style lead workflows, and approval-gated sends unless a future auto-response policy is explicitly approved.
- Created a messaging rollout plan covering message channel abstraction, safety policy, LeadInbox, iOS compose, macOS probe, draft/handoff, incoming strategy, approved send blockers, dogfood, and release gate.
- Updated roadmap, feature registry, feature maturity, risk register, threat model, changelog, prompt ledger/queue/audit, project state, and completion report.
- Validated with full tests, docs/prompt/command validation, command registry validation, startup policy validation, and capability manifest validation.
- No runtime message sending, Messages database access, broad Full Disk Access request, personal-data tool enablement, bulk sending, silent send path, memory write, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.

- Apple Ecosystem + Lead Response Track planning completed on `agent/overnight-2026-05-23`.
- Created decision records for Apple ecosystem architecture, consumer Messages strategy, Apple Messages for Business strategy, and LeadInbox abstraction.
- Created a lead response workflow spec covering rollout levels 0 through 5, with sends CRITICAL and auto-response deferred.
- Updated roadmap, feature registry, feature maturity, risk register, threat model, changelog, prompt tracking, project state, and completion report.
- Validated docs/policy status with feature maturity docs validation, startup policy validation, capability manifest validation, and command registry validation.
- No runtime connector, personal-data read, private Messages database access, Full Disk Access dependency, send path, background polling, memory write, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.

- Gmail and Telegram connector doctors completed on `agent/overnight-2026-05-23`.
- Added config-only `python smart_agent.py gmail doctor`, `python smart_agent.py gmail scopes`, `python smart_agent.py telegram doctor`, and `python smart_agent.py telegram status`.
- Gmail doctor validates env presence, token path metadata, configured scopes, broad/send-capable scope warnings, and disabled CRITICAL send status without reading inboxes or sending email.
- Telegram doctor validates bot-token presence, allowed/default chat-id metadata, missing chat-id warnings, and disabled CRITICAL send status without reading chats or sending messages.
- No full Gmail/Telegram connector, provider API call, token validation, inbox/chat read, send path enablement, memory write, personal-data tool enablement, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.
- `GMAIL-TELEGRAM-DOCTORS` was selected out of queue order by explicit user request; `APPLE-MESSAGING-ROADMAP` remains the next queued prompt.

- Cost-aware weather provider selector completed on `agent/overnight-2026-05-23`.
- Added action-aware weather auto selection: Open-Meteo for current/forecast, NOAA/NWS for U.S. alerts, and WeatherAPI only when configured and explicitly selected or allowed by paid-provider policy.
- Added optional WeatherAPI provider normalization for current, forecast, hourly, and alerts through the existing brokered weather tools.
- Added `python smart_agent.py weather providers`, `python smart_agent.py weather provider auto "Phoenix, AZ"`, `weather current --provider auto`, and `weather current --provider weatherapi`.
- Provider decisions are included in structured weather results and audit summaries; API keys are not returned or logged.
- Added mocked tests for auto current, auto alerts, WeatherAPI paid-default denial, explicit WeatherAPI, missing-key setup hints, provider-decision audit, no memory writes, secret redaction, and CLI provider commands.
- No WeatherAPI default-by-key behavior, system location inference, memory location storage, personal-data tool enablement, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.
- `WEATHER-PROVIDER-SELECTOR` was marked complete out of queue order by explicit user request; `APPLE-MESSAGING-ROADMAP` remains the next queued prompt.

- Optional SerpAPI fallback provider completed on `agent/overnight-2026-05-23`.
- Added `web.search.serpapi` as a brokered, LOW-risk, rate-limited capability with cost-policy checks.
- Added explicit CLI support for `python smart_agent.py web search "query" --provider serpapi` and `python smart_agent.py research "query" --provider serpapi`.
- Added SerpAPI result normalization to the existing search result schema with `UNTRUSTED_WEB` labels.
- Added missing-key, paid-API disabled, timeout/API error, no-auto-default, redaction, audit, and research-routing tests using mocks only.
- Updated command registry/test matrix, README, connector cost docs, risk/threat/test/release docs, feature registry, feature maturity, roadmap, changelog, prompt ledger/queue/audit, and completion report.
- No direct Google scraping, search-history memory storage, default SerpAPI selection, API-key exposure, personal-data tool enablement, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.
- Free-first Web Acquisition Layer v1 completed on `agent/overnight-2026-05-23`.
- Added brokered `web.robots`, `web.sitemap`, `web.feed`, `web.acquire_url`, and `web.acquire` tools and CLI commands.
- Added public robots.txt checks, sitemap parsing, RSS/Atom item extraction, TTL acquisition cache, robots-aware direct public URL acquisition, blocked/CAPTCHA page unavailability, untrusted-content wrapping, and provider ladder skip reporting.
- Added config placeholders `WEB_ACQUISITION_CACHE_ENABLED` and `WEB_ACQUISITION_CACHE_TTL_SECONDS`.
- Updated command registry/test matrix, README, connector cost docs, risk/threat/test/release docs, feature registry, feature maturity, roadmap, changelog, prompt ledger/queue/audit, and completion report.
- No CAPTCHA/anti-bot bypass, logged-in scraping, browser profile/cookie/session access, paid provider defaulting, search history storage, personal-data tool enablement, ToolBroker bypass, PolicyEngine weakening, ApprovalManager bypass, or AuditLogger bypass was added.
- `FREE-FIRST-WEB-ACQUISITION` was marked complete out of queue order by explicit user request; `APPLE-MESSAGING-ROADMAP` remains the next queued prompt.

- Prompt Tracker Maturity Track completed on `agent/overnight-2026-05-23`.
- PTM-01 was repaired by adding prompt tracker audit/gap artifacts and then marked complete.
- PTM-02 through PTM-10 were executed sequentially and marked complete with targeted test/docs evidence.
- Added prompt evidence classification, conservative recovery commands, embedded-delimiter prompt pack parsing, prompt tracker dogfood suites, prompt tracker evals, and PTM release-gate docs.
- At that point `prompts audit` reported zero active prompts and `APPLE-MESSAGING-ROADMAP` as the next queued prompt; after the Apple track, current prompt tracking now points to `MESSAGE-CHANNEL-ABSTRACTION`.
- No prompt body was executed automatically; no personal-data tool was enabled; no ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger behavior was weakened.

- Secret/config doctor completed on `agent/overnight-2026-05-23`.
- Added redacted credential/config presence checks for SerpAPI, WeatherAPI, Gmail, and Telegram.
- Added `python smart_agent.py secrets doctor`, `python smart_agent.py secrets status`, and connector status entries for `serpapi`, `weatherapi`, `gmail`, and `telegram`.
- The doctor warns on tracked `.env`, repo-local token paths, and secret-looking docs/tests/config values while never printing raw secrets.
- SerpAPI and WeatherAPI remain non-default paid/quota-limited providers unless cost policy explicitly allows them.
- No provider API calls, Gmail inbox reads, Telegram sends, personal-data access, memory writes, ToolBroker bypasses, PolicyEngine weakening, ApprovalManager bypasses, or AuditLogger bypasses were added.
- `SECRET-CONFIG-DOCTOR` was marked complete out of prompt queue order by explicit user request; `PTM-01` remains the next recommended prompt.

- Cost-aware provider policy completed on `agent/overnight-2026-05-23`.
- Added reusable `agent/connectors/cost_policy.py` with `ProviderCostConfig`, provider candidates, free-first selection, paid/quota gates, setup hints, redacted decision payloads, and `provider.select` audit helper.
- Added provider ordering docs for web/search, weather, and personal communications.
- Added config defaults: `PROVIDER_COST_MODE`, `ALLOW_PAID_APIS`, `MAX_PAID_API_CALLS_PER_DAY`, `SEARCH_DEFAULT_PROVIDER`, and `WEATHER_DEFAULT_PROVIDER`.
- Added focused tests for no-key provider preference, paid-provider denial, SerpAPI/WeatherAPI gates, provider-decision audit events, redaction, and missing-provider setup hints.
- No new provider API calls, personal-data tools, sends, writes, policy weakening, ToolBroker bypass, ApprovalManager bypass, or AuditLogger bypass were added.
- `COST-AWARE-PROVIDER-POLICY` was marked complete out of prompt queue order by explicit user request; `PTM-01` remains the next recommended prompt.

- Prompt Tracker Maturity prompt pack imported on `agent/overnight-2026-05-23`.
- Source pack: `prompts/packs/prompt-tracker-maturity-v1.promptpack.md`.
- Original pack copy created at `prompts/packs/prompt-tracker-maturity-v1.md`.
- Created queued prompt files `prompts/queued/PTM-01.md` through `prompts/queued/PTM-10.md`.
- Verified the split prompt body text for all 10 PTM prompts exactly matches the original pack body sections.
- Updated `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and `docs/PROMPT_AUDIT.md`; PTM-01 through PTM-10 are now top-of-queue.
- Set `next_prompt_id` to `PTM-01`; no PTM prompt was executed.
- Existing prompt-pack validator rejected the pack because PTM-03 includes example delimiter text by design, so the pack was split manually with PTM-specific delimiters.
- `prompts next` returns `PTM-01`.
- Focused prompt/maturity/command validation passed: 19 passed in 0.23s.
- Full suite passed: 663 passed, 1 skipped in 20.90s.
- Startup policy validation passed: ok.
- Capability manifest validation passed: ok.
- Command registry/docs validation passed: 228 commands, no problems.

- Live Dogfood + Session Review release gate completed on `agent/overnight-2026-05-23`.
- Validation session `sess_20260523T182508Z_abdad880` captured safe command `cmd_d205fdc403f7` through `session run -- setup`.
- Feedback `fb_11c10fcb408c` attached to the captured command and redacted a fake secret as `<REDACTED_SECRET>`.
- `session review --last --create-bugs` created local redacted bug `BUG-0002`.
- `bugs create-regression BUG-0002` created skipped redacted scaffold `tests/regressions/test_bug_0002.py`.
- `quality status`, `quality bugs`, and `quality regressions` reported the validation session, open bugs, and regression coverage.
- Safe dogfood `all_safe --dry-run` returned status ok with 8 skipped commands by design.
- Redaction search found no raw fake token in generated session/review/bug/regression artifacts.
- Policy invariant scan passed: no personal-data capabilities enabled by default, no HIGH capability missing approval, and no CRITICAL capability allows approval reuse.
- Focused docs/dogfood/bug/quality validation passed: 45 passed in 0.51s.
- Full suite passed: 663 passed, 1 skipped in 20.78s.
- Startup policy validation passed: ok.
- Capability manifest validation passed: ok.
- Command registry/docs validation passed: 228 commands, no problems.
- Native skill validation passed: 3 manifests valid.

- Product Quality Dashboard v1 completed on `agent/overnight-2026-05-23`.
- Added `agent/ui/product_quality.py` with read-only quality summaries over redacted sessions, feedback, bugs, regression links, eval reports, full-test status, feature maturity, dogfood recommendations, and release-gate docs.
- Added `python smart_agent.py quality status`, `quality sessions`, `quality bugs`, `quality regressions`, `quality features`, and `quality next`.
- Quality dashboard reads local metadata/log files only; it does not execute tools, access personal connectors, grant approvals, write memory, or expose raw personal data.
- Focused Product Quality Dashboard tests passed: 7 passed in 0.14s.
- Focused quality/command/prompt/maturity validation passed: 26 passed in 0.26s.
- Command registry validation passed: 228 commands, no problems.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Diff whitespace check passed.
- Full suite passed: 663 passed in 20.68s.

- Live Test Runbook and Daily Dogfood Workflow completed on `agent/overnight-2026-05-23`.
- Added `agent/dogfood/planner.py` with daily/weekly dogfood plans, checklist output, and next-step recommendations based on latest redacted session metadata plus feature-maturity notes.
- Added `python smart_agent.py dogfood plan`, `python smart_agent.py dogfood next`, and `python smart_agent.py dogfood checklist`.
- Added `docs/dogfood/LIVE_TEST_RUNBOOK.md`, `docs/dogfood/DAILY_DOGFOOD_CHECKLIST.md`, `docs/dogfood/WEEKLY_RELEASE_CHECK.md`, and `docs/templates/dogfood_session_notes.md`.
- Dogfood planning commands are metadata-only; they do not run suites, access personal data, grant approvals, send messages, or write memory.
- Focused dogfood tests passed: 11 passed in 0.44s.
- Focused dogfood/command/prompt/maturity validation passed: 30 passed in 0.45s.
- Command registry validation passed: 222 commands, no problems.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Diff whitespace check passed.
- Full suite passed: 656 passed in 21.58s.

- Session Review and Bug Generator completed on `agent/overnight-2026-05-23`.
- Added `agent/session_logs/review.py` with redacted session review, optional local bug creation, stable `BUG-0001` style ids, severity classification, and audit events.
- Added `python smart_agent.py session review <session_id>`, `python smart_agent.py session review --last`, `python smart_agent.py session review --last --create-bugs`, `python smart_agent.py bugs list`, `python smart_agent.py bugs show <bug_id>`, and `python smart_agent.py bugs export`.
- Created `docs/BUG_TRIAGE.md`, `reports/session_reviews/.gitkeep`, and `bugs/.gitkeep`; generated review/bug artifacts are ignored by git.
- Review reads redacted session previews and feedback only, does not access personal connectors, sends no data externally, writes no memory, and does not fix bugs automatically.
- Focused session review tests passed: 21 passed in 1.19s.
- Focused session/command registry tests passed: 26 passed in 1.14s.
- Focused session/command/prompt/maturity validation passed: 40 passed in 1.23s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Full suite passed: 645 passed in 20.13s.
- Command registry validation passed: 215 commands, no problems.
- Final focused docs/registry validation after tracking updates passed: 40 passed in 1.20s; command registry ok; `git diff --check` passed.

- Manual Dogfood Command Suites completed on `agent/overnight-2026-05-23`.
- Added `agent/dogfood/` with suite loading, validation, command parsing, dry-run preview, failure-continuing runner, expected-exit handling, and optional active-session capture.
- Added `python smart_agent.py dogfood list/show/run`, including `--dry-run` and `--session`.
- Added curated suites under `dogfood_suites/`: `core`, `weather`, `web`, `workspace_files`, `memory`, `approvals`, `native_skills`, `personal_dry_run`, and `all_safe`.
- Added synthetic dogfood fixtures under `workspace/dogfood` and `workspace/skills`.
- Added `docs/dogfood/DOGFOOD_GUIDE.md` and `docs/dogfood/COMMAND_SUITES.md`.
- Updated README, command registry docs, feature registry, maturity, roadmap, prompt tracking, changelog, and completion report.
- Focused dogfood tests passed: 8 passed in 0.30s.

- Live Session Logging and Replay completed on `agent/overnight-2026-05-23`.
- Added `agent/session_logs/` with models, store, recorder, redaction, replay, and reviewer helpers.
- Added `python smart_agent.py session start/status/run/end/list/show/replay/export/last`.
- Added `docs/SESSION_LOGGING.md` and `reports/sessions/.gitkeep`; raw session logs are gitignored.
- Added focused tests for lifecycle, replay, command run capture, redaction, visible audit-id linking, large output storage, malformed file handling, gitignore protection, and CLI dispatch.
- Updated README, command registry docs, feature registry, maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, changelog, and completion report.
- Focused session logging and command registry tests passed: 15 passed in 0.48s.
- Focused session/docs/prompt/command validation passed: 29 passed in 0.55s.
- Full suite passed: 626 passed in 19.91s on the final run.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Command registry validation passed: 197 commands, no problems.
- Diff whitespace check passed.

- Approved bounded overnight safe-mode run completed on `agent/overnight-2026-05-23`.
- Completed two low-risk cycles: tracking sync for `OVERNIGHT-SAFE-6H` and stricter overnight report-template validation.
- Created `reports/overnight/overnight_2026-05-23.md`.
- Updated prompt queue, prompt ledger, prompt audit, project state, roadmap, feature maturity, feature registry, changelog, and completion report.
- Focused self-improvement and docs validation passed: 47 passed in 3.04s after adjusting active-prompt validation to count unique prompt IDs.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Command registry validation passed: 189 commands, no problems.
- Full suite passed: 616 passed in 18.63s on the final run.
- No approval gate was hit after the user's explicit bounded-run approval.
- No personal-data access, send/write path, package install, external script, unexpected network access, background persistence, policy weakening, audit disabling, or commit was added.

- Full release gate and feature maturity review completed for this batch.
- Full suite passed: 616 passed in 18.31s after docs updates.
- Safe eval suite passed: 21 passed, 0 failed, 8 skipped. Skips were live LM Studio checks missing `LMSTUDIO_MODEL` and personal-data evals skipped by default.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Command registry validation passed: 189 commands, no problems.
- Native skill validation passed: 3 manifests valid.
- Unknown tool denial check passed through `ToolBroker`.
- Personal-data connector/default-enabled check passed with `tasks.draft_create` treated as non-personal Action Center draft creation.
- HIGH approval manifest check passed.
- CRITICAL per-action/no-reuse manifest check passed.
- ToolBroker path scan found the registered tool handler call inside `ToolBroker`; status/preflight paths only use registry metadata.
- Feature roadmap row `Full release gate + maturity review` is now complete.
- Updated release-gate evidence in feature maturity, feature registry, project state, prompt tracking, changelog, and completion report.
- No runtime feature, connector, policy relaxation, send/write path, personal-data enablement, memory behavior, or background automation was added.
- No commit was created because the worktree already contains broad pre-existing feature-batch changes and this release-gate sync is not a clean standalone commit boundary.
- Overnight self-improvement safe-mode runbook completed in focused and full tests.
- Added `docs/SELF_IMPROVEMENT_OVERNIGHT_RUNBOOK.md`, `docs/templates/overnight_report_template.md`, and `reports/overnight/.gitkeep`.
- Added `python smart_agent.py improve overnight-plan`.
- The planner reads tracking docs through brokered `filesystem.read`, ranks safe docs/tests/hardening/evals candidates, excludes HIGH/CRITICAL and personal-data work, writes no memory, creates no branch, starts no schedule/background runner, and commits nothing.
- `OVERNIGHT-SAFE-6H` completed for the 2026-05-23 approved bounded run; future overnight runs require separate explicit user approval.
- Updated README, command registry docs, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, project state, changelog, and completion report.
- Focused self-improvement tests passed: 28 passed in 3.37s.
- Focused prompt/maturity/command docs validation passed: 19 passed in 0.19s.
- Full suite passed: 616 passed in 18.51s.
- Command registry validation passed: 189 commands, no missing records.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Personal-data connector/default-enabled check passed with `tasks.draft_create` treated as non-personal Action Center draft creation.
- HIGH/CRITICAL approval manifest check passed.
- Diff whitespace check passed.
- Controlled self-improvement implementation loop v1 commit-action checkpoint completed in focused and full tests.
- Added `python smart_agent.py improve create-action-for-commit`.
- The new checkpoint runs self-improvement tests through brokered `code.run_tests`, generates diff through brokered `git.diff`, and creates only a pending Action Center `self_improvement.commit` record.
- The checkpoint refuses to create a commit action when tests fail, never executes `git.commit`, writes no memory, and requires later Action Center approval plus `improve commit --from-action <action_id>` for execution.
- Updated README, command registry docs, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, project state, changelog, and completion report.
- Focused self-improvement tests passed: 23 passed in 3.18s.
- Full suite passed: 611 passed in 19.77s.
- Command registry validation passed: 188 commands, no missing records.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Personal connector default-disabled check passed.
- HIGH/CRITICAL approval manifest check passed.
- Diff whitespace check passed.
- Scheduler / Automation v1 backup_create follow-up completed in focused and full tests.
- Added `backup_create` to the supported scheduler workflow allowlist and CLI `--workflow` choices.
- Scheduled `backup_create` calls `backup.create` through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Scheduled backups are redacted-only; unredacted backup args are rejected before any backup tool call.
- Scheduled backup output records `personal_connectors_read=false`, `memory_written=false`, `critical_actions_executed=false`, and `toolbroker_used=true`.
- Updated scheduler docs, README, command registry docs, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, prompt tracking, project state, and completion report.
- Focused scheduler tests passed: 9 passed in 0.62s.
- Full suite passed: 609 passed in 19.59s.
- Focused docs validation after tracking updates passed: 19 passed in 0.19s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (77 capabilities).
- Command registry validation passed: 187 commands, no missing records.
- Personal-data default-disabled check passed.
- HIGH/CRITICAL approval manifest check passed.
- Scheduled backup_create CLI smoke passed using a temporary schedule store/audit log and redacted backup directory.
- Diff whitespace check passed.
- Model-router benchmark and prompt quality evals completed in focused and full tests.
- Added `models list`, `models benchmark --safe`, `router eval`, `prompts eval`, and `prompts report`.
- Added fixture-backed model/router/prompt-quality cases covering normal no-tool chat, weather, web/current-info, URL/document, memory, personal-data request, send/approval-gate, prompt-injection, and answer-quality guardrails.
- Reports write to `docs/PROMPT_QUALITY_REPORT.md`, `logs/model_router_prompt_quality.json`, and `reports/evals/`.
- Focused model/router/eval tests passed: 26 passed in 1.22s.
- Full suite passed: 607 passed in 18.68s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok, 187 commands, no problems.
- Diff whitespace check passed.
- Backup / Restore / Migration v1 completed in focused and full tests.
- Added brokered `backup.create`, `backup.list`, `backup.inspect`, `backup.verify`, `backup.export`, and `backup.restore` tools.
- Added CLI commands `backup create/list/inspect/verify/export --redacted/restore` through the direct CLI dispatch layer while still constructing `PolicyEngine`, `ToolBroker`, `ApprovalManager`, and `AuditLogger`.
- Backups write redacted local archive directories with `manifest.json`, per-file hashes, an integrity hash, excluded-secret records, and restore limitations.
- Backup scope includes config/docs/tracking/native-skill files plus redacted memory/action metadata; captures and audit metadata are optional.
- `.env` and key/certificate files are excluded; secret-like values are redacted from copied text.
- `backup.restore` is HIGH risk, approval-required, denied safely in non-interactive mode, verifies hashes first, creates pre-restore copies where possible, and blocks backed-up capability manifests that would weaken policy or enable personal connectors.
- Added backup/restore docs, command registry entries, feature registry/maturity updates, risk register and threat model entries, and prompt ledger/queue/audit records.
- Focused backup/policy/packaging tests passed: 46 passed in 1.87s.
- Full suite passed: 598 passed in 17.30s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok, 182 commands, no problems.
- Diff whitespace check passed.
- Local startup ergonomics completed in focused and full tests.
- Added a Python 3.11+ guard at the top of `smart_agent.py` before agent module imports.
- Added `scripts/agent`, an executable local launcher that prefers `AI_AGENT_PYTHON`, `./.venv/bin/python`, the bundled Codex Python 3.12 runtime, and then system `python3` only if it is Python 3.11+.
- Documented `.venv` setup, `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`, and `curl http://localhost:1234/v1/models` model-id discovery.
- Added command registry entry `CMD-CORE-006` for `./scripts/agent <command>`.
- Targeted startup ergonomics and command registry tests passed: 8 passed in 0.40s.
- Full suite passed: 590 passed in 16.86s.
- Focused prompt/maturity/command docs validation passed: 19 passed in 0.19s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok, 177 commands, no problems.
- Apple Python 3.9 smoke `python3 smart_agent.py setup` printed the Python 3.11+ setup instructions instead of crashing.
- `./scripts/agent doctor` used Python 3.12 and reported missing `LMSTUDIO_MODEL` clearly while leaving model prompts/tools untouched.
- Diff whitespace check passed.
- Privacy Center / Data Inventory v1 completed in focused and full tests.
- Added `privacy status`, `privacy inventory`, `privacy export`, `privacy delete-memory`, `privacy audit-summary`, and `privacy permissions` CLI commands.
- Privacy inventory uses metadata/status only and does not read personal connector data.
- Redacted privacy export includes memory/capture previews, pending actions, approvals, audit summary, cache metadata, and deletion limitations without revealing secrets.
- Memory deletion requires explicit `--confirm DELETE-MEMORY` and then routes through brokered `memory.clear`; no real memory deletion was run in this release gate outside isolated tests.
- Privacy status distinguishes enabled non-personal URL/task-draft workflows from disabled-by-default personal connector reads.
- Targeted Privacy Center tests passed: 7 passed in 1.07s.
- Full suite passed: 587 passed in 16.95s.
- Focused prompt/maturity/command docs validation passed: 19 passed in 0.19s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok, 176 commands, no problems.
- CLI smoke passed for `privacy status`; unconfirmed `privacy delete-memory` returned the expected confirmation-required error.
- Diff whitespace check passed.
- Notes / Knowledge Capture trusted file marker completed in focused and full tests.
- Added explicit `--trusted-user` support for `capture from-file` so user-authored workspace files can be labeled `TRUSTED_USER`; default file captures remain `UNTRUSTED_DOCUMENT`.
- Capture file reads still go through brokered `filesystem.read`, capture writes still go through brokered `filesystem.write`, URL captures still go through brokered `web.fetch_url`, and memory promotion still goes through brokered `memory.store`.
- No Apple Notes integration, private app database scraping, personal connector access, or automatic memory storage was added.
- Targeted Knowledge Capture tests passed: 11 passed in 0.83s.
- Full suite passed: 580 passed in 15.56s.
- Focused prompt/maturity/command docs validation passed: 19 passed in 0.18s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok, 170 commands, no problems.
- Diff whitespace check passed.
- Browser selected URL / web clipping capability compatibility completed in focused and full tests.
- Added canonical capability tracking for `browser.read_url`, `browser.summarize_url`, and disabled `browser.selected_tab`, while retaining legacy selected-URL aliases.
- Selected-tab CLI stub now audits the disabled `browser.selected_tab` capability.
- Explicit URL read/summarize still fetch through brokered `web.fetch_url`; URL clipping still writes through brokered `filesystem.write`.
- Focused browser/connector/manifest tests passed: 20 passed in 1.55s.
- Full suite passed: 578 passed in 15.94s.
- Focused prompt/maturity/command docs validation passed: 19 passed in 0.20s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no problems.
- Direct browser-access scan found expected docs/tests/stub references only; no history/cookie/session/password/profile reader was added.
- `git diff --check` passed.
- Messages safe handoff v1 Action Center verification hardening completed in focused and full tests.
- Low-level `messages.save_draft` and `messages.copy_draft` now reject direct broker execution unless Action Center verifies the matching approved action id.
- Message save/copy tool submissions must match the approved reviewed draft before workspace write or clipboard handoff can be reached.
- Focused Messages safe handoff tests passed: 12 passed in 0.52s.
- Focused Messages plus docs/prompt validation passed: 26 passed in 0.60s.
- Focused command registry/release-gate tests passed: 12 passed in 0.20s.
- Full suite passed: 577 passed in 15.19s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Docs validation passed: 9 passed in 0.01s.
- Final docs/prompt validation after tracking edits passed: 14 passed in 0.18s.
- Diff whitespace check passed.
- Email approved send v1 Action Center verification hardening completed in focused and full tests.
- Low-level `email.send_approved` now rejects direct broker execution unless Action Center verifies the matching approved action id.
- Email send tool submissions must match the approved reviewed draft before mock/no-provider execution can be reached.
- `execute_email_send_action()` injects the approved `action_id` only after the Action Center record is approved and before brokered execution.
- Focused email tests passed: 12 passed in 0.66s.
- Focused email/write/release-gate tests passed: 26 passed in 0.73s.
- Focused email and command-registry tests passed: 17 passed in 0.70s.
- Focused tracking/maturity/command docs validation passed: 19 passed in 0.19s.
- Full suite passed after docs updates: 574 passed in 14.93s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Diff whitespace check passed.
- Contacts approved edits v1 Action Center verification hardening completed in focused and full tests.
- Low-level `contacts.update_selected` and `contacts.create` tools now reject direct broker execution unless Action Center verifies the matching approved action id.
- Contact write tool submissions must match the approved Action Center preview before the stub is reached.
- `execute_contact_action()` injects the approved `action_id` only after the Action Center record is approved and before brokered execution.
- Focused contacts tests passed after final code hardening: 13 passed in 0.64s.
- Focused contacts and command-registry tests passed: 18 passed in 0.69s.
- Full suite passed after final code hardening: 573 passed in 15.06s.
- Focused tracking/maturity/command docs validation passed: 19 passed in 0.18s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Diff whitespace check passed.
- Calendar approved writes v1 Action Center verification hardening completed in focused tests.
- Low-level `calendar.create_event`, `calendar.update_event`, and `calendar.delete_event` tools now reject direct broker execution unless Action Center verifies the matching approved action id.
- `execute_calendar_action()` injects the approved `action_id` only after the Action Center record is approved and before brokered execution.
- Focused calendar/write/release-gate tests passed: 25 passed in 0.75s.
- Full suite passed: 571 passed in 14.99s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Diff whitespace check passed.
- Tasks / Reminders connector v1 brokered draft-create pass completed.
- Added `tasks.draft_create` as a brokered MEDIUM-risk Action Center-scoped capability.
- Updated `tasks draft-create` CLI to route through ToolBroker before creating a pending Action Center `tasks.create` record.
- Confirmed `tasks.draft_create` does not access a task provider, does not create a real reminder, does not write memory, and does not enable personal task provider access by default.
- Focused Tasks/Command Registry tests passed: 16 passed in 0.91s.
- Full suite passed: 570 passed in 14.74s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Diff whitespace check passed.
- Unified Action Center v1 hardening pass completed.
- Added regression coverage for required `tool` metadata, no direct Action Center execution after approval, export minimization, and lifecycle audit minimization.
- `actions export` and Action Center lifecycle audit records now minimize sensitive action bodies/drafts while exact secret-redacted local previews remain available for user approval review.
- Focused Action Center tests passed: 14 passed in 0.79s.
- Full suite passed: 569 passed in 14.04s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 170 commands, no missing records.
- Diff whitespace check passed.
- Golden Eval Suite and quality scorecards completed for local tested v1 scope.
- Added data-backed eval cases under `eval_cases/` for routing, policy, ToolBroker, prompt injection, and workflow dry-runs.
- Added `eval run --routing`, `--policy`, `--tools`, `--workflows`, `--prompt-injection`, and `--lmstudio-live`.
- Eval reports now include category scorecards, `quality_score`, latest JSON at `logs/eval_results.json`, and per-run JSON under `reports/evals/`.
- Personal-data evals remain skipped by default; live LM Studio remains opt-in; tool evals use `ToolBroker`.
- Focused tests passed: `tests/test_eval_harness.py tests/test_command_registry.py` reported 17 passed in 0.85s.
- Release-gate sync before the next feature set completed.
- Full suite passed: 561 passed in 13.51s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 164 commands, no missing records.
- Native skill validation passed: 3 manifests valid.
- Prompt audit passed at that time: 90 prompt records, 59 complete, 28 queued, 3 blocked, next `SESSION-LOGGING-REPLAY`.
- Manifest safety audit passed: no personal-data capabilities enabled by default; HIGH actions require approval; CRITICAL actions require per-action approval and no approval reuse.
- `docs/FEATURE_ROADMAP.md` now explicitly tracks Native Skills, Next Product Feature, and Overnight Self-Improvement tracks.
- PDF workspace native skill v1 implemented in the working tree.
- Added `agent/tools/documents/pdf.py`.
- Added `documents.pdf.read`, `documents.pdf.extract_text`, `documents.pdf.extract_tables`, and `documents.pdf.summarize`.
- Added `python smart_agent.py pdf info`, `pdf extract-text`, `pdf summarize`, and `pdf extract-tables`.
- Added built-in native skill manifest `native_skills/pdf_workspace.yaml`.
- Added `docs/native_skills/pdf.md`.
- PDF tools resolve paths through approved workspace roots, block traversal/outside paths, enforce file/page/text limits, and label content `UNTRUSTED_DOCUMENT`.
- PDF tools use existing Python dependency `pypdf`; no external binaries, OCR, embedded actions/scripts, split/merge, generated PDF writes, or memory writes are enabled in v1.
- PDF focused tests passed: 10 passed in 0.69s.
- Focused docs/command/prompt/PDF validation passed: 29 passed in 0.75s.
- Full suite passed: 561 passed in 12.77s.
- Startup policy validation passed: startup policy ok.
- Diff whitespace check passed.
- Native skill manifest validation passed: 3 manifests valid.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 164 commands, no missing records.
- Native skill finder v1 implemented in the working tree.
- Added `agent/native_skills/finder.py`.
- Added brokered `native_skills.find_skill` capability and `python smart_agent.py skills find "<query>"`.
- Added built-in metadata-only manifest `native_skills/native_skill_finder.yaml`.
- Finder searches local native skill manifests, `docs/native_skills` candidate docs, feature registry, and maturity tracker.
- Finder reports matching native skills/candidates, maturity level, readiness score, implementation status, safe-to-use-now status, required approvals, required capabilities, and next work needed.
- Finder executes through `ToolBroker`, `PolicyEngine`, and `AuditLogger`; files read are audited.
- Finder does not browse external marketplaces, install skills, execute external code, grant permissions, or write memory.
- Native skill finder focused tests passed: 5 passed in 0.15s.
- Focused docs/registry/prompt validation passed: 30 passed in 0.29s.
- Full suite passed: 551 passed in 12.26s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: 161 commands, no missing records.
- Native skill manifest and discovery loader implemented in the working tree.
- Added `agent/native_skills/manifest.py`, `registry.py`, `loader.py`, `validator.py`, and `models.py`.
- Added built-in metadata-only manifest `native_skills/native_skill_vetter.yaml`.
- Added `python smart_agent.py skills list`, `skills show <skill_id>`, `skills validate`, and `skills doctor`.
- Manifest loader reads metadata only and never executes scripts, imports external code, installs marketplace skills, grants permissions, enables tools, or writes memory.
- Manifest validation rejects unknown required/allowed capabilities, missing risk/trust/memory/audit fields, ToolBroker-bypass language, executable manifest fields, personal-data manifests enabled by default, and CRITICAL manifests without `approval_required: per_action`.
- Native skill registry status is included in runtime doctor and dashboard metadata.
- Native skill manifest focused tests passed: 6 passed in 0.15s.
- Manifest CLI smoke passed: `skills validate` and `skills show native_skill_vetter` returned `status=ok`.
- Native skill vetter v1 implemented and locally validated in focused tests.
- Added `native_skills.vet_skill_file`, `native_skills.vet_skill_folder`, and `native_skills.score_candidate` capabilities.
- Added `python smart_agent.py skills vet`, `skills vet-folder`, and `skills score` CLI commands.
- Vetter reads only approved workspace paths, treats candidate files as `UNTRUSTED_DOCUMENT`, parses `SKILL.md` frontmatter, flags scripts, shell commands, network calls, package installs, secrets, filesystem escapes, personal-data access, browser cookie/session access, prompt-injection language, approval-bypass language, opaque binaries, and missing licenses.
- Vetter never executes scripts, installs dependencies, grants permissions, enables skills, or stores skill content in memory by default.
- Vetter execution goes through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.
- Focused native skill vetter tests passed: 10 passed in 0.59s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok.
- Command registry validation passed: status ok.
- Skill marketplace survey and native-candidate shortlist completed.
- Created `docs/native_skills/SKILL_MARKETPLACE_SURVEY.md`.
- Created `docs/native_skills/NATIVE_CANDIDATE_MATRIX.md`.
- Created `docs/native_skills/TOP_NATIVE_SKILL_SHORTLIST.md`.
- Updated `docs/native_skills/NATIVE_SKILL_CANDIDATES.md` with shortlisted native candidates.
- Surveyed OpenClaw/ClawHub/LobeHub-style category signals as untrusted web research only.
- No external skills were installed, imported, run, cloned, or executed.
- No runtime capabilities were added.
- High-risk categories such as email send, message send, browser automation, cloud deployment, self-evolution, and unrestricted app automation were marked later/defer.
- Recommended first implementation is `NATIVE-SKILL-VETTER`.
- Focused docs/prompt validation passed: 14 passed in 0.15s.
- Full suite passed: 530 passed in 11.22s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Native Skills Program foundation completed.
- Created `docs/native_skills/NATIVE_SKILLS_PROGRAM.md`.
- Created `docs/native_skills/SKILL_INTAKE_PROCESS.md`.
- Created `docs/native_skills/NATIVE_SKILL_CRITERIA.md`.
- Created `docs/native_skills/NATIVE_SKILL_CANDIDATES.md`.
- Created `docs/native_skills/SKILL_RISK_MODEL.md`.
- Created `docs/templates/native_skill_record_template.md`.
- Defined native skills as reviewed local versioned workflows mapped to existing `ToolBroker` capabilities.
- Defined non-goals: no unreviewed external scripts, direct tool access, hidden network access, permission bypass, automatic installation, approval bypass, or replacement for ToolBroker tools.
- Added native skill categories, maturity states, selection criteria, disqualification criteria, risk model, and candidate registry.
- Added docs validation for required native skill files and safety-boundary language.
- Updated feature registry, feature maturity, feature roadmap, risk register, threat model, test plan, changelog, prompt tracking, project state, and completion report.
- No external skills were installed, imported, run, or executed.
- No runtime capabilities were added.
- Focused docs/prompt validation passed: 14 passed in 0.17s.
- Full suite passed: 530 passed in 10.68s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Full feature maturity review and release gate completed.
- Full test suite passed: 529 passed in 10.23s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Command registry validation passed: 154 commands, no missing registry/matrix ids, no invalid records.
- Safe eval suite passed: 9 passed, 0 failed, 8 skipped by design. LM Studio live evals skipped because `LMSTUDIO_MODEL` was not set; personal-data evals skipped by default.
- Release gate found and fixed Open-Meteo live geocoding for comma-separated U.S. city/state inputs such as `Phoenix, AZ`; added a mocked regression test.
- ToolBroker-bypass scan found provider calls contained inside registered tool providers/workflow broker paths, with user-facing workflows still using `ToolBroker`.
- Personal-data tools remain disabled by default.
- HIGH actions remain approval-required.
- CRITICAL actions remain per-action approval only with no approval reuse.
- Command registry validation found no undocumented command drift.
- `docs/FEATURE_MATURITY.md` now has a `Next Work-Up Candidates` section.
- `FULL-FEATURE-MATURITY-REVIEW` is marked complete; next queued prompt is `NATIVE-SKILLS-FOUNDATION`.
- Scheduler / Automation v1 implemented in the working tree.
- Added `agent/workflows/scheduler.py`.
- Added `python smart_agent.py schedule list`.
- Added `python smart_agent.py schedule create`.
- Added `python smart_agent.py schedule run <schedule_id>`.
- Added `python smart_agent.py schedule pause <schedule_id>`.
- Added `python smart_agent.py schedule delete <schedule_id>`.
- Supported scheduled workflows in v1:
  - `daily_briefing`
  - `connector_doctor`
  - `eval_safe`
  - `memory_cleanup`
  - `audit_summary`
- Scheduler v1 is manual-run only and creates no LaunchAgent, cron job, daemon, login item, or hidden background persistence.
- Schedule records are stored locally in JSON at `data/schedules.json` by default; tests and advanced usage can set `SCHEDULE_PATH`.
- Schedule lifecycle events and scheduled run start/finish events are audited.
- Scheduled tool workflows still use `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Personal Daily Briefing sections remain approval-gated and are not read when approval is unavailable.
- Unsupported workflows, including direct send/write/CRITICAL action workflows, are rejected.
- `memory_cleanup` is intentionally conservative in v1 and does not delete memory automatically.
- Added `docs/SCHEDULER.md`.
- Scheduler focused tests passed: 7 passed in 0.47s.
- Scheduler/prompt/registry/maturity focused tests passed: 25 passed in 0.45s.
- Full suite passed: 528 passed in 10.76s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Command registry validation passed: 154 commands, no missing records.
- Diff whitespace check passed.
- Command Registry + Manual QA System implemented in the working tree.
- Added a durable command catalog with 150 command records across core runtime, diagnostics, connectors, approvals, Action Center, weather, web/research, workspace files, memory, personal modules, workflows, PromptOps, quality/evals, planned groups, legacy commands, and blocked commands.
- Added `docs/COMMAND_REGISTRY.md`.
- Added `docs/COMMAND_TEST_MATRIX.md`.
- Added `docs/COMMAND_LEGACY.md`.
- Added `docs/COMMAND_QA_RUNBOOK.md`.
- Added `docs/templates/command_record_template.md`.
- Added `docs/templates/command_test_record_template.md`.
- Added `python smart_agent.py commands list`.
- Added `python smart_agent.py commands show <command_id>`.
- Added `python smart_agent.py commands search "<query>"`.
- Added `python smart_agent.py commands legacy`.
- Added `python smart_agent.py commands deprecated`.
- Added `python smart_agent.py commands validate`.
- Added `python smart_agent.py commands qa-plan`.
- Added `python smart_agent.py commands qa-run <group>`.
- Command registry validation passes locally and checks command docs, matrix coverage, metadata completeness, README links, and AGENTS command-registry rules.
- `commands qa-run` is intentionally non-executing in v1; it prints SAFE/LOW manual QA examples for the requested group.
- Manual QA results remain pending for most commands and should be logged in `docs/COMMAND_TEST_MATRIX.md` as suites are run.
- Command status counts: 129 active, 10 planned, 4 experimental, 4 stubbed, 2 legacy, 1 blocked, 0 deprecated, 0 removed.
- Command registry focused tests passed: 13 passed in 0.11s.
- Full suite passed: 521 passed in 10.74s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Diff whitespace check passed.
- PromptOps Workbench v1 implemented in the working tree.
- Added `agent/promptops/` modules for import, clipboard, workbench, runner, state, safety, reports, and models.
- Added `python smart_agent.py work import <file>`.
- Added `python smart_agent.py work import --stdin`.
- Added `python smart_agent.py work import-clipboard`.
- Added `python smart_agent.py work next`, `show-next`, `copy-next`, `resume`, `status`, `review`, and `audit`.
- Added `python smart_agent.py work mark-active`, `mark-complete`, and `mark-failed`.
- Added disabled-by-default `python smart_agent.py work run-next`.
- Added safe-only `python smart_agent.py work autopilot --safe-only --max-prompts N`.
- Added `docs/PROMPTOPS_WORKBENCH.md` and `docs/templates/promptops_run_report_template.md`.
- PromptOps imports prompt packs or raw single prompts, updates prompt ledger/queue/audit/project state, and does not execute imported prompts automatically.
- Imported prompt text is labeled `UNTRUSTED_DOCUMENT`.
- Runner execution requires `CODEX_RUNNER_ENABLED=true`; default behavior writes a safe report instead of running Codex.
- Autopilot refuses HIGH/CRITICAL/FORBIDDEN risk prompts, approval-gated prompts, and forbidden categories.
- PromptOps focused prompt/docs tests passed: 41 passed in 0.32s.
- Full suite passed: 516 passed in 10.91s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Diff whitespace check passed.
- Prompt Pack import/splitting support is complete.
- Added `agent/prompts/pack_models.py`, `pack_parser.py`, `pack_validator.py`, `prompt_store.py`, `prompt_queue.py`, and `prompt_audit.py`.
- Added `docs/PROMPT_PACK_FORMAT.md` and `docs/templates/prompt_pack_template.md`.
- Added `python smart_agent.py prompts validate-pack <pack_file>`.
- Added `python smart_agent.py prompts import <pack_file>`.
- Added `python smart_agent.py prompts split <pack_file>`.
- Added `python smart_agent.py prompts mark-superseded <prompt_id> --by <replacement_id>`.
- Prompt packs are validation-first, import-only, split into `prompts/queued/`, and never executed automatically.
- Prompt Ledger and Prompt Queue tracking is in progress.
- Added `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and `docs/PROMPT_AUDIT.md`.
- Added prompt record directories under `prompts/queued`, `prompts/active`, `prompts/completed`, `prompts/skipped`, `prompts/failed`, and `prompts/superseded`.
- Added `docs/templates/prompt_record_template.md`.
- Added `python smart_agent.py prompts list/next/show/add/mark-active/mark-complete/mark-skipped/mark-failed/audit/missing`.
- Reconstructed prompt evidence for baseline, weather, connector, workflow, controlled-action, and self-improvement batches.
- Queued the next important prompt groups beginning with `NATIVE-SKILLS-FOUNDATION`.
- Controlled Self-Improvement Implementation Loop v1 implemented in the working tree.
- Added `python smart_agent.py improve implement <proposal_id>`.
- Added `python smart_agent.py improve run-tests`.
- Added `python smart_agent.py improve show-diff`.
- Added `python smart_agent.py improve commit --from-action <action_id>`.
- Implementation requires an approved proposal record in `data/self_improvement/approved_proposals.json`.
- Implementation creates/switches to a `codex/` branch.
- Approved file writes go through brokered `filesystem.write`.
- Tests and diff go through brokered `code.run_tests` and `git.diff`.
- Commit is queued as an Action Center `self_improvement.commit` record and does not execute until approved.
- Protected safety file edits, policy weakening, audit disabling, personal-data grants, persistence paths, and package installs without approval are blocked.
- Controlled self-improvement focused tests passed: 21 passed in 2.34s.
- Personal Task Extraction v1 implemented in the working tree.
- Added `python smart_agent.py tasks extract --from-notes ./workspace/notes.md`.
- Added `python smart_agent.py tasks extract --from-email-thread <thread_id>`.
- Added `python smart_agent.py tasks extract --from-meeting <event_id>`.
- Added `python smart_agent.py tasks extract --from-url <url>`.
- Added `python smart_agent.py tasks extract --from-capture ./workspace/captures/<file>.json`.
- Added `python smart_agent.py tasks extract --dry-run`.
- Each source is read through existing brokered tools/connectors.
- Email/calendar personal sources remain approval-gated.
- Extracted task candidates become pending Action Center `tasks.create` records only.
- No task creation, writes/sends, contact edits, or memory writes execute in the extraction workflow.
- Untrusted source instruction lines are filtered before task extraction.
- Personal Task Extraction focused workflow tests passed: 70 passed in 1.45s.
- Meeting Follow-Up v1 implemented in the working tree.
- Added `python smart_agent.py meeting follow-up --event-id <event_id>`.
- Added `python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md`.
- Added `python smart_agent.py meeting follow-up --dry-run`.
- Added optional `--contact` and `--json` support.
- Selected calendar event reads remain approval-gated through `calendar.read_selected_event`.
- Meeting notes are read only through brokered `filesystem.read` and workspace path policy.
- Notes content is treated as `UNTRUSTED_DOCUMENT`; instruction-injection lines are filtered before synthesis.
- Suggested tasks, email sends, and calendar updates create pending Action Center records only.
- No email send, calendar write, task creation, contact edit, or memory write executes in the workflow.
- Meeting Follow-Up focused workflow tests passed: 61 passed in 1.01s.
- Full suite passed: 465 passed in 8.59s.
- Startup policy, capability manifest validation, docs validation, and diff whitespace check passed.
- Daily Briefing v2 implemented in the working tree.
- Added configurable opt-in sections for weather, calendar selected date range, tasks/reminders, email metadata only, web topics, memory preferences, and suggested Action Center actions.
- Added `python smart_agent.py briefing daily --sections weather,calendar,tasks,email,web,memory,suggested_actions`.
- Added `python smart_agent.py briefing config show`.
- Added `python smart_agent.py briefing config set sections=... weather_location=... web_topics=...`.
- Personal-data sections remain HIGH risk and require approval; denied or unavailable sections are skipped independently and reported in the final briefing.
- Email bodies and messages are not read.
- No writes/sends execute from the briefing; suggested actions create pending Action Center items only.
- No memory writes occur by default; the memory section reads non-personal preference records only.
- Dry-run shows planned tool calls and approvals without executing tools.
- Daily Briefing v2 focused workflow tests passed: 51 passed in 0.53s.
- Notes / Knowledge Capture v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py capture note "text"`.
- Added `python smart_agent.py capture from-file <path>`.
- Added `python smart_agent.py capture from-url <url>`.
- Added `python smart_agent.py capture list`.
- Added `python smart_agent.py capture summarize`.
- Added `python smart_agent.py capture promote-to-memory <capture_id>`.
- Captures are stored as JSON files under `./workspace/captures` through brokered `filesystem.write`.
- Source files are read through brokered `filesystem.read`.
- URLs are fetched through brokered `web.fetch_url`.
- Web captures remain `UNTRUSTED_WEB`; file captures remain `UNTRUSTED_DOCUMENT`; note captures are `TRUSTED_USER`.
- Secrets are rejected before capture writes.
- Apple Notes integration, private app database scraping, and personal-data connector access were not added.
- Memory promotion calls brokered `memory.store`; personal-looking content is blocked by default before memory storage.
- Browser selected URL and clipping v1 completed and locally release-gated in the working tree.
- Added `docs/decisions/browser_selected_tab_clipping.md`.
- Added `python smart_agent.py browser read-url "<url>"`.
- Added `python smart_agent.py browser summarize-url "<url>"`.
- Added `python smart_agent.py browser clip-url "<url>" --to workspace`.
- Added `python smart_agent.py browser selected-tab` as a clear unavailable/stubbed selected-tab path.
- URL read and summarize workflows fetch only explicit public URLs through brokered `web.fetch_url`.
- URL clips fetch through brokered `web.fetch_url` and write only under `./workspace` through brokered `filesystem.write`.
- Fetched page content remains `UNTRUSTED_WEB`; saved clips are labeled `UNTRUSTED_DOCUMENT`.
- The connector does not read browser history, cookies, sessions, forms, passwords, bookmarks, or private browser profile databases.
- No browser automation, form submission, cookie/session scraping, password manager access, or native selected-tab integration was added.
- Added browser connector status metadata for the explicit URL workflow while keeping native selected-tab disabled/stubbed.
- Messages safe handoff v1 completed and locally release-gated in the working tree.
- Added `docs/decisions/messages_send_path.md`.
- Added `messages.save_draft` and `messages.copy_draft` capabilities, both HIGH risk, disabled by default, approval-required, and no-send.
- Added Action Center handoff records from `python smart_agent.py messages draft-from-text --to "Name" --context-file ./workspace/thread.txt`.
- Added `python smart_agent.py messages save-draft --from-action <action_id>`.
- Added `python smart_agent.py messages copy-draft --from-action <action_id>`.
- Saved message drafts remain inside `./workspace`.
- Clipboard copy uses approval-gated handoff and supports mock mode in tests.
- Automatic text/message sending remains deferred.
- No Messages database scraping, Full Disk Access dependency, AppleScript send automation, Accessibility send automation, or memory storage was added.
- Email approved send v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py email draft-new --to ... --subject ... --body ...`.
- Added Action Center backed `python smart_agent.py email draft-reply <thread_id> --to ... --subject ... --body ...`.
- Added `python smart_agent.py email send --from-action <action_id>`.
- Email send drafts create Action Center records only and do not send.
- Approved email send actions execute once through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Direct `email.send_approved` calls without an Action Center action id are blocked even if an approval manager auto-approves the capability.
- `email.send_approved` remains disabled by default and CRITICAL per-action approval only.
- Preflight previews include from account/provider, to, cc, bcc, subject, full body, attachments, thread/reply context, and rollback impossibility.
- Editing an email send action invalidates prior approval.
- Bulk sends and attachments are blocked in v1.
- The current email send provider is mock-only for tests; real provider integration is deferred.
- Email thread context remains `UNTRUSTED_EMAIL` and cannot approve or instruct sending.
- Email send contents are not written to memory by default.
- Contacts approved edits v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py contacts draft-update <contact_id> --set field=value --old field=value`.
- Added `python smart_agent.py contacts update --from-action <action_id>`.
- Added `python smart_agent.py contacts draft-create --display-name "Name" --field field=value`.
- Added `python smart_agent.py contacts create --from-action <action_id>`.
- Contact update/create drafts create Action Center records only and do not mutate Contacts.app.
- Approved contact update/create actions execute once through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- `contacts.update_selected` and `contacts.create` remain disabled by default and CRITICAL per-action approval only.
- Contact updates require explicit field-level diffs.
- Phone, email, address, and note-like contact values are redacted in persisted previews and audit logs.
- Bulk contact edits are denied.
- Contact deletion remains deferred and unregistered.
- The current contact write connector remains a no-external-change stub; live native Contacts writes are deferred.
- Contact details are not written to memory by default.
- Reminders / Tasks connector v1 completed and locally release-gated in the working tree.
- Added adapter-first personal tasks connector with `NotConfiguredTasksConnector` and `MockTasksConnector`.
- Added brokered `tasks.list`, `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` tools.
- Added `python smart_agent.py tasks list`.
- Added `python smart_agent.py tasks draft-create "task"`.
- Added `python smart_agent.py tasks create --from-action <action_id>`.
- Added `python smart_agent.py tasks complete <task_id>`.
- Added `python smart_agent.py tasks update <task_id>`.
- Added `python smart_agent.py tasks delete <task_id>`.
- Task create drafts create Action Center records only and execute once from approved actions.
- Task listing is HIGH risk and approval-required.
- Task create/update/complete/delete are CRITICAL per-action approval tools.
- Tasks connector is disabled by default, selected-scope, no full export, no memory storage by default, and no native Reminders provider enabled.
- Added Reminders / Tasks connector decision notes.
- Calendar approved writes v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py calendar draft-create`.
- Added `python smart_agent.py calendar create --from-action <action_id>`.
- Added `python smart_agent.py calendar draft-update <event_id>`.
- Added `python smart_agent.py calendar update --from-action <action_id>`.
- Added `python smart_agent.py calendar draft-delete <event_id>`.
- Added `python smart_agent.py calendar delete --from-action <action_id>`.
- Calendar draft commands create Action Center records only; they do not create, update, delete, invite, export, or store calendar data in memory.
- Calendar `--from-action` commands require an approved Action Center record and execute through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Calendar approved write actions are consumed once after brokered execution.
- Calendar create/update/delete capabilities remain disabled by default and CRITICAL per-action approval only.
- The current approved write connector remains a no-external-change stub; live native Calendar writes are deferred.
- Notes/body text is omitted from drafts unless `--allow-notes` is explicit.
- Automatic invites and recurring events are not supported in v1.
- Unified Action Center v1 completed in the working tree.
- Added `python smart_agent.py actions list`.
- Added `python smart_agent.py actions show <action_id>`.
- Added `python smart_agent.py actions approve <action_id>`.
- Added `python smart_agent.py actions deny <action_id>`.
- Added `python smart_agent.py actions edit <action_id> key=value`.
- Added `python smart_agent.py actions clear-denied`.
- Added `python smart_agent.py actions export`.
- Added persisted action records in `data/actions.json` with action id, timestamps, status, tool/capability, risk/trust, preview, sanitized args, rollback availability, source workflow, approval state, and audit ids.
- Action Center integrates with `ApprovalStore`/`ApprovalRequest`, redacts previews, records audit lifecycle events, invalidates prior approvals after edits, and enforces one-time approval consumption.
- Action Center does not execute tools directly; any future execution must still go through `ToolBroker`, `PolicyEngine`, approval rules, and `AuditLogger`.
- CRITICAL action records remain per-action only with no approval reuse.
- Non-interactive action execution gates block approval-required pending actions.
- Live validation and eval harness v1 completed in the working tree.
- Added `python smart_agent.py eval list`.
- Added `python smart_agent.py eval run --safe`.
- Added `python smart_agent.py eval run --lmstudio`.
- Added `python smart_agent.py eval run --web`.
- Added `python smart_agent.py eval run --weather`.
- Added `python smart_agent.py eval run --workspace`.
- Added `python smart_agent.py eval run --memory`.
- Added `python smart_agent.py eval report`.
- Eval safe runs cover no-tool LM Studio chat when configured, time tool roundtrip, weather current/forecast when configured, web search/fetch when configured, controlled workspace read/write, non-sensitive memory add/search/delete, dry-run/preflight, and connector doctor checks.
- Personal-data evals for calendar, contacts, email, and messages are skipped by default.
- Eval reports write structured results to `logs/eval_results.json` and Markdown summaries to `docs/EVAL_REPORT.md`.
- Eval tool checks execute through `ToolBroker` and are audited.
- Eval harness performs no sends, no calendar/contact writes, no personal-data reads by default, and no personal memory storage.
- Project tracking and release gate sync completed.
- Confirmed current reported built features are reflected in `CHANGELOG.md`, `docs/FEATURE_REGISTRY.md`, `docs/FEATURE_MATURITY.md`, `docs/FEATURE_ROADMAP.md`, and this project state file.
- Full suite still reports 359 passing tests.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed.
- Confirmed no personal-data tools are enabled by default.
- Confirmed enabled HIGH-risk actions evaluate to approval-required.
- Confirmed CRITICAL capabilities require per-action approval and disallow approval reuse.
- Confirmed unknown capabilities are denied.
- Confirmed the next feature set is queued as controlled actions and proactive workflows, with no runtime feature implementation in this sync.
- Agent Dashboard v1 completed and validated.
- Added `python smart_agent.py dashboard`.
- Added `python smart_agent.py status`.
- Dashboard reports current model/config, LM Studio status, enabled tools, connector status, permissions, pending approvals, recent audit metadata, memory counts, risk settings, last test run, and setup hints.
- Dashboard is metadata/status-only: it does not attach tools, execute connector actions, read personal data, grant permissions, consume approvals, start background actions, write memory, or display memory content.
- Secrets are redacted and personal connectors are displayed from configuration/status metadata only.
- Self-improvement backlog generator completed and validated.
- Added `python smart_agent.py improve backlog`.
- Added `python smart_agent.py improve propose`.
- Backlog/propose mode reads only an approved set of project docs, tests, capability config, self-improvement workflow files, and audit-log paths through brokered `filesystem.read` calls.
- Backlog/propose mode is read-only: no file edits, permission grants, package installs, personal-data access, memory writes, or commits.
- Dry-run mode audits planned file reads without reading file contents.
- Safety-weakening suggestions such as disabling audit logs, relaxing ToolBroker/PolicyEngine gates, or enabling personal-data connectors by default are flagged as blocked.
- Email Triage v1 completed and validated.
- Added `python smart_agent.py email triage` and `python smart_agent.py email triage --selected-thread "<thread_id>"`.
- Email Triage v1 uses metadata only by default, classifies priority from metadata, reads at most one selected thread body after approval, summarizes it, and drafts a reply without sending.
- Selected thread body content remains `UNTRUSTED_EMAIL`, is redacted from triage reports, and is not stored in memory by default.
- Meeting Prep v1 completed and validated.
- Added `python smart_agent.py meeting prep` with selected `--event-id` or `--date` plus `--title`, optional `--contact`, optional `--web-topic`, `--dry-run`, and `--json`.
- Added brokered `calendar.read_selected_event` capability as HIGH risk, disabled by default, approval-required, selected-event only, and no-memory by default.
- Meeting Prep v1 uses only brokered selected calendar event reads, optional approved contact searches, and optional web search; it performs no sends, writes, bulk exports, or memory writes by default.
- Daily Briefing v1 completed and validated.
- Added `python smart_agent.py briefing daily` with optional `--weather`, `--calendar`, `--email-metadata`, `--web-topic`, `--dry-run`, and `--json`.
- Daily Briefing v1 uses only explicitly selected sources through `ToolBroker`; calendar and email metadata are skipped when disabled or unapproved.
- Daily Briefing v1 performs no sends, writes, message reads, email body reads, browser history reads, contact reads, or memory writes by default.
- Messages/text draft-only assistant completed and validated.
- Added explicit `messages.draft_from_text` capability for the workspace-only manual fallback.
- Email metadata + selected-thread + draft-only assistant completed and validated.
- Email metadata and body outputs are labeled `UNTRUSTED_EMAIL`; draft output remains no-send/no-delete/no-move/no-archive.
- Contacts read-only selected-scope connector completed and validated.
- Added contacts contact-text-as-data safety notice and sensitive-field requested/config regression coverage.
- Calendar read-only selected-range connector completed and validated.
- Added calendar event-text-as-data safety notice and regression coverage.
- Personal connector readiness gate completed and validated.
- Added `docs/checklists/personal_connector_readiness.md`.
- Verified ToolBroker, PolicyEngine, approval UI, dry-run/preflight, AuditLogger, secret redaction, connector registry, personal disabled-by-default manifest entries, HIGH/CRITICAL approval rules, untrusted-content wrappers, memory defaults, denial tests, non-interactive approval blocking, and no direct connector calls outside ToolBroker.
- Memory v2 safe context completed and validated.
- Workspace file assistant workflow completed and validated.
- Source-grounded web research hardening completed and validated.
- Approval UI foundation and universal dry-run/preflight mode completed.
- Added prompt-free `preflight` command backed by deterministic routing and `ToolBroker.dry_run()`.
- Runtime doctor + connector dashboard polish completed.
- Durable project tracking files and validation updated.
- Capability manifest normalized and startup validation hardened.
- M0-M11 baseline complete.
- Post-connector release gate passed locally.
- Weather connector pattern completed with Open-Meteo, NWS, WeatherKit stub, safe preferences, caching/rate limiting, alerts, and daily weather briefing.
- Connector framework extraction completed in the working tree and validated with targeted/full tests before this tracking pass.

## Current Work In Progress

None. Internet Access release gate and roadmap reset is complete and local/full validations passed with `./.venv/bin/python` 3.12.13.

## Files Being Changed

- Internet Access release gate and roadmap reset additions/changes:
  - `docs/decisions/internet_access_graduation_track.md`
  - `docs/web/WEB_ACCESS_POLICY.md`
  - `docs/web/INTERNET_PROVIDER_STRATEGY.md`
  - `docs/web/SOURCE_GROUNDING_REQUIREMENTS.md`
  - `docs/web/BLOCKED_SOURCE_POLICY.md`
  - `tests/test_feature_maturity_docs.py`
  - README, CHANGELOG, feature registry, feature maturity, roadmap, prompt ledger/queue/audit, project state, completion report, risk register, threat model, test plan, and release checklist.
- PTM batch additions/changes:
  - `agent/prompts/evidence.py`
  - `agent/prompts/recovery.py`
  - `agent/prompts/pack_parser.py`
  - `agent/prompts/prompt_store.py`
  - `agent/ui/prompts.py`
  - `agent/ui/cli_commands.py`
  - `agent/ui/evals.py`
  - `agent/ui/command_registry.py`
  - `agent/promptops/state.py`
  - `tests/test_prompt_tracker_maturity.py`
  - `tests/test_prompt_tracking.py`
  - `dogfood_suites/prompt_tracker_core.yaml`
  - `dogfood_suites/prompt_pack_import.yaml`
  - `dogfood_suites/promptops_workbench.yaml`
  - `eval_cases/prompt_tracker.json`
  - `docs/prompt_tracker/`
  - `prompts/completed/PTM-01.md` through `prompts/completed/PTM-10.md`
  - Prompt tracking, feature tracking, command registry, risk/threat/test/release, README, CHANGELOG, and completion docs.
- Free-first web acquisition additions/changes:
  - `agent/tools/web/acquisition.py`
  - `agent/tools/registry.py`
  - `smart_agent.py`
  - `config/capabilities.yaml`
  - `.env.example`
  - `tests/test_web_acquisition.py`
  - `README.md`
  - `docs/connectors/PROVIDER_SELECTION.md`
  - `docs/connectors/COST_POLICY.md`
  - `docs/COMMAND_REGISTRY.md`
  - `docs/COMMAND_TEST_MATRIX.md`
  - `docs/FEATURE_REGISTRY.md`
  - `docs/FEATURE_MATURITY.md`
  - `docs/FEATURE_ROADMAP.md`
  - `docs/PROMPT_LEDGER.md`
  - `docs/PROMPT_QUEUE.md`
  - `docs/PROMPT_AUDIT.md`
  - `docs/RISK_REGISTER.md`
  - `docs/THREAT_MODEL.md`
  - `docs/TEST_PLAN.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/PROJECT_STATE.md`
  - `docs/COMPLETION_REPORT.md`
  - `CHANGELOG.md`
- `.env.example`
- `agent/connectors/cost_policy.py`
- `tests/test_provider_cost_policy.py`
- `docs/decisions/cost_aware_provider_policy.md`
- `docs/connectors/PROVIDER_SELECTION.md`
- `docs/connectors/COST_POLICY.md`
- `.gitignore`
- `agent/session_logs/review.py`
- `agent/ui/cli_commands.py`
- `agent/ui/command_registry.py`
- `tests/test_session_logs.py`
- `tests/test_prompt_tracking.py`
- `README.md`
- `CHANGELOG.md`
- `docs/BUG_TRIAGE.md`
- `docs/SESSION_LOGGING.md`
- `docs/dogfood/DOGFOOD_GUIDE.md`
- `docs/COMMAND_REGISTRY.md`
- `docs/COMMAND_TEST_MATRIX.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/PROMPT_LEDGER.md`
- `docs/PROMPT_QUEUE.md`
- `docs/PROMPT_AUDIT.md`
- `docs/RISK_REGISTER.md`
- `docs/THREAT_MODEL.md`
- `docs/TEST_PLAN.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/COMPLETION_REPORT.md`
- `reports/session_reviews/.gitkeep`
- `bugs/.gitkeep`

## Commands Run

- Internet Access release gate and roadmap reset commands:
  - `./.venv/bin/python -m pytest tests/test_feature_maturity_docs.py -q`
  - `./.venv/bin/python -m pytest tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
  - `./.venv/bin/python -m pytest -q`
  - `./.venv/bin/python -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy(); print('startup policy ok')"`
  - `./.venv/bin/python -m agent.safety.validation config/capabilities.yaml`
  - `./scripts/agent commands validate`
  - `./scripts/agent prompts audit`
- PTM batch commands:
  - `.venv/bin/pytest tests/test_prompt_tracking.py tests/test_prompt_pack.py tests/test_promptops_workbench.py -q`
  - `.venv/bin/pytest tests/test_prompt_tracking.py tests/test_prompt_pack.py tests/test_promptops_workbench.py tests/test_prompt_tracker_maturity.py tests/test_dogfood_suites.py tests/test_command_registry.py tests/test_feature_maturity_docs.py -q`
  - `./scripts/agent prompts mark-active PTM-01..PTM-10`
  - `./scripts/agent prompts mark-complete PTM-01..PTM-10 --test-result "targeted prompt tracker tests passed: 54 passed" --docs-updated yes`
  - `./scripts/agent eval run --prompt-tracker --json`
  - `./scripts/agent prompts validate-pack prompts/packs/prompt-tracker-maturity-v1.promptpack.md`
  - `./scripts/agent dogfood run prompt_tracker_core --dry-run`
  - `./scripts/agent prompts evidence PTM-10`
  - `./scripts/agent prompts recover-plan`
  - `./scripts/agent commands validate`
  - Startup policy validation and capability manifest validation snippets.
  - `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q`
- Free-first web acquisition commands:
  - `./scripts/agent prompts mark-active FREE-FIRST-WEB-ACQUISITION --notes ...`
  - `.venv/bin/python -m pytest tests/test_web_acquisition.py`
  - `./scripts/agent tools list | rg "web\\.(robots|sitemap|feed|acquire)"`
  - `.venv/bin/python -m pytest tests/test_web.py tests/test_web_acquisition.py tests/test_command_registry.py`
  - `.venv/bin/python -m agent.safety.validation config/capabilities.yaml`
  - `.venv/bin/python - <<'PY' ... validate_capabilities_config(...) ... PY`
  - `./scripts/agent commands validate`
  - `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest`
  - `./scripts/agent prompts mark-complete FREE-FIRST-WEB-ACQUISITION --test-result ... --docs-updated yes`
- Required governance/tracking docs read with `sed` and `rg` for the cost-aware provider policy task.
- Existing web/weather provider, connector registry, audit, runtime config, redaction, and test files inspected with `rg` and `sed`.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_provider_cost_policy.py`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_provider_cost_policy.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate`
- Startup policy validation.
- Capability manifest validation.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q`
- `git diff --check`
- Required governance/tracking docs read with `sed` and `rg`.
- Inspected session logging, replay, store, dogfood, and command registry code with `rg` and `sed`.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_session_logs.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 - <<'PY' ... write_command_docs('.') ... PY`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_session_logs.py tests/test_command_registry.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate`
- Startup policy validation.
- Capability manifest validation.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_session_logs.py tests/test_command_registry.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q && /Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate && git diff --check`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_dogfood_suites.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 - <<'PY' ... write_command_docs('.') ... PY`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py dogfood list`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py dogfood run all_safe --dry-run`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_dogfood_suites.py tests/test_command_registry.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate`
- Startup policy validation.
- Capability manifest validation.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_dogfood_suites.py tests/test_command_registry.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q && /Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate && git diff --check`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_dogfood_suites.py -q && git diff --check`
- Self-improvement workflow, CLI, command registry, and tests inspected with `sed` and `rg`.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_self_improvement.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 - <<'PY' ... write_command_docs('.') ... PY`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py improve overnight-plan --json`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py tests/test_command_registry.py -q`
- Startup policy validation.
- Capability manifest validation.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest`
- Personal-data connector/default-enabled manifest check.
- HIGH/CRITICAL approval manifest check.
- `git diff --check`
- `git status --short`
- `sed`/`rg` reads of required governance docs, ToolBroker, PolicyEngine, ApprovalManager, AuditLogger, capability manifest, CLI dispatch, command registry, memory/capture/action stores, and related tests.
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_backup_restore.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_policy.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 - <<'PY' ... validate_startup_policy() ... PY`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 smart_agent.py commands validate`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest tests/test_backup_restore.py tests/test_policy.py tests/test_ux_packaging.py -q`
- `/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest -q`
- `git diff --check && git status --short`
- `sed`/`rg` reads of the required governance docs, Action Center implementation, approval/action preview code, README, and tracking docs.
- `git diff -- agent/safety/actions.py tests/test_action_center.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_action_center.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py commands validate`
- `git diff --check`
- `rg` and `sed` reads of required governance docs, prompt tracking docs, calendar write tools, Action Center, calendar write workflow, CLI, capability manifest, and calendar write tests.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_calendar_approved_writes.py tests/test_approved_write_actions.py tests/test_release_gate.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py commands validate`
- `git diff --check`
- `rg` and `sed` reads of required governance docs, Tasks connector, Action Center, ToolBroker, capability manifest, CLI, command registry, and task tests.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_tasks_connector.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_tasks_connector.py tests/test_command_registry.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY - <<'PY' ... write_command_docs('.') ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py commands validate`
- `git diff --check`
- `rg -n "eval run|eval list|EVAL|Eval|eval_report|run_eval|evals|argparse.*eval|subparsers.*eval" smart_agent.py agent tests docs README.md`
- `rg --files | rg "eval|scorecard|golden|EVAL"`
- `git status --short && git branch --show-current`
- `sed -n '1,260p' agent/ui/evals.py`
- `sed -n '260,620p' agent/ui/evals.py`
- `sed -n '300,365p' agent/ui/cli_commands.py`
- `sed -n '1,340p' tests/test_eval_harness.py`
- `sed -n '1,260p' agent/core/router.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_eval_harness.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py eval run --routing --policy --tools --workflows --prompt-injection`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_eval_harness.py tests/test_command_registry.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY - <<'PY' ... write_command_docs('.') ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py tests/test_command_registry.py -q`
- Read required governance, tracking, and native-skills docs with `sed`.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts mark-active NATIVE-SKILL-MANIFEST`
- Implemented metadata-only native skill manifest models, loader, validator, registry, and CLI commands.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_native_skill_manifests.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py skills validate`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py skills show native_skill_vetter`
- Regenerated command registry docs after adding `skills list/show/validate/doctor`.
- Focused native manifest/doctor/dashboard/command validation.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts mark-active NATIVE-SKILL-VETTER`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_native_skills.py -q`
- Startup policy validation.
- Capability manifest validation.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py commands validate`
- Regenerated command registry docs after adding `skills` commands.
- CLI smoke for `skills vet` and `skills score` using a temporary workspace skill file; removed the temporary workspace file after the smoke.
- Web research for OpenClaw/ClawHub/LobeHub-style marketplace category and risk signals.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts mark-active SKILL-MARKETPLACE-SURVEY`
- Updated native-skills survey docs, matrix, shortlist, and tracking files.
- Focused docs/prompt validation, full test suite, startup policy validation, capability manifest validation, and prompt audit pending/finalized during this run.
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' smart_agent.py`
- `rg -n "subparsers|add_parser|def _run|prompts|dashboard|memory|improve" smart_agent.py agent/ui tests docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `sed -n '1,360p' agent/ui/cli_commands.py`
- `sed -n '1,220p' CHANGELOG.md`
- `sed -n '1,160p' docs/FEATURE_REGISTRY.md`
- `sed -n '1,170p' docs/FEATURE_MATURITY.md`
- `sed -n '1,220p' tests/test_feature_maturity_docs.py`
- `sed -n '1,180p' docs/TEST_PLAN.md`
- `sed -n '1,140p' docs/RISK_REGISTER.md`
- `sed -n '1,160p' docs/THREAT_MODEL.md`
- `sed -n '1,160p' docs/RELEASE_CHECKLIST.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts next`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- Startup policy and capability manifest validation.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts audit`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_prompt_pack.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- Startup policy and capability manifest validation after prompt pack support.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts audit`
- `git diff --check`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' agent/tools/personal/read_only.py && sed -n '1,220p' agent/tools/personal/write_actions.py`
- `sed -n '1,260p' agent/tools/registry.py && rg -n "tasks\\.|reminders|Reminder|Task" agent tests config docs README.md -g '*.py' -g '*.yaml' -g '*.md'`
- `sed -n '820,1040p' smart_agent.py`
- `sed -n '1,180p' agent/config/schema.py && sed -n '1180,1385p' config/capabilities.yaml`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_tasks_connector.py -q; else python3 -m pytest tests/test_tasks_connector.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py tasks draft-create "Follow up with Alex" --source-workflow meeting_prep | head -80; else python3 smart_agent.py tasks draft-create "Follow up with Alex" --source-workflow meeting_prep | head -80; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_tasks_connector.py tests/test_connector_framework.py::test_connector_registry_loads tests/test_connectors.py::test_connectors_cli_list -q; else python3 -m pytest tests/test_tasks_connector.py tests/test_connector_framework.py::test_connector_registry_loads tests/test_connectors.py::test_connectors_cli_list -q; fi`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `sed -n '1,420p' agent/tools/personal/calendar.py`
- `sed -n '1,180p' agent/tools/personal/write_actions.py`
- `sed -n '1,620p' agent/core/tool_broker.py`
- `rg -n "def _run_calendar|calendar draft|calendar create|calendar update|calendar delete|calendar\\.create_event|write_actions" smart_agent.py agent tests -g '*.py'`
- `sed -n '700,840p' smart_agent.py`
- `sed -n '1,160p' tests/test_approved_write_actions.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_calendar_approved_writes.py -q; else python3 -m pytest tests/test_calendar_approved_writes.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py calendar draft-create --title "Test" --start 2026-05-23T10:00 --end 2026-05-23T10:30 | head -80; else python3 smart_agent.py calendar draft-create --title "Test" --start 2026-05-23T10:00 --end 2026-05-23T10:30 | head -80; fi`
- `git status --short data logs | cat`
- `pwd && git status --short && git branch --show-current`
- `rg -n "calendar\\.create_event|contacts\\.update_selected|email\\.send_approved|messages\\.send_approved|filesystem\\.delete|git\\.commit|memory\\.(store_personal|write_personal)|self_improvement\\.commit" config/capabilities.yaml agent tests docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md README.md`
- `sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/safety/action_preview.py`
- `sed -n '1,320p' agent/ui/cli_commands.py`
- `sed -n '1,220p' agent/safety/audit.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_action_center.py -q; else python3 -m pytest tests/test_action_center.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest -q; else python3 -m pytest -q; fi`
- Startup policy validation via `validate_startup_policy('config/capabilities.yaml')`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_feature_maturity_docs.py -q; else python3 -m pytest tests/test_feature_maturity_docs.py -q; fi`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py actions list | head -80; else python3 smart_agent.py actions list | head -80; fi`
- `rg -n "direct|ToolBroker|execute\\(|ActionCenter|action\\." agent/safety/actions.py agent/ui/cli_commands.py tests/test_action_center.py`
- `date '+%Y-%m-%d %H:%M %Z'`
- `git status --short --branch`
- `git log --oneline -5`
- `date '+%Y-%m-%d %H:%M %Z'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest -q; else python3 -m pytest -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... validate_startup_policy('config/capabilities.yaml') ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')) ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_feature_maturity_docs.py -q; else python3 -m pytest tests/test_feature_maturity_docs.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... PolicyEngine invariant checks ... PY`
- `rg -n "LM Studio|Qwopus|no-tool|deterministic router|ToolBroker|PolicyEngine|PermissionManager|ApprovalManager|AuditLogger|preflight|doctor|connector framework|Agent Dashboard|Open-Meteo|NWS|WeatherKit|web search|Workspace file|Memory v2|Calendar read-only|Contacts read-only|Email Triage|Meeting Prep|Daily Briefing|self-improvement backlog" CHANGELOG.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/PROJECT_STATE.md docs/FEATURE_ROADMAP.md`
- `sed -n '1,260p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' CHANGELOG.md`
- `git diff --check`
- `rg -n "subprocess|os\\.system|Popen|requests\\.|urllib|open\\(|sqlite3|~/Library|Library/Messages|Library/Mail|Keychains|execute\\(" agent smart_agent.py -g '*.py'`
- `sed -n '1,220p' docs/FEATURE_REGISTRY.md && sed -n '70,160p' docs/FEATURE_MATURITY.md && sed -n '1,180p' docs/FEATURE_ROADMAP.md`
- `sed -n '1,220p' SPEC.md && sed -n '1,220p' AGENTS.md && sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' docs/FEATURE_ROADMAP.md && sed -n '1,120p' docs/FEATURE_REGISTRY.md && tail -n 120 docs/COMPLETION_REPORT.md`
- `git status --short && rg -n "dashboard|status|audit tail|permissions show|tools list|def dispatch_cli|audit" smart_agent.py agent tests README.md -g '*.py' -g '*.md'`
- `sed -n '1,240p' agent/ui/cli_commands.py && sed -n '1,260p' agent/ui/doctor.py && sed -n '1,180p' agent/ui/audit_viewer.py`
- `sed -n '1,220p' agent/ui/permissions_dashboard.py && sed -n '1,220p' agent/safety/approvals.py && sed -n '1,160p' agent/ui/connectors.py`
- `sed -n '1,260p' agent/config/runtime.py && sed -n '1,160p' agent/ui/config_viewer.py && sed -n '1,220p' tests/test_ux_packaging.py`
- `sed -n '220,520p' tests/test_ux_packaging.py`
- `sed -n '1,220p' agent/memory/tools.py && sed -n '1,220p' agent/memory/persistent_memory.py`
- `sed -n '1,180p' agent/connectors/base.py && sed -n '1,180p' agent/connectors/status.py && sed -n '1,180p' agent/connectors/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_ux_packaging.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py dashboard --audit-limit 3 | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py status --json --audit-limit 2 | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py audit tail 2`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check && PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')" && $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `pwd && git status --short && rg -n "self_improve|self-improve|improve|backlog|proposal|propose" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '1,260p' agent/tools/low_risk/workspace_files.py`
- `sed -n '1,260p' agent/core/tool_broker.py`
- `sed -n '260,620p' smart_agent.py`
- `sed -n '1,260p' agent/workflows/self_improvement.py`
- `sed -n '1,220p' tests/test_self_improvement.py`
- `sed -n '1,220p' agent/tools/registry.py`
- `rg -n "filesystem\\.read|filesystem\\.write|filesystem\\.delete|self_improvement|ToolSpec|capability" config/capabilities.yaml tests/test_policy.py tests/test_tool_broker.py agent -g '*.py' -g '*.yaml'`
- `sed -n '620,1100p' smart_agent.py`
- `sed -n '430,530p' agent/core/tool_broker.py`
- `sed -n '1,180p' tests/test_workflows.py`
- `sed -n '1,180p' agent/workflows/files.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_self_improvement.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py improve backlog --dry-run --json | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py improve propose --json`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '818,880p' smart_agent.py`
- `sed -n '1,360p' agent/tools/personal/email.py`
- `sed -n '1,260p' agent/workflows/email_assistant.py && sed -n '1,240p' tests/test_personal_modules.py`
- `rg -n "email triage|triage|draft-reply|email\\.metadata|email\\.list_metadata|Email" tests agent README.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md docs/PROJECT_STATE.md CHANGELOG.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py email triage --dry-run --json | head -100`
- `git diff --check`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '1,360p' agent/workflows/daily_briefing.py`
- `sed -n '1,360p' agent/tools/personal/calendar.py`
- `sed -n '1,360p' agent/tools/personal/contacts.py`
- `rg -n "meeting|calendar read|contacts search|def _run_.*command|briefing" smart_agent.py agent tests README.md docs/FEATURE_REGISTRY.md docs/FEATURE_ROADMAP.md docs/FEATURE_MATURITY.md docs/PROJECT_STATE.md CHANGELOG.md`
- `sed -n '700,830p' smart_agent.py`
- `sed -n '1,180p' tests/test_workflows.py`
- `sed -n '1,280p' agent/tools/registry.py`
- `sed -n '1,260p' agent/safety/policy.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_workflows.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py meeting prep --date 2026-05-22 --title "Roadmap Sync" --dry-run --json | head -100`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '1,260p' agent/workflows/daily_briefing.py`
- `rg -n "briefing|daily_briefing|daily" smart_agent.py agent tests README.md docs/FEATURE_REGISTRY.md docs/PROJECT_STATE.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md CHANGELOG.md`
- `sed -n '1,320p' smart_agent.py`
- `sed -n '1,260p' tests/test_workflows.py`
- `sed -n '400,470p' smart_agent.py`
- `sed -n '240,620p' tests/test_workflows.py`
- `sed -n '1,260p' agent/workflows/base.py`
- `sed -n '1,260p' agent/core/tool_broker.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_workflows.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py briefing daily --weather "Phoenix, AZ" --calendar --email-metadata --web-topic "AI safety" --dry-run --json | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `git status --short --branch && git log --oneline -5`
- Read `AGENTS.md`, `CHANGELOG.md`, `docs/PROJECT_STATE.md`, `docs/FEATURE_REGISTRY.md`, `docs/FEATURE_ROADMAP.md`, and `tests/test_feature_maturity_docs.py`.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `git diff --check`
- `sed -n '1,260p' config/capabilities.yaml`
- `sed -n '1,260p' agent/safety/policy.py && sed -n '1,260p' agent/safety/validation.py && sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/config/schema.py && sed -n '1,220p' agent/config/loader.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_policy.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_ux_packaging.py::test_doctor_with_mocked_lmstudio_reachable tests/test_ux_packaging.py::test_doctor_with_lmstudio_unavailable tests/test_ux_packaging.py::test_doctor_reports_missing_model tests/test_ux_packaging.py::test_doctor_reports_invalid_config tests/test_connectors.py tests/test_connector_framework.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py connectors status weather | head -80`
- `rg -n "dry-run|dry_run|preflight|ApprovalRequest|approvals|ActionPreview|request_approval|decision_provider|auto_approve" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '1,340p' agent/ui/cli_commands.py`
- `sed -n '1,260p' agent/core/router.py`
- `sed -n '1,340p' agent/core/tool_broker.py`
- `sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/safety/action_preview.py`
- `sed -n '1,260p' agent/tools/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_preflight.py tests/test_tool_broker.py tests/test_safety_control_plane.py tests/test_ux_packaging.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py preflight "email.read_selected_thread"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py preflight "What's the weather in Phoenix?"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `git status --short --branch`
- `rg -n "read_date_range\\(|find_availability\\(|contacts\\.search\\(|read_selected\\(|list_metadata\\(|read_selected_thread\\(|summarize_thread\\(|draft_reply\\(|send_approved\\(|create_event\\(|update_event\\(|delete_event\\(" agent smart_agent.py -g '*.py'`
- `rg -n "\\.handler\\(|handler\\(\\*\\*|broker\\.registry|get\\(tool_name\\)|ToolSpec\\(|default_registry\\(|execute\\(" agent smart_agent.py -g '*.py'`
- `rg -n "~/Library|Library/Messages|Library/Mail|Keychains|Full Disk|sqlite3|Contacts\\.app|Calendar\\.app|osascript|imap|IMAP|Messages" agent smart_agent.py -g '*.py'`
- `rg -n "CalendarConnector|ContactsConnector|EmailConnector|MessagesConnector|connector\\." agent smart_agent.py -g '*.py'`
- `sed -n '720,1310p' config/capabilities.yaml`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,420p' agent/tools/personal/calendar.py`
- `sed -n '1,180p' agent/tools/personal/read_only.py`
- `rg -n "calendar read|calendar availability|calendar\\.read_date_range|calendar\\.find_availability|def _calendar|subparsers.*calendar" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '640,740p' smart_agent.py`
- `sed -n '1120,1365p' tests/test_personal_modules.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,280p' agent/tools/personal/messages.py`
- `sed -n '880,940p' smart_agent.py`
- `rg -n "messages\\.read_selected_thread|messages\\.summarize_thread|messages\\.draft_reply|messages\\.draft_from_text|draft-from-text|UNTRUSTED_MESSAGE|messages.send|Library/Messages|bulk message" tests/test_personal_modules.py config/capabilities.yaml README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md agent -g '*.py' -g '*.md' -g '*.yaml'`
- `sed -n '975,1065p' config/capabilities.yaml && sed -n '1,230p' agent/tools/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,430p' agent/tools/personal/email.py`
- `sed -n '800,900p' smart_agent.py`
- `rg -n "email\\.list_metadata|email\\.read_selected_thread|email\\.summarize_thread|email\\.draft_reply|email.send|draft reply|UNTRUSTED_EMAIL|bulk inbox|archive|move|delete" tests/test_personal_modules.py config/capabilities.yaml README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,360p' agent/tools/personal/contacts.py`
- `sed -n '740,830p' smart_agent.py`
- `rg -n "contacts\\.search|contacts\\.read_selected|contacts search|contacts read|bulk|phone|email.*redact|Contact" tests/test_personal_modules.py README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/COMPLETION_REPORT.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,260p' agent/memory/tools.py`
- `sed -n '1,260p' agent/memory/persistent_memory.py`
- `sed -n '1,260p' tests/test_memory.py`
- `rg -n "memory\\.|Memory|context injection|memory add|memory search|temporary_personal|personal_data_reference|session_context|workflow_lesson" agent tests README.md docs config -g '*.py' -g '*.md' -g '*.yaml'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_memory.py tests/test_ux_packaging.py::test_cli_memory_list_command_works`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `sed -n '1,240p' agent/workflows/research.py`
- `sed -n '240,420p' agent/workflows/research.py`
- `sed -n '280,430p' tests/test_workflows.py`
- `sed -n '1,210p' tests/test_web.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_workflows.py tests/test_web.py`
- `WEB_SEARCH_PROVIDER= BRAVE_SEARCH_API_KEY= PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py research "local AI news"`
- `sed -n '1,260p' agent/tools/low_risk/workspace_files.py`
- `rg -n "filesystem\\.|files |workspace|patch|delete|backup|UNTRUSTED_DOCUMENT" agent tests README.md docs config -g '*.py' -g '*.md' -g '*.yaml'`
- `sed -n '1,280p' tests/test_filesystem.py`
- `sed -n '1,220p' agent/tools/low_risk/git_tools.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_filesystem.py tests/test_files_workflow.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' docs/FEATURE_REGISTRY.md`
- `sed -n '1,220p' docs/FEATURE_MATURITY.md`
- `git status --short`
- `rg -n "web.fetch_url|fetch_url|research|browser|clip" agent smart_agent.py tests config/capabilities.yaml README.md docs -g '*.py' -g '*.yaml' -g '*.md'`
- `sed -n '1,260p' agent/tools/web/fetch.py`
- `sed -n '1,260p' agent/tools/registry.py`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '190,430p' agent/tools/personal/read_only.py`
- `sed -n '1,260p' agent/workflows/research.py`
- `sed -n '1140,1225p' config/capabilities.yaml`
- `sed -n '1,180p' agent/safety/policy.py`
- `sed -n '1,560p' agent/core/tool_broker.py`
- `sed -n '1,620p' agent/tools/low_risk/workspace_files.py`
- `sed -n '1,280p' tests/test_policy.py`
- `sed -n '1,260p' tests/test_personal_modules.py`
- `sed -n '1,260p' agent/config/schema.py`
- `sed -n '1,300p' agent/connectors/registry.py`
- `sed -n '1,260p' agent/connectors/status.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_browser_clipping.py tests/test_connectors.py tests/test_connector_framework.py tests/test_policy.py::test_capability_manifest_has_required_hardening_metadata -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest -q`
- Startup policy validation via `validate_startup_policy('config/capabilities.yaml')`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" smart_agent.py browser selected-tab | head -80`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' AGENTS.md`
- `sed -n '1,180p' docs/FEATURE_MATURITY.md`
- `sed -n '1,120p' docs/FEATURE_REGISTRY.md`
- `git status --short`
- `sed -n '1,320p' agent/memory/tools.py`
- `sed -n '1,260p' agent/memory/persistent_memory.py`
- `sed -n '1,260p' agent/safety/redaction.py`
- `sed -n '520,880p' smart_agent.py`
- `rg -n "memory.store|store_personal|def _run_memory|MEMORY_SCHEMAS|secret" agent tests -g '*.py'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_knowledge_capture.py -q`

## Test Status

- Internet Access release gate and roadmap reset: focused docs validation 12 passed; focused prompt/docs validation 17 passed; full suite 820 passed, 2 skipped; startup policy ok; capability manifest validation ok; command registry validation ok with 306 commands; prompt audit ok with zero active prompts and `WEB-SEARCH-PROVIDER-REGISTRY` next.
- Free-first web acquisition targeted tests: 8 passed in 0.13s.
- Focused web/acquisition/command registry tests: 27 passed in 0.19s.
- Startup policy validation after free-first web acquisition: startup policy ok.
- Capability manifest validation after free-first web acquisition: capability manifest ok (82 capabilities).
- Command registry validation after free-first web acquisition: status ok, 247 commands, no problems.
- Full suite after free-first web acquisition with bundled Codex Python runtime: 691 passed, 1 skipped in 22.39s.
- `.venv` full-suite attempt remains blocked by missing optional `reportlab`; bundled runtime should be used for PDF/full-suite coverage in this workspace.
- Prompt Tracker Maturity focused tests: 54 passed in 1.31s.
- Prompt Tracker Maturity docs/command/prompt tracker validation: 63 passed in 1.42s.
- Prompt tracker eval: 3 passed, 0 failed, 5 skipped personal-data checks.
- Prompt pack validation: `prompt-tracker-maturity-v1`, 10 prompts, status ok.
- Command registry validation: status ok, 242 commands, no problems.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok (77 capabilities).
- Full suite with bundled Codex Python runtime: 683 passed, 1 skipped in 22.34s.
- `.venv` full-suite attempt is blocked by missing optional `reportlab`; bundled runtime passed and should be used for PDF/full-suite coverage in this workspace.
- Cost-aware provider policy focused tests: 7 passed in 0.07s.
- Focused provider/prompt/maturity docs validation: 21 passed in 0.22s.
- Command registry validation: status ok, 228 commands, no problems.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok (77 capabilities).
- Full suite: 670 passed, 1 skipped in 20.82s.
- Diff whitespace check: passed.
- Session feedback focused tests: 14 passed in 0.69s.
- Focused session/command/prompt/maturity validation: 33 passed in 0.81s.
- Full suite after feedback capture: 638 passed in 19.15s.
- Startup policy validation after feedback capture: startup policy ok.
- Capability manifest validation after feedback capture: capability manifest ok (77 capabilities).
- Command registry validation after feedback capture: status ok, 210 commands, no problems.
- Final focused docs/registry validation after tracking updates: 33 passed in 0.77s.
- Diff whitespace check after feedback capture: passed.
- Dogfood suite focused tests: 8 passed in 0.30s.
- Focused dogfood/command/prompt/maturity validation: 27 passed in 0.35s.
- Dogfood CLI smoke: `dogfood list` and `dogfood run all_safe --dry-run` passed.
- Full suite after dogfood suites: 634 passed in 20.12s.
- Startup policy validation after dogfood suites: startup policy ok.
- Capability manifest validation after dogfood suites: capability manifest ok (77 capabilities).
- Command registry validation after dogfood suites: status ok, 201 commands, no problems.
- Final focused docs/registry validation after tracking updates: 27 passed in 0.33s.
- Final dogfood focused rerun after suite YAML adjustment: 8 passed in 0.22s.
- Diff whitespace check after dogfood suites: passed.
- Overnight self-improvement focused tests: 28 passed in 3.37s.
- Focused prompt/maturity/command docs validation: 19 passed in 0.19s.
- Full suite after overnight runbook: 616 passed in 18.51s.
- Startup policy validation after overnight runbook: startup policy ok.
- Capability manifest validation after overnight runbook: capability manifest ok (77 capabilities).
- Command registry validation after overnight runbook: status ok, 189 commands, no problems.
- Personal-data connector/default-enabled check after overnight runbook: passed; `tasks.draft_create` is a non-personal Action Center draft exception.
- HIGH/CRITICAL approval manifest check after overnight runbook: passed.
- Diff whitespace check after overnight runbook: passed.
- Backup/policy/packaging focused tests: 46 passed in 1.87s.
- Full suite after Backup / Restore / Migration v1: 598 passed in 17.30s.
- Startup policy validation after Backup / Restore / Migration v1: startup policy ok.
- Capability manifest validation after Backup / Restore / Migration v1: capability manifest ok.
- Command registry validation after Backup / Restore / Migration v1: status ok, 182 commands, no problems.
- Diff whitespace check after Backup / Restore / Migration v1: passed.
- Calendar approved writes focused tests: 25 passed in 0.75s.
- Full suite after calendar approved writes Action Center verification hardening: 571 passed in 14.99s.
- Startup policy validation after calendar approved writes Action Center verification hardening: startup policy ok.
- Capability manifest validation after calendar approved writes Action Center verification hardening: capability manifest ok.
- Command registry validation after calendar approved writes Action Center verification hardening: status ok, 170 commands, no problems.
- Diff whitespace check after calendar approved writes Action Center verification hardening: passed.
- Tasks connector focused tests: 11 passed in 0.93s.
- Tasks connector plus command registry focused tests: 16 passed in 0.91s.
- Full suite after Tasks / Reminders brokered draft-create pass: 570 passed in 14.74s.
- Startup policy validation after Tasks / Reminders brokered draft-create pass: startup policy ok.
- Capability manifest validation after Tasks / Reminders brokered draft-create pass: capability manifest ok.
- Command registry validation after Tasks / Reminders brokered draft-create pass: status ok, 170 commands, no problems.
- Diff whitespace check after Tasks / Reminders brokered draft-create pass: passed.
- Action Center focused tests: 14 passed in 0.79s.
- Full suite after Action Center hardening: 569 passed in 14.04s.
- Startup policy validation after Action Center hardening: startup policy ok.
- Capability manifest validation after Action Center hardening: capability manifest ok.
- Command registry validation after Action Center hardening: status ok, 170 commands, no problems.
- Diff whitespace check after Action Center hardening: passed.
- Golden Eval focused tests: 12 passed in 0.84s.
- Golden Eval + command registry focused tests: 17 passed in 0.85s.
- Focused Golden Eval CLI: 13 passed, 0 failed, 5 personal-data skips by design.
- Full suite after Golden Eval Suite: 565 passed in 12.90s.
- Post-doc focused docs/command validation: 14 passed in 0.12s.
- Startup policy validation after Golden Eval Suite: startup policy ok.
- Capability manifest validation after Golden Eval Suite: capability manifest ok.
- Command registry validation after Golden Eval Suite: status ok, 170 commands, no problems.
- Native skill validation after Golden Eval Suite: status ok, 3 valid manifests.
- Diff whitespace check after Golden Eval Suite: passed.
- Native skill manifest focused tests: 6 passed in 0.15s.
- Manifest CLI smoke: `skills validate` returned `status=ok` for one manifest, and `skills show native_skill_vetter` returned `status=ok`.
- Focused native manifest/doctor/dashboard/command validation: 22 passed in 0.38s.
- Focused validation after prompt/docs sync: 37 passed in 0.93s.
- Full suite after native skill manifest loader: 546 passed in 12.16s.
- Startup policy validation after native skill manifest loader: startup policy ok.
- Capability manifest validation after native skill manifest loader: capability manifest ok.
- Command registry validation after native skill manifest loader: status ok, 160 commands, no problems.
- Skills doctor after native skill manifest loader: status ok, one manifest validated.
- Native skill vetter focused tests: 10 passed in 0.59s.
- Focused native skill/docs/command validation: 29 passed in 0.75s.
- Full suite after Native skill vetter: 540 passed in 12.46s.
- CLI smoke for `skills vet` and `skills score`: both returned allowed brokered results with `content.status=ok`, `risk_level=LOW`, and `safe_to_port=yes`.
- Startup policy validation after Native skill vetter: startup policy ok.
- Capability manifest validation after Native skill vetter: capability manifest ok.
- Command registry validation after Native skill vetter: status ok, 157 commands, no problems.
- Native Skills Program focused docs validation: 9 passed in 0.02s.
- Full suite after Native Skills Program foundation: 530 passed in 10.38s.
- Startup policy validation after Native Skills Program foundation: startup policy ok.
- Capability manifest validation after Native Skills Program foundation: capability manifest ok (59 capabilities).
- Prompt audit after Native Skills Program foundation: 90 prompt records known; 54 complete, 33 queued, 3 blocked, next prompt `SKILL-MARKETPLACE-SURVEY`.
- Prompt Pack import/splitting focused/docs tests: 28 passed in 0.18s.
- Full suite after Prompt Pack import/splitting support: 503 passed in 10.59s.
- Startup policy validation after Prompt Pack import/splitting support: startup policy ok.
- Capability manifest validation after Prompt Pack import/splitting support: capability manifest ok.
- Prompt audit CLI after Prompt Pack import/splitting support: 86 prompt records known; 49 complete, 34 queued, 3 blocked, next prompt `NATIVE-SKILLS-FOUNDATION`.
- Diff whitespace check after Prompt Pack import/splitting support: passed.
- Prompt Ledger and Prompt Queue focused/docs validation tests: 13 passed in 0.15s.
- Full suite after Prompt Ledger and Prompt Queue tracking: 488 passed in 10.65s.
- Startup policy validation after Prompt Ledger and Prompt Queue tracking: startup policy ok.
- Capability manifest validation after Prompt Ledger and Prompt Queue tracking: capability manifest ok.
- Prompt audit CLI: 85 prompt records known; 48 complete, 34 queued, 3 blocked, next prompt `NATIVE-SKILLS-FOUNDATION`.
- Diff whitespace check after Prompt Ledger and Prompt Queue tracking: passed.
- Knowledge Capture targeted tests: 9 passed in 0.63s.
- Full suite after Knowledge Capture v1: 445 passed in 7.91s.
- Startup policy validation after Knowledge Capture v1: startup policy ok.
- Capability manifest validation after Knowledge Capture v1: capability manifest ok.
- Docs validation after Knowledge Capture v1: 7 passed in 0.01s.
- Diff whitespace check after Knowledge Capture v1: passed.
- Browser clipping focused tests: 24 passed in 1.23s.
- Full suite after Browser selected URL and clipping v1: 436 passed in 7.33s.
- Startup policy validation after Browser selected URL and clipping v1: startup policy ok.
- Capability manifest validation after Browser selected URL and clipping v1: capability manifest ok.
- Docs validation after Browser selected URL and clipping v1: 7 passed in 0.01s.
- Diff whitespace check after Browser selected URL and clipping v1: passed.
- Browser selected-tab CLI stub smoke returned a clear unavailable message and audited the disabled selected-tab capability.
- Reminders / Tasks targeted tests: 10 passed in 0.34s.
- Connector registry/list regression tests after adding tasks: 12 passed in 0.39s.
- Capability manifest validation after adding tasks: capability manifest ok.
- Tasks draft-create CLI smoke: produced a pending Action Center record and did not create a task.
- Full suite after Reminders / Tasks connector: 397 passed in 5.81s.
- Startup policy validation after Reminders / Tasks connector: startup policy ok.
- Capability manifest validation after Reminders / Tasks connector: capability manifest ok.
- Docs validation after Reminders / Tasks connector: 7 passed in 0.01s.
- Diff whitespace check after Reminders / Tasks connector: passed.
- Calendar approved writes targeted tests: 10 passed in 0.67s.
- Calendar draft-create CLI smoke: produced a pending Action Center record and did not create an event.
- Full suite after calendar approved writes: 387 passed in 5.13s.
- Startup policy validation after calendar approved writes: startup policy ok.
- Capability manifest validation after calendar approved writes: capability manifest ok.
- Docs validation after calendar approved writes: 7 passed in 0.01s.
- Diff whitespace check after calendar approved writes: passed.
- Action Center targeted tests: 10 passed in 0.48s.
- Full suite after Action Center: 377 passed in 4.37s.
- Startup policy validation after Action Center: startup policy ok.
- Capability manifest validation after Action Center: capability manifest ok.
- Docs validation after Action Center: 7 passed in 0.01s.
- Diff whitespace check after Action Center: passed.
- Action Center CLI smoke: `actions list` returned an empty actions list successfully.
- Eval harness targeted tests: 8 passed in 0.46s.
- Full suite after eval harness: 367 passed in 4.01s.
- Startup policy validation after eval harness: startup policy ok.
- Capability manifest validation after eval harness: capability manifest ok.
- Docs validation after eval harness: 7 passed in 0.01s.
- Diff whitespace check after eval harness: passed.
- Policy invariant check after eval harness: no personal-data tools enabled by default, no CRITICAL approval misconfiguration, unknown capability denied.
- Docs validation: 7 passed in 0.01s.
- Current task targeted policy tests: 17 passed in 0.22s.
- Current task startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Full suite: 297 passed in 3.09s.
- Current diagnostics targeted tests: 19 passed in 0.81s.
- Full suite: 298 passed in 3.23s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Approval/preflight targeted tests: 30 passed in 0.33s.
- Full suite: 303 passed in 2.81s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Web/research targeted tests: 38 passed in 0.20s.
- Disabled-provider CLI smoke returned a structured `web search provider is not configured` report with no fabricated sources.
- Full suite: 307 passed in 2.87s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Personal connector readiness gate full suite: 320 passed in 2.90s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Final full suite: 320 passed in 2.94s.
- Direct personal-data access and ToolBroker-bypass scans: no readiness blockers found.
- Calendar targeted personal connector tests: 52 passed in 0.69s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Full suite: 321 passed in 2.92s.
- Diff whitespace check: passed.
- Capability manifest validation: capability manifest ok.
- Contacts targeted personal connector tests: 54 passed in 0.70s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.95s.
- Diff whitespace check: passed.
- Email targeted personal connector tests: 54 passed in 0.72s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.99s.
- Diff whitespace check: passed.
- Messages targeted personal connector tests: 54 passed in 0.65s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.93s.
- Diff whitespace check: passed.
- Memory targeted tests: 13 passed in 0.13s.
- Full suite: 320 passed in 2.89s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Filesystem/workflow targeted tests: 14 passed in 0.18s.
- Full suite: 315 passed in 2.82s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.

## Blockers

None for optional SerpAPI fallback v1. Live SerpAPI smoke requires user-provided `SERPAPI_API_KEY` and `ALLOW_PAID_APIS=true`. Environment note: `.venv` lacks optional `reportlab`, so full-suite PDF coverage used the bundled Codex Python runtime.

## Decisions Made During Current Task

- Treat the Internet Access release gate as docs/tracking only; no live web calls, provider implementation, paid API use, browser automation, query-history storage, or memory writes were added.
- Supersede the stale `WEB-ACQUISITION-LAYER` queue row with the already completed `FREE-FIRST-WEB-ACQUISITION` implementation evidence.
- Make `WEB-SEARCH-PROVIDER-REGISTRY` the next prompt so future web provider work starts with metadata and governance before adding provider calls.
- Define future internet access graduation in a separate track with no CAPTCHA/anti-bot/login-wall bypass, no browser profile access, no paid defaults, and source-grounding/citation gates before maturity claims.
- Implement SerpAPI as a dedicated `web.search.serpapi` tool/capability instead of changing the default `web.search` behavior.
- Keep `web "query"` and default `research "query"` on the existing provider path; SerpAPI requires explicit `--provider serpapi`.
- Require `ALLOW_PAID_APIS=true` for SerpAPI runtime calls, even when the provider is explicitly selected, so paid/quota-limited use is deliberate.
- Treat SerpAPI results as `UNTRUSTED_WEB`, redact search queries in audit logs with the same default behavior as `web.search`, and never include `SERPAPI_API_KEY` in tool results, docs, or audit records.
- Use mocked HTTP transport in unit tests; no live SerpAPI network call was made during this task.
- Treat `web acquire "query"` as a free-first ladder that uses local cache/direct URL/domain sitemap paths and returns a clear limitation when no free source can satisfy an arbitrary query.
- Keep paid/quota-limited providers skipped by default through the existing cost policy; do not call SerpAPI, Brave, WeatherAPI, SearXNG, or any new paid provider from this task.
- Use a TTL operational cache for public acquisition results, not memory and not raw query-history storage.
- Return robots-disallowed, blocked, or CAPTCHA-like pages as unavailable with `bypass_attempted=false` instead of trying alternate bypass techniques.
- Label public webpage text as `UNTRUSTED_WEB` and fetched feed/sitemap documents as `UNTRUSTED_DOCUMENT`.
- Treat the overnight runbook as a planning gate only; `OVERNIGHT-SAFE-6H` ran only after explicit user approval in this thread, and future overnight runs require separate approval.
- Add `improve overnight-plan` as a read-only planner that uses brokered `filesystem.read` calls against tracking docs.
- Rank docs, tests, and hardening work first for overnight safe-mode.
- Exclude HIGH, CRITICAL, FORBIDDEN, personal-data, send/write, package-install, network, persistence, and approval-bypass work from overnight candidates.
- Keep commits, schedules, branches, file edits, and memory writes out of the overnight planner.
- Treat Scheduler v1 backup support as an optional manual-run workflow named `backup_create`, not a background automation or new backup capability.
- Require scheduled backups to execute through brokered `backup.create` and force `redacted=true`.
- Reject `redacted=false` in scheduled backup args before invoking any backup tool.
- Keep `backup.restore`, calendar/contact/task writes, email sends, message sends, and self-improvement commits outside scheduled automatic execution.
- Implement Backup / Restore as brokered `backup.*` tools rather than a direct filesystem CLI path.
- Keep backup archives as local redacted directory archives with `manifest.json`, per-file hashes, and an integrity hash instead of compressed opaque archives in v1.
- Include config/docs/tracking/native-skill files by default, redacted memory/action metadata by default when present, and optional captures/audit metadata.
- Exclude `.env` and key/certificate files and redact secret-looking text in copied files and metadata exports.
- Make `backup.restore` HIGH risk and approval-required; in non-interactive mode it is denied safely and audited.
- Validate backed-up `config/capabilities.yaml` against the current startup validator before restore so policy weakening, personal connector default enablement, CRITICAL approval reuse, and bypass flags are blocked.
- Treat Action Center action-id verification as part of the low-level message handoff tool guard, not only as CLI workflow policy.
- Require `messages.save_draft` and `messages.copy_draft` handlers to reject execution unless the configured Action Center has the matching approved action id.
- Require message save/copy submitted arguments to match the approved Action Center preview before the workspace write or clipboard copy path is reached.
- Keep message handoff HIGH risk, disabled by default, approval-required, no-send, no Messages database scraping, no Full Disk Access, no AppleScript/Accessibility send automation, and no memory storage.
- Treat Action Center action-id verification as part of the low-level email send tool guard, not only as CLI workflow policy.
- Require `email.send_approved` handler to reject execution unless the configured Action Center has the matching approved action id.
- Require email send submitted arguments to match the approved reviewed draft before the mock/no-provider send path is reached.
- Keep email send disabled by default and CRITICAL per-action; this hardening does not enable a live email provider.
- Preserve draft commands as Action Center-only record creation; no draft sends email, reads private Mail databases, runs in the background, or stores memory.
- Treat Action Center action-id verification as part of the low-level contact write tool guard, not only as CLI workflow policy.
- Require `contacts.update_selected` and `contacts.create` handlers to reject execution unless the configured Action Center has the matching approved action id.
- Require contact write submitted arguments to match the approved Action Center preview before the no-external-change stub is reached.
- Keep contact write tools disabled by default and CRITICAL per-action; this hardening does not enable a live native Contacts write provider.
- Preserve draft commands as Action Center-only record creation; no draft edits Contacts.app, bulk-edits, deletes contacts, or stores memory.
- Treat Action Center action-id verification as part of the low-level calendar write tool guard, not only as CLI workflow policy.
- Require `calendar.create_event`, `calendar.update_event`, and `calendar.delete_event` handlers to reject execution unless the configured Action Center has the matching approved action id.
- Keep calendar write tools disabled by default and CRITICAL per-action; this hardening does not enable a live native write provider.
- Preserve draft commands as Action Center-only record creation; no draft creates, updates, deletes, sends invites, recurrence, or stores memory.
- Treat `tasks.draft_create` as an Action Center-scoped capability, not a personal task-provider connector capability, because it only creates a local pending action and does not read or write task-provider data.
- Keep `tasks.draft_create` MEDIUM risk and default enabled so users can draft task proposals, while keeping `tasks.list`, `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` disabled by default and approval-gated.
- Route `python smart_agent.py tasks draft-create "task"` through ToolBroker before Action Center creates a pending `tasks.create` action.
- Omit task notes from draft-create by default unless explicitly allowed; do not write memory.
- Treat Unified Action Center as a review/approval queue only; do not add any direct execution path.
- Preserve exact local approval previews in `data/actions.json` so user review remains meaningful.
- Minimize sensitive bodies/drafts in action exports and lifecycle audit payloads because those records are for reporting and audit evidence, not exact approval display.
- Keep CRITICAL actions per-action only and require any future execution to go through ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger.
- Treat this task as documentation and validation only; do not add runtime features.
- Mark `SESSION-LOGGING-REPLAY` complete after adding redacted session logging/replay; use `DOGFOOD-COMMAND-SUITES` as the next prompt queue item.
- Add the requested product feature set to `docs/PROJECT_STATE.md` and `docs/FEATURE_ROADMAP.md` without marking planned items mature or implemented.
- Add an explicit Overnight Self-Improvement track and keep long-running overnight work blocked until a runbook and user approval exist.
- Implement native skill manifests as metadata-only workflow definitions, not executable plugins.
- Discover manifests from `native_skills/` and `docs/native_skills/manifests/`.
- Reject manifests with unknown capabilities, executable fields, ToolBroker-bypass language, enabled personal-data defaults, or CRITICAL approval reuse risk.
- Integrate native skill registry status into doctor/dashboard as metadata only.
- Implement native skill vetting as static analysis only; do not execute external skill scripts or imported code.
- Restrict v1 vetting input to approved workspace paths.
- Treat candidate skill content as `UNTRUSTED_DOCUMENT`.
- Register native skill vetting as LOW-risk, rate-limited, audited `native_skills.*` capabilities.
- Keep vetting separate from native manifests, loaders, installation, and enablement.
- Implement prompt pack support as SDLC metadata import/splitting only; do not execute imported prompts.
- Reject any pack mode other than `import_only` and any default execution other than `one_prompt_at_a_time`.
- Store original prompt packs under `prompts/packs/` and split individual prompt files under `prompts/queued/`.
- Preserve prompt bodies exactly after the `PROMPT:` marker.
- Append imported prompt rows to `docs/PROMPT_LEDGER.md` and `docs/PROMPT_QUEUE.md`, and append an import summary to `docs/PROMPT_AUDIT.md`.
- Keep `prompts next` dependency-aware and skip approval-gated prompts that are not ready.
- Implement prompt tracking as SDLC metadata and CLI inspection/update commands only; do not add external connectors, personal-data access, sends, writes, or policy changes.
- Use `docs/PROMPT_LEDGER.md` as the master reconstructed evidence table.
- Use `docs/PROMPT_QUEUE.md` as the ordered next-prompt source of truth.
- Use `docs/PROMPT_AUDIT.md` for best-effort completed/queued/blocked/superseded/missing-evidence review.
- Use file-based prompt records under `prompts/<status>/` for future active/completed/failed/skipped/superseded prompt details.
- Require `prompts mark-complete` to include test/docs status or `--unknown` so prompts are not silently marked complete without evidence.
- Keep the next prompt as `NATIVE-SKILLS-FOUNDATION`; block explicit send/overnight prompts until approval gates are satisfied.
- Implement Knowledge Capture v1 as a workspace JSON inbox under `./workspace/captures`, not as an Apple Notes integration.
- Use only existing brokered tools for capture operations: `filesystem.write` for capture persistence, `filesystem.read` for workspace source files, `web.fetch_url` for URL sources, and `memory.store` for explicit promotion.
- Reject secret-looking capture content before writing any capture file.
- Treat manual note captures as `TRUSTED_USER`, URL captures as `UNTRUSTED_WEB`, and file captures as `UNTRUSTED_DOCUMENT`.
- Keep captured content out of long-term memory by default; `promote-to-memory` is explicit and still goes through Memory v2 policy.
- Block personal-looking content from default memory promotion before calling `memory.store`.
- Avoid Apple Notes, private app folders, browser history, email, messages, contacts, calendar, and any personal-data connector access.
- Implement Browser v1 as an explicit URL workflow over existing brokered `web.fetch_url` and `filesystem.write` tools, not as browser automation.
- Keep native selected-tab reading as a clear stub because no safe selected-scope browser integration is implemented yet.
- Add browser connector status metadata for the URL workflow while documenting that selected-tab native access remains unavailable.
- Treat fetched URL content as `UNTRUSTED_WEB` and stored clips as `UNTRUSTED_DOCUMENT`.
- Store clips only under `./workspace` and rely on the existing workspace guard for path traversal and denied-path protection.
- Do not read browser history, cookies, sessions, form contents, bookmarks, password managers, or private browser profile databases.
- Do not submit forms, download binaries by default, or automate browser UI.
- Implement Reminders / Tasks v1 as adapter/mock first; no native Reminders provider, private database scraping, or Full Disk Access.
- Register tasks as a personal connector namespace so startup validation enforces disabled-by-default.
- Make `tasks.list` HIGH risk and approval-required because task titles can expose private data.
- Make `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` CRITICAL per-action approval tools.
- Use Action Center for task creation drafts and one-shot approved create execution.
- Keep update/complete/delete direct CLI commands brokered and approval-gated rather than adding write/send shortcuts.
- Omit task notes unless explicitly allowed and never write task contents to memory by default.
- Implement calendar approved writes v1 as Action Center drafts plus brokered execution from approved actions.
- Keep the live calendar write provider deferred; the current `calendar.create_event`, `calendar.update_event`, and `calendar.delete_event` handlers are no-external-change approved-write connector stubs.
- Require `--allow-notes` before notes/body text is included in calendar write drafts.
- Keep automatic invites disabled via `send_invites=false` in v1.
- Keep recurring events unsupported in v1.
- Decode selected calendar event tokens to capture rollback data for update/delete drafts where possible.
- Consume Action Center approval once only after `ToolBroker` reports an allowed execution.
- Implement Action Center as a safety-layer persisted review queue in `agent/safety/actions.py`, not as an executor.
- Link Action Center records to `ApprovalStore`/`ApprovalRequest` so approval state is visible in existing approval infrastructure.
- Keep one-time approval consumption as state tracking only; actual tool execution remains a future `ToolBroker` path.
- Treat `memory.write_personal`, `file.delete`, and `self_improvement.commit` as Action Center action types that map to existing brokered capabilities `memory.store_personal`, `filesystem.delete`, and `git.commit`.
- Require exact preview args for all supported Action Center action types before queuing.
- Mark irreversible actions such as sends/deletes with rollback unavailable in the preview.
- Invalidate prior approvals after an action draft is edited.
- Build the eval harness as a CLI validation layer under `agent/ui/evals.py` rather than as a new connector or workflow with new permissions.
- Keep eval results structured and write both `logs/eval_results.json` and `docs/EVAL_REPORT.md`.
- Keep personal-data evals skipped by default; no calendar/contact/email/message live reads are attempted.
- Use `ToolBroker.execute()` and `ToolBroker.dry_run()` for tool evals so policy, rate limits, approval behavior, and audit remain in path.
- Use a controlled `./workspace/eval` file for workspace read/write validation.
- Use only a non-sensitive project fact for memory eval and delete it before completion.
- Keep `docs/PROJECT_STATE.md` as the primary resume file.
- Keep `docs/FEATURE_REGISTRY.md` as the source-of-truth feature safety/status table.
- Keep `docs/FEATURE_ROADMAP.md` as the ordered batch queue.
- Keep `CHANGELOG.md` in Keep-a-Changelog style.
- Preserve uncommitted connector-framework work rather than reverting user/Codex changes.
- Validate tracking docs through pytest instead of adding a runtime docs command in this pass.
- Normalize the manifest in place rather than adding a second manifest file.
- Keep `stores_data` as a required field in addition to the new normalized schema, because existing policy/docs already use it.
- Keep runtime and connector diagnostics read-only and metadata-only; do not execute tools or probe personal data.
- Implement preflight as a brokered dry-run preview instead of a separate execution path.
- Allow exact tool/capability names in preflight so high-risk disabled capabilities can be inspected before enabling personal connectors.
- Keep preflight prompt-free and deterministic; it does not ask the LLM for tool calls.
- Keep source-grounded research deterministic and brokered; no LLM synthesis pass was added in this task.
- Expose `fetch_failures` as a first-class report field so failed or denied fetches are obvious to the caller.
- Treat pure webpage instruction-injection text as unusable evidence instead of falling back to it as an excerpt.
- Build file assistant commands as a workflow wrapper around existing `filesystem.*` and `git.diff` tools instead of direct file access.
- Label `filesystem.read` output and file workflow summaries/searches as `UNTRUSTED_DOCUMENT`.
- Do not add a `files delete` shortcut; deletion remains available only through the existing approval-gated `filesystem.delete` tool.
- Route memory CLI list/add/search/delete/export/clear/context through ToolBroker instead of the old direct memory viewer path.
- Add `memory.context` as a bounded non-personal context injection tool that audits injected memory IDs.
- Keep personal-memory context injection disabled by default; personal data still requires approval to store and is not injected without a future approved design.
- Add a personal connector readiness checklist as a prerequisite gate; it verifies safety controls only and does not approve live personal-data reads.
- Keep the calendar connector selected-range, disabled by default, and approval-required; add event-text-as-data labeling instead of altering policy or allowing event text to drive tools.
- Keep the contacts connector selected-scope, disabled by default, and approval-required; add contact-text-as-data labeling and require requested fields plus config gates before sensitive email/phone/address values are returned.
- Treat email metadata as `UNTRUSTED_EMAIL`, because sender and subject fields can contain adversarial instructions even without body text.
- Keep email draft-only output explicit: no send, delete, move, archive, approval, or memory storage side effects.
- Add `messages.draft_from_text` as a distinct brokered capability/tool for the safe manual workspace-file fallback instead of overloading `messages.draft_reply` at the CLI boundary.
- Keep live macOS Messages integration unavailable until a safe permissioned implementation path exists; do not scrape `~/Library/Messages` or request Full Disk Access.
- Build Agent Dashboard v1 as a CLI/status interface rather than a local web dashboard for now, matching the current architecture and avoiding background services.
- Keep dashboard memory visibility to counts by category/scope only; do not display stored memory content.
- Keep dashboard audit visibility to safe metadata fields; do not display raw sanitized args by default.

## Things To Verify Before Marking Complete

- Reddit + Multilingual Forum Intelligence Track planning verification is complete: forum policy docs, roadmap updates, risk/threat updates, feature registry/maturity, prompt tracking, changelog, completion report, project state, focused docs/prompt tests, startup policy validation, capability manifest validation, command registry validation, full suite, and prompt audit are updated; no runtime Reddit API calls, scraping, permanent forum storage, training, personal-data default enablement, paid API default, or CLI command changes were added.
- Internet Access release gate and roadmap reset verification is complete: docs validation, full suite, startup policy validation, capability manifest validation, command registry validation, prompt audit, web policy docs, roadmap reset, risk/threat updates, feature registry/maturity, completion report, and project state are updated; no live web calls or provider implementation occurred.
- Optional SerpAPI fallback v1 verification is complete: targeted web/research workflow tests, focused provider/command docs tests, docs validation, full suite, startup policy validation, capability manifest validation, command registry validation, completion report, project state, feature registry, maturity tracking, roadmap, risk register, threat model, test plan, release checklist, changelog, and prompt tracking are updated.
- Prompt pack parser rejects duplicate ids/orders, missing end markers, missing metadata, invalid risk levels, missing dependencies, cycles, completed-on-import, and `execute_all`.
- `validate-pack` writes no files.
- `import`/`split` write pack and queued prompt files, update ledger/queue/audit, preserve prompt bodies, and do not execute prompts.
- Full suite, docs validation, startup policy validation, capability manifest validation, diff whitespace check, completion report, project state, feature registry, feature maturity, changelog, and prompt audit are updated.
- Prompt tracking docs exist, queue rows have prompt IDs, project state references `active_prompt_id` and `next_prompt_id`, AGENTS requires prompt ledger updates, prompt CLI tests pass, full suite passes, startup policy validation passes, capability manifest validation passes, and completion report is updated.
- Knowledge Capture v1 full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Knowledge Capture trusted file marker full suite, startup policy, capability manifest validation, command registry validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, prompt tracking, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Privacy Center full suite, startup policy, capability manifest validation, command registry validation, docs validation, CLI smoke, diff whitespace check, README, changelog, command registry, feature registry, roadmap, maturity tracker, prompt tracking, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Browser selected URL and clipping v1 focused tests, full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, CLI selected-tab stub smoke, README, decision record, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Contacts approved edits full suite, startup policy, capability manifest validation, command registry validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, test plan, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Email approved send targeted tests, full suite, startup policy, capability manifest validation, command registry validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, test plan, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Messages safe handoff targeted tests, full suite, startup policy, capability manifest validation, command registry validation, docs validation, diff whitespace check, bypass/path scans, README, decision record, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, test plan, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Reminders / Tasks full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, completion report, and PROJECT_STATE completion update are complete.
- Calendar approved writes full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, completion report, and PROJECT_STATE completion update are complete.
- Action Center targeted tests passed: 10 passed in 0.48s.
- Full suite passed after Action Center: 377 passed in 4.37s.
- Startup policy validation passed after Action Center.
- Capability manifest validation passed after Action Center.
- Docs validation passed after Action Center: 7 passed in 0.01s.
- Diff whitespace check passed after Action Center.
- `actions list` CLI smoke succeeded.
- `README.md`, `CHANGELOG.md`, `FEATURE_REGISTRY.md`, `FEATURE_ROADMAP.md`, `FEATURE_MATURITY.md`, `COMPLETION_REPORT.md`, and `PROJECT_STATE.md` updated for Action Center.
- Eval harness targeted tests passed.
- Full test suite passed: 367 passed in 4.01s.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed: 7 passed in 0.01s.
- `git diff --check` passed.
- Policy invariant check passed: no personal-data tools enabled by default, no CRITICAL approval misconfiguration, unknown capability denied.
- `docs/COMPLETION_REPORT.md`, `CHANGELOG.md`, `FEATURE_REGISTRY.md`, `FEATURE_ROADMAP.md`, `FEATURE_MATURITY.md`, and `PROJECT_STATE.md` updated for eval harness.
- Full test suite passed: 359 passed in 3.61s after tracking updates.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed: 7 passed in 0.01s.
- Diff whitespace check passed.
- Feature inventory confirmed against changelog, registry, maturity tracker, roadmap, and project state.
- Personal-data tools remain disabled by default.
- HIGH-risk enabled actions still require approval.
- CRITICAL capabilities still require per-action approval with no approval reuse.
- Unknown capabilities are still denied.
- `docs/COMPLETION_REPORT.md` updated.
- `docs/PROJECT_STATE.md` status changed from `in_progress` to `complete`.
- `CHANGELOG.md`, `FEATURE_REGISTRY.md`, and `FEATURE_ROADMAP.md` reflect this tracking pass.
- Capability normalization: full suite, docs validation, startup policy, completion report, and PROJECT_STATE completion update are complete.
- Runtime doctor/dashboard polish full suite, docs validation, startup policy, completion report, and PROJECT_STATE completion update are complete.
- Approval/preflight full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Source-grounded web research full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Workspace file assistant full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Memory v2 full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Personal connector readiness gate full suite, startup policy, capability manifest validation, direct-access scans, checklist, completion report, release checklist, risk register, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Calendar read-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Contacts read-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Email draft-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Messages draft-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Daily Briefing v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, and PROJECT_STATE completion update are complete.
- Meeting Prep v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, risk register, threat model, and PROJECT_STATE completion update are complete.
- Email Triage v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, risk register, threat model, and PROJECT_STATE completion update are complete.
- Self-improvement backlog generator full suite, startup policy, capability manifest validation, docs validation, README, changelog, feature registry, roadmap, maturity tracking, completion report, and PROJECT_STATE completion update are complete.
- Agent Dashboard v1 targeted UX tests, CLI smoke, full suite, startup policy, capability manifest validation, docs validation, README, changelog, feature registry, roadmap, maturity tracking, completion report, and PROJECT_STATE completion update are complete.

## Next Queue

1. REDDIT-PROVIDER-POLICY-COMPLIANCE: Reddit provider policy and compliance scaffolding.
2. See `docs/PROMPT_QUEUE.md` for the full ordered prompt queue and blocked approval gates.

## Next Feature Set: Controlled Actions and Proactive Workflows

1. Golden eval suite + quality scorecards. Complete for local tested v1; live LM Studio/provider validation remains opt-in.
2. Unified Action Center v1. Complete in local tests; no direct execution path.
3. Tasks / Reminders connector v1. Complete in local targeted tests; native Reminders provider deferred.
4. Calendar approved writes v1. Complete in local targeted tests; live native writes deferred.
5. Contacts approved edits v1. Complete in local targeted tests; native Contacts write provider and delete deferred.
6. Email approved send v1. Complete in local targeted tests; mock provider only and real provider deferred.
7. Messages safe handoff v1. Complete in local targeted tests; automatic send remains deferred.
8. Browser selected-tab / clipping v1. Complete in local targeted tests; native selected-tab remains stubbed.
9. Notes / knowledge capture v1. Complete in local/full tests; Apple Notes integration deferred.
10. Privacy Center / data inventory v1. Complete in local/full tests; metadata-only inventory and redacted export, no personal connector reads.
11. Backup / restore / migration v1. Planned.
12. Model-router benchmark and prompt quality evals. Planned.
13. Scheduler / automation v1. Complete; manual-run only, optional redacted `backup_create`, and no hidden persistence.
14. Controlled self-improvement implementation loop. Complete in focused/full tests; commit remains approval-gated.
15. Overnight self-improvement runbook. Queued/planning-only.
16. Full release gate + maturity review. Planned after this feature set.

## Open Decisions

- Whether to commit the current accumulated post-baseline feature batch together.
- Whether to implement a native Calendar.app/EventKit write provider after a separate decision record and explicit approval.
- Whether to implement a native Reminders/EventKit reminders provider after a separate decision record and explicit approval.
- Whether to add future approval-gated personal-data evals after the Unified Action Center exists.
- Whether to add a dedicated `docs validate` CLI command later or keep validation as pytest-only.
- Whether a future dashboard should add a local web UI after CLI dashboard release-gating.

## Known Risks

- Tracking files can drift if future runs skip documentation updates.
- Personal connector work remains high risk and must stop at approval gates.
- Live validation depends on local LM Studio/provider/user configuration.
- Uncommitted work can be lost if not committed after tests pass.

## Resume Instructions For Codex

Before doing any work:

1. Read `SPEC.md`.
2. Read `docs/SDLC.md`.
3. Read `AGENTS.md`.
4. Read `docs/PROJECT_STATE.md`.
5. Read `docs/PROMPT_QUEUE.md`.
6. Read `docs/PROMPT_LEDGER.md`.
7. Read `docs/FEATURE_ROADMAP.md`.
8. Read `docs/FEATURE_REGISTRY.md`.
9. Read `docs/COMPLETION_REPORT.md`.
10. Inspect git status.
11. Identify the current task and next safe task.
12. Do not proceed past approval gates.

Before finishing any run:

1. Run the relevant tests.
2. Update `docs/COMPLETION_REPORT.md`.
3. Update `CHANGELOG.md` for user-visible changes.
4. Update `docs/FEATURE_REGISTRY.md`.
5. Update `docs/FEATURE_ROADMAP.md` if statuses changed.
6. Update `docs/PROJECT_STATE.md`.
7. Update `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and `docs/PROMPT_AUDIT.md` when prompt status changes.
8. Report files changed, commands run, tests run, results, blockers, prompt_id, next_prompt_id, and next task.

## Last Run Summary

Completed Tracker Hygiene, Indexing, and Compaction Pass. Created tracker dashboard, tracker index, maintenance guide, archive policy, and consistency report; added anchored tracker rules and navigation links; added tracker docs validation; ran full tests and release validations relevant to docs-only work; kept readiness YELLOW because clean release boundary and live/manual validation remain incomplete. Full suite passed with 1039 passed, 1 skipped. Next recommended prompt: `CONTINUE-RELEASE-HARDENING-CLEAN-BOUNDARY`.
