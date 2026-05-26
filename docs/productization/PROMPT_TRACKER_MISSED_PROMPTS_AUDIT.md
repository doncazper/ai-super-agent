# Prompt Tracker Missed Prompts Audit

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25

## Summary

The prompt tracker is useful, but it currently has disagreements across `docs/PROMPT_QUEUE.md`, `docs/PROMPT_LEDGER.md`, `docs/PROMPT_AUDIT.md`, and the prompt filesystem. The safest interpretation is that most major recent packs completed with evidence, but several tracker rows are stale or missing prompt files.

## Prompt Packs Imported

| Prompt pack | Evidence | Classification | Notes |
|---|---|---|---|
| `prompt-tracker-maturity-v1` | Ledger, completed prompt files, registry, tests | completed_verified | PTM-01 through PTM-10 show broad evidence |
| `agent-dna-cloneability-v1` | Docs, changelog, registry, maturity | completed_verified | Docs/provenance only |
| `agent-runtime-orchestration-v1` | ORCH prompt evidence, runtime modules/tests/docs | completed_verified | Local metadata runtime |
| `native-skill-system-hardening-v1` | Completed prompt files, registry, maturity, tests | completed_verified but tracker-stale | Queue/ledger still contain stale SKILL rows |
| `brain-runtime-independence-v1` | BRAIN-01 through BRAIN-11 evidence | completed_verified | LM Studio preserved, gateway added |
| `hermes-inspired-safe-autonomy-v1` | HERMES-01 through HERMES-13 evidence | completed_verified | Safe autonomy remains gated |
| `apple-platform-compatibility-v1` | Prompt pack file present | needs_review | Pack file evidence only; completion not verified |
| `codebase-bug-review-and-hardening` | Prompt pack file present | needs_review | No completion classification verified in this audit |
| `command-qa-sandbox-self-heal` | Prompt pack file present | needs_review | No completion classification verified in this audit |
| `natural-language-command-understanding` | Prompt pack file present | needs_review | No completion classification verified in this audit |

## Prompt Status Classes

| Class | Prompt examples | Evidence |
|---|---|---|
| completed_verified | `BRAIN-01` through `BRAIN-11`, `HERMES-01` through `HERMES-13`, `PTM-01` through `PTM-10`, `SKILL-01` through `SKILL-10` | Completed prompt files, completion report, changelog, tests, docs |
| likely_complete | None separated during this audit | Strong items were already in completed_verified or left needs_review |
| partial | News Intelligence track | News roadmap and manifest exist, but runtime provider/status commands remain queued |
| active | `MATURITY-AUDIT-01` at audit start | Active prompt file and queue/ledger row |
| queued_not_started | `news-provider-registry-status-commands`, `PLATFORM-CAPABILITY-MANIFEST-MAPPING`, `PLATFORM-STARTUP-LAZYLOAD-GUARDRAILS` | Queue/ledger rows, no completion evidence |
| failed | None verified | `prompts/failed/` empty during audit |
| blocked | None verified | No current blocked prompt row verified |
| skipped | None verified | `prompts/skipped/` empty during audit |
| superseded | Older prompt tracker concepts | Audit narrative references superseded work, but prompt directory has no superseded files |
| stale | `news-capability-manifest-provider-policy` listed as queued in `PROMPT_AUDIT`, stale SKILL rows in queue/ledger | Other trackers and evidence show completion |
| orphaned_file | `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md` | Queued file remains although completed evidence exists elsewhere |
| missing_file | Queued news/platform follow-up rows | Queue/ledger entries exist but matching queued prompt files were not found |
| no_evidence | Pack files that are present but not linked to completion evidence | Needs review before running or archiving |
| needs_review | Apple compatibility, command QA/self-heal, natural language command understanding packs | Prompt pack file exists; completion state not verified |

## Tracker Inconsistencies

1. `docs/PROMPT_AUDIT.md` still listed `news-capability-manifest-provider-policy` as queued in one section even though ledger/project state/completion evidence show it completed.
2. `docs/PROMPT_QUEUE.md` and `docs/PROMPT_LEDGER.md` contain stale `SKILL-*` queued rows despite completed prompt files and native skill release-gate evidence.
3. `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md` appears stale because the Reddit OAuth/config doctor has completed evidence in trackers and docs.
4. Queue/ledger entries for news/platform follow-ups do not consistently have corresponding files under `prompts/queued/`.

## Top Prompts To Run Next

1. `news-provider-registry-status-commands`
2. `PLATFORM-CAPABILITY-MANIFEST-MAPPING`
3. `PLATFORM-STARTUP-LAZYLOAD-GUARDRAILS`
4. Prompt tracker reconciliation and stale file cleanup
5. All-safe dogfood release evidence pass

## Prompts Recommended To Supersede Or Archive

- Stale queued `SKILL-*` rows should be marked completed or superseded with links to completed evidence.
- `prompts/queued/REDDIT-OAUTH-CONFIG-DOCTOR.md` should be archived or superseded after confirming the completed prompt file and tracker row.
- Pack files with no execution evidence should remain unrun and be classified as `needs_review`, not completed.

## Exact Next Prompt Recommendation

`news-provider-registry-status-commands`

