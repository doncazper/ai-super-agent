# Canonical State Integration

Status: CANON-09 plan-only integration.

Prompt tracking keeps the human evidence trail. Canonical runtime state provides a compact machine-readable view of active work for dashboards and handoffs.

## Ownership

- `prompts/active/*.md` identifies the active prompt file.
- `docs/PROMPT_LEDGER.md` records prompt history and evidence.
- `docs/PROMPT_QUEUE.md` records intended order and current queue state.
- `docs/PROMPT_AUDIT.md` records reconciliation findings.
- Canonical state reads those files and reports conflicts; it does not replace them.

## Required Invariants

- Keep at most one active prompt.
- Move completed prompt files to `prompts/completed/`.
- Keep queued prompts queued unless evidence shows they ran.
- Keep completed prompts out of the active queue.
- Preserve prompt bodies exactly when importing packs.
- Use `needs_review` instead of guessing when evidence is incomplete.

## Recovery Guidance

When canonical state and prompt trackers disagree:

1. Inspect the active/completed/queued prompt files.
2. Inspect `docs/COMPLETION_REPORT.md` for evidence.
3. Inspect tests/docs/changelog/feature registry for supporting evidence.
4. Make the smallest anchored tracker edit.
5. Run prompt audit and relevant docs validation.

Do not auto-run recovered prompts.
