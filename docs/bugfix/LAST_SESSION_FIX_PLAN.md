# Last Session Fix Plan

Last updated: 2026-05-25

## Scope

Fix only safe, scoped issues found while reviewing the latest session and related bug artifacts. This plan is intentionally narrow because the latest recorded session had no command failures or feedback.

## Priority Fixes

| Priority | Fix | Expected files | Risk | Tests | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Document latest session review and confirmed bug status. | `docs/bugfix/LAST_SESSION_REVIEW.md`, `docs/bugfix/LAST_SESSION_FIX_PLAN.md` | SAFE | `tests/test_last_session_bugfix_docs.py` | complete |
| 2 | Reconcile prompt-state drift caused by the interrupted `HERMES-09` handoff. | `docs/PROJECT_STATE.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_LEDGER.md`, `docs/PROMPT_AUDIT.md`, `docs/TRACKER_DASHBOARD.md` | SAFE | prompt audit | in progress |
| 3 | Verify existing setup-command regressions for `BUG-0001` and `BUG-0002`. | existing regression tests | LOW | `tests/regressions/test_bug_0001_setup_command.py`, `tests/regressions/test_bug_0002.py` | in progress |
| 4 | Mark the active bugfix prompt complete with evidence. | prompt tracking files | SAFE | prompt audit | pending |
| 5 | Restore/resume `HERMES-09` only after this prompt is complete, because the user confirmed it was skipped accidentally. | prompt tracking files | SAFE/MEDIUM | HERMES-09 targeted tests when implemented | pending |

## Deferred Items

- No new latest-session runtime bug was found to fix.
- No natural-language misunderstanding was available for regression coverage because the latest session had no user feedback.
- Broader release-boundary cleanup remains outside this prompt.
- HERMES-09 implementation remains outside this bugfix prompt and should resume next.

## Approval Gates

Stop before any work that would require:

- package installation
- background persistence
- external skill execution
- plugin runtime execution
- personal-data access
- send/write behavior
- policy, approval, permission, audit, or ToolBroker relaxation

No approval gate has been hit in this bugfix plan.
