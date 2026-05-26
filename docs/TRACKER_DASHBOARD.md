# Tracker Dashboard

Last updated: 2026-05-25

This is the short human-readable entry point for the project trackers. It summarizes current state and points to the detailed source-of-truth files instead of replacing them.

## Current Active Work

- Active work: none after `QA-FE-BE-01` completion.
- Scope just completed: Command QA frontend/backend boundary with `QAService`, JSON-serializable API envelopes, service-backed dashboard/status output, frontend API contract docs, command registry/test matrix updates, and regression tests.
- Non-goals: no GUI/server, no background persistence, no queued prompt execution, no new connectors, no personal-data tools, no paid APIs, no HIGH/CRITICAL execution, no send/write behavior, no package install, and no safety-control bypass.

## Repo State

- Current branch: `checkpoint/large-working-tree-20260523`.
- Last known good commit: `2be398f Refactor agent prompts and project state tracking`.
- Working tree state: large dirty tree from prior feature batches; generated workspace artifacts are now narrowly ignored, but the clean release boundary remains the highest-priority process blocker.
- Release state: YELLOW after Release Hardening Loop v2.
- Release readiness score: 83/100 from `docs/release/RELEASE_READINESS_AUDIT.md`.

## Prompt State

- Current prompt: none active after `QA-FE-BE-01` completion.
- Current prompt pack: no active pack. `hermes-inspired-safe-autonomy-v1` is complete through `HERMES-13`.
- Prompt queue: standing queue still includes `news-provider-registry-status-commands` and platform follow-ups; prompt tracker audit also found stale rows/files that need reconciliation.
- Next recommended prompt: `news-provider-registry-status-commands`.

## Top Queued Or Recommended Items

1. `news-provider-registry-status-commands`: News provider registry and status inspection commands without provider calls or article fetching.
2. Brain Runtime Gateway wiring prompt: only after review, preserve LM Studio default and no-tools/tool-call behavior.
3. Native skill lockfile/pinning workflow: reviewed real `native_skills.lock` and approval-gated update path before external skill import/runtime work.
4. `PLATFORM-CAPABILITY-MANIFEST-MAPPING`: disabled manifest placeholders, validation, and ToolBroker-only mapping safeguards so bridge-advertised capabilities cannot self-enable.
5. Review source changes into a clean release candidate branch or commit series now that generated workspace artifact hygiene is documented.
6. Run full `dogfood run all_safe --session` and review the resulting session.
7. Add a static direct network/subprocess allowlist guard.
8. Run opt-in live LM Studio smoke validation.
9. Run opt-in live web/search provider validation for configured providers only.
10. Prioritize manual QA for HIGH/CRITICAL, personal-data, provider, and live commands.

## Top Blockers

1. P1: large dirty working tree prevents a clean release boundary.
2. P1: prompt tracker disagreements remain: stale SKILL rows, stale queued Reddit OAuth/config doctor file, and missing queued prompt files for some planned prompts.
3. P1/P2: live/manual validation is incomplete for the current feature breadth.
4. P2: direct network/subprocess primitives need a documented static allowlist guard.
5. P2: generated artifact hygiene needs a clean release-candidate pass.
6. P3: manual QA evidence is thinner than the command surface.
7. P3: provider setup paths need continued live/manual smoke coverage.
8. P4: `commands list | head` can surface a closed-pipe traceback.
9. P4: roadmap history has old duplicate/out-of-order numbering artifacts.
10. P4: release readiness trend is not yet tracked as a compact history.

## Most Mature Features

- ToolBroker / PolicyEngine / AuditLogger.
- Weather connector.
- Web search/fetch/research/acquisition.
- Prompt Ledger, Prompt Queue, and Prompt Pack tracking.
- Command Registry and Manual QA system.
- Action Center approval lifecycle.
- Workspace file and memory foundations.

## Least Mature Or Most Conservative Features

- Apple Ecosystem + Lead Response planning tracks.
- Apple Messaging / iMessage roadmap track.
- Reddit + Multilingual Forum Intelligence live/provider validation.
- Forum and Chinese forum live discovery.
- Native Skills marketplace survey and future skill intake.
- Brain Runtime Independence, which now has architecture docs, provider-neutral interface/registry scaffolding, deterministic mock tests, an LM Studio provider adapter, metadata-only brain status commands, disabled-by-default llama.cpp server/Ollama/llama-cpp-python in-process/MLX scaffolds, mock benchmark/eval reports, metadata-only fallback/router decisions, disabled MCP stubs, and release-gate docs. It is still conservative because normal live chat has not fully moved behind the gateway and alternate providers lack live validation.
- News Intelligence, which now has docs, disabled/planned manifest entries, safe config defaults, and provider-policy scaffolding but no runtime provider/status commands or provider calls yet.
- Cross-Platform Core + Platform Bridge work after the contract/stub scaffolding milestones.

## Commands Needing Manual QA

The command registry validates with 522 commands, but manual QA remains uneven. The highest-priority manual QA buckets are:

1. HIGH and CRITICAL approval-gated commands.
2. Personal-data read/write/send commands that are disabled by default.
3. Provider commands that need configured live services.
4. Web/research commands that rely on external sources.
5. Forum/Reddit/V2EX commands that remain opt-in.
6. Dogfood/session/review commands that should be run in a full `all_safe --session` pass.

## Features Needing Live Validation

- LM Studio no-tool chat and local model answer quality.
- SearXNG provider against a configured self-hosted instance.
- Brave Search and SerpAPI only when explicitly configured and allowed.
- Safe web fetch/research/cache against selected public URLs.
- Reddit OAuth/auth-check/search/thread flows only when configured.
- V2EX read-only API connector only when enabled.
- Chinese forum discovery through approved search/fetch paths.
- Local-model translation quality.
- Personal-data connectors and write/send paths only under explicit future approval gates.

## Docs Needing Updates

- `docs/release/RELEASE_READINESS_AUDIT.md` after each release gate.
- `docs/TRACKER_DASHBOARD.md` after major batches.
- `docs/TRACKER_CONSISTENCY_REPORT.md` during release gates.
- `docs/FEATURE_ROADMAP.md` historical duplicate/order artifacts when a targeted cleanup is approved.
- `docs/COMPLETION_REPORT.md` archive/splitting once an archive location is prepared.

## Last Test Result

Hermes-Inspired Safe Autonomy `HERMES-13` release gate completed on 2026-05-25 using `./.venv/bin/python`:

- Full suite: 1380 passed, 1 skipped.
- Focused HERMES release-gate tests: 74 passed.
- Fixture-backed `eval run --safe-autonomy`: 4 pass, 0 fail, 5 personal-data skips.
- Preview-only `dogfood run safe_autonomy_core --dry-run`: passed.
- Startup policy validation: ok via `make policy-check`.
- Capability manifest validation: ok via `make policy-check`.
- Command registry validation: ok with 484 commands.
- Prompt audit: passed after HERMES-13 with active_count 0, completed_count 206, queued_count 3, and no completed prompts missing evidence.

## Last Release Gate Status

YELLOW. Local tests and validation are green, but a clean release boundary plus broader live/manual validation are still required before treating the repo as GREEN.
