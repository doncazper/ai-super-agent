# Docs Wiring Reconciliation

Last reconciled: 2026-05-25

## Findings

- README, tracker dashboard/index, feature registry, feature maturity, command registry, completion report, and changelog all exist and are actively used.
- This reconciliation added an explicit source-of-truth hierarchy because summary trackers and productization docs can drift from code/tests and capability manifest reality.
- `docs/PROJECT_STATE.md` and `docs/COMPLETION_REPORT.md` must be updated at the end of this pass so durable resume state does not remain `active`.
- `docs/TRACKER_DASHBOARD.md` should remain a summary view, not the canonical truth when it conflicts with code/tests/ledger evidence.

## Fixes Made

- Added the reconciliation report set under `docs/reconciliation/`.
- Corrected prompt queue/ledger drift for completed prompt packs.
- Recorded Media/Secrets pack source-file recovery as `needs_review`, not completed.

## Deferred

- A docs-link validation command was not found during this pass. Docs coverage currently comes from focused tests, command registry validation, and full test suite.
- README top-level links looked broadly current; no broad README rewrite was done.
