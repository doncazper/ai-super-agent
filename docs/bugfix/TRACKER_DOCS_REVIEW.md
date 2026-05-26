# Prompt Tracker, Docs, And Maturity Bug Review

Prompt ID: `CODEBUG-06`
Date: 2026-05-25

## Scope

Review prompt tracker state, dense tracker consistency, docs validation signals, and maturity evidence for small anchored fixes during the CODEBUG controlled batch.

## Non-Goals

- No broad tracker rewrite.
- No deletion of historical prompt details.
- No maturity upgrades without evidence.
- No queued prompt auto-run outside the active CODEBUG batch.
- No runtime feature changes.

## Evidence Reviewed

- `docs/PROMPT_QUEUE.md`
- `docs/PROMPT_LEDGER.md`
- `docs/PROMPT_AUDIT.md`
- `docs/TRACKER_CONSISTENCY_REPORT.md`
- `docs/FEATURE_MATURITY.md`
- `docs/FEATURE_REGISTRY.md`
- prompt files under `prompts/queued/`, `prompts/active/`, and `prompts/completed/`
- `./.venv/bin/python smart_agent.py prompts audit`

## Findings

| Finding | Severity | Status | Evidence | Action |
|---|---:|---|---|---|
| Prompt audit one-active rule is healthy | n/a | verified | `prompts audit` reported `active_count: 1` with `CODEBUG-06`. | No fix needed. |
| Completed prompts have evidence | n/a | verified | `prompts audit` reported `completed_missing_evidence: []`. | No fix needed. |
| CODEBUG queue rows lagged prompt state | P2 | fixed | `docs/PROMPT_QUEUE.md` still showed CODEBUG-01 through CODEBUG-05 as queued while completed prompt files existed and `prompts audit` listed them complete. | Anchored queue-row update for CODEBUG-01 through CODEBUG-06 only. |
| `CODEBUG-07` is queued without evidence | n/a | expected | `prompts audit` reports `queued_without_evidence: ["CODEBUG-07"]` while CODEBUG-07 has not run yet. | Leave queued. |
| Older tracker stale rows remain outside CODEBUG scope | P3 | deferred | Prompt audit docs still carry historical notes about stale native-skill rows and other long-lived tracker disagreements. | Do not broadly rewrite; keep for a dedicated tracker-reconciliation prompt. |

## Tests And Validation

- `./.venv/bin/python smart_agent.py prompts audit`: active_count 1 (`CODEBUG-06`), completed_count 212, completed_missing_evidence empty, queued_count 5.
- `./.venv/bin/python -m pytest -q tests/test_prompt_tracking.py tests/test_prompt_pack.py tests/test_prompt_tracker_maturity.py tests/test_promptops_workbench.py tests/test_tracker_hygiene_docs.py tests/test_productization_audit_docs.py tests/test_feature_maturity_docs.py tests/test_command_registry.py`: 66 passed.

## Safety Notes

The only tracker mutation was an anchored status/evidence correction for the active CODEBUG controlled batch. No prompt bodies were summarized, deleted, or rewritten, and no queued prompt was marked complete without evidence.
