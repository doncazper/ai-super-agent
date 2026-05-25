# Tracker Dashboard

Last updated: 2026-05-25

This is the short human-readable entry point for the project trackers. It summarizes current state and points to the detailed source-of-truth files instead of replacing them.

## Current Active Work

- Active work: Native Skill System Hardening pack complete through `SKILL-10` local release gate.
- Scope: metadata-only roots, manifests, dependency gating, provenance/trust, lock verification, vetting, profiles, compatibility, conflicts, harness/dogfood/evals, docs generator/catalog, release-gate docs, and tracker updates.
- Non-goals: no external skill installation, marketplace enablement, external skill/script execution, dependency installation, provider/connector calls for skill metadata checks, plugin runtime execution, personal-data skill enablement, memory write, permission grant, or safety-control bypass.

## Repo State

- Current branch: `checkpoint/large-working-tree-20260523`.
- Last known good commit: `e1dfdbf Add command registry and documentation tracking`.
- Working tree state: large dirty tree from prior feature batches; generated workspace artifacts are now narrowly ignored, but the clean release boundary remains the highest-priority process blocker.
- Release state: YELLOW after Release Hardening Loop v2.
- Release readiness score: 83/100 from `docs/release/RELEASE_READINESS_AUDIT.md`.

## Prompt State

- Current prompt: none active; `SKILL-01` through `SKILL-10` completed locally after explicit user request.
- Current prompt pack: `native-skill-system-hardening-v1` complete.
- Prompt queue: `news-provider-registry-status-commands` is next in prompt tracking; native-skill-specific follow-up should be reviewed lockfile/pinning workflow or a clean release-candidate boundary prompt.
- Next recommended prompt: `news-provider-registry-status-commands`.

## Top Queued Or Recommended Items

1. `news-provider-registry-status-commands`: News provider registry and status inspection commands without provider calls or article fetching.
2. Native skill lockfile/pinning workflow: reviewed real `native_skills.lock` and approval-gated update path before external skill import/runtime work.
3. `PLATFORM-CAPABILITY-MANIFEST-MAPPING`: disabled manifest placeholders, validation, and ToolBroker-only mapping safeguards so bridge-advertised capabilities cannot self-enable.
4. Review source changes into a clean release candidate branch or commit series now that generated workspace artifact hygiene is documented.
5. Run full `dogfood run all_safe --session` and review the resulting session.
6. Add a static direct network/subprocess allowlist guard.
7. Run opt-in live LM Studio smoke validation.
8. Run opt-in live web/search provider validation for configured providers only.
9. Prioritize manual QA for HIGH/CRITICAL, personal-data, provider, and live commands.
10. Improve `commands list | head` closed-pipe behavior.

## Top Blockers

1. P2: large dirty working tree prevents a clean release boundary.
2. P2: live/manual validation is incomplete for the current feature breadth.
3. P2: direct network/subprocess primitives need a documented static allowlist guard.
4. P3: manual QA evidence is thinner than the command surface.
5. P3: provider setup paths need continued live/manual smoke coverage.
6. P4: `commands list | head` can surface a closed-pipe traceback.
7. P4: generated artifact hygiene now has narrow ignore rules and passing regression coverage; keep ignored-output review green.
8. P4: roadmap history has old duplicate/out-of-order numbering artifacts.
9. P4: dense append-only trackers need regular summary/index refreshes.
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
- News Intelligence, which now has docs, disabled/planned manifest entries, safe config defaults, and provider-policy scaffolding but no runtime provider/status commands or provider calls yet.
- Cross-Platform Core + Platform Bridge work after the contract/stub scaffolding milestones.

## Commands Needing Manual QA

The command registry validates with 428 commands, but manual QA remains uneven. The highest-priority manual QA buckets are:

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

News capability manifest/provider-policy validation on 2026-05-25 using `./.venv/bin/python`:

- Full suite: 1119 passed, 1 skipped.
- News capability/provider-policy regression: 10 passed.
- Focused News/docs/maturity regression: 28 passed.
- Startup policy validation: ok via `make policy-check`.
- Capability manifest validation: ok via `make policy-check`.
- Command registry validation: ok with 398 commands.
- Prompt audit: active_count 0, completed_count 170, queued_count 3, next_prompt_id `news-provider-registry-status-commands`.

## Last Release Gate Status

YELLOW. Local tests and validation are green, but a clean release boundary plus broader live/manual validation are still required before treating the repo as GREEN.
