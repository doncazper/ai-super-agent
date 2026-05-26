# Blocked Prompt Execution Plan

Prompt ID: `RUN-DIRTY-TREE-BLOCKED-PROMPTS-IN-ORDER-01`

Date: 2026-05-26

## Current Decision

Do not run additional feature prompts in this pass. The duplicate-file and remote/main blockers are resolved, but the worktree is not clean: the Daydream pack was imported and queued in the previous run and remains uncommitted.

Running another large pack now would mix unrelated prompt-pack import state with new feature work, making prompt evidence, release gates, and any later Git gate harder to audit.

## Correct Order After Clean Boundary

| Order | Candidate | Current Status | Prerequisites | Safe To Run Now? | Reason |
|---:|---|---|---|---|---|
| 1 | `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01` | queued | Current dirty tree reviewed | no, this audit did not stage/commit | Required to checkpoint Daydream import/tracker changes before more feature packs |
| 2 | Bug Intelligence and Failure Capture | not imported/run | clean boundary | no | Captures failures, wrong answers, launch bugs, and future pack blockers before more feature work |
| 3 | Agent Memory Kernel / Tracker Intelligence | not imported/run | clean boundary; Bug Intelligence | no | Improves source-of-truth, tracker drift detection, evidence graph, and handoff quality |
| 4 | Self-Healing Rollback Maturity | not imported/run | clean boundary; Bug Intelligence; Memory Kernel preferred | no | Uses bug/repro/regression concepts better after Bug Intelligence and benefits from Memory Kernel evidence |
| 5 | AI Ecosystem Intelligence v2 | not imported/run | clean boundary; tracker/memory stability | no | v2 is current; source/provider intelligence should wait for tracker/memory stability |
| 6 | Authorized Deep Scan | not imported/run | clean boundary; AIHUB/source context | no | Complements AIHUB and web/source acquisition safely |
| 7 | Writing Naturalizer | not imported/run | clean boundary; safety policy review | no | Mostly independent, but safer after Bug/Memory tracking exists |
| 8 | Daydream Lab Idle Research | imported/queued only | clean boundary; Bug Intelligence; Memory Kernel; AIHUB; AuthScan; Performance/QA/Self-Heal integrations available | no | Imported prompt bodies should stay queued; Daydream should not execute early |

## Superseded Or Stale Items

- AI Ecosystem Intelligence v1: do not run if present later; v2 is the current pack.
- `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md`: stale queued file because completed evidence exists in `prompts/completed/REDDIT-OAUTH-CONFIG-DOCTOR.md`.
- Global launcher self-repair: already completed; user clarified it is built.
- Canonical runtime gateway hardening: already completed.

## Stop Conditions For The Next Runner

- Any likely real secret in tracked/staged files.
- Any `* 2.*` duplicate file that is not proven exact duplicate or safely quarantined.
- Dirty tree containing unrelated feature work.
- Failing `git diff --check`, secret scan, git preflight, command registry validation, policy-check, or targeted tests.
- Missing prompt pack source file.
- Prompt pack requiring package install, model download, live provider access, paid API, personal-data access, background service, or approval gate.
- Any ambiguity about whether queued/completed prompt evidence is stale.

## Recommended Next Action

Run `CLEAN-COMMIT-AND-REMOTE-MAIN-DECISION-01` or an equivalent safe commit-boundary prompt to stage, scan, commit, and push the Daydream import/tracker changes if clean. After that, start with Bug Intelligence unless validation or dependency evidence blocks it.
