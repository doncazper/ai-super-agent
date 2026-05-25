# Tracker Archive Policy

Last updated: 2026-05-25

Archiving is allowed only to reduce active-tracker navigation cost. It must not erase evidence.

## Can Be Archived

- Old completion report sections after they are summarized and linked.
- Historical prompt records after ledger/audit summaries retain the prompt ID, status, evidence, and archive path.
- Old release-gate reports once the current release dashboard links them.
- Closed bug reports after their fix, regression evidence, and final status are recorded.
- Old session/dogfood/eval reports that are no longer active release evidence.
- Historical generated artifacts that are reproducible and not source-of-truth.

## Must Remain Active

- Current `docs/PROJECT_STATE.md` status.
- Current active prompt and next prompt.
- Open blockers and release readiness state.
- Current command registry and command test matrix.
- Current feature registry and feature maturity rows.
- Current risk and threat model entries.
- Latest release checklist and completion evidence.
- Any unresolved P0/P1/P2 issue.

## Archive Rules

1. Move historical content to an `archive/` or date-scoped docs location only after the active tracker links to it.
2. Preserve prompt IDs, command IDs, feature IDs, bug IDs, dates, and test evidence.
3. Mark archived content as historical.
4. Do not rewrite historical conclusions unless adding a clearly dated correction note.
5. Do not delete useful detail unless it is duplicated in the archive and linked from the active tracker.
6. Do not move private, secret, or personal data into long-term archive paths.
7. Keep generated/local runtime artifacts out of release branches unless explicitly approved.

## Suggested Archive Layout

```text
docs/archive/
  completion_reports/YYYY/
  prompt_tracking/YYYY/
  release_gates/YYYY/
  bugs/YYYY/
  dogfood/YYYY/
```

This layout is not created by this pass. It is a future low-risk cleanup candidate after the release boundary is decided.

## Evidence Links

Every archive move should leave a short active-tracker note with:

- What moved.
- Why it moved.
- Where it moved.
- Which IDs/dates are covered.
- Which validation or release gate used the archived evidence.

