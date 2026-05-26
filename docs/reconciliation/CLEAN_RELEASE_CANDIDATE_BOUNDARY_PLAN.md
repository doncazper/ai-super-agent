# Clean Release Candidate Boundary Plan

Last reconciled: 2026-05-25

## Current Boundary

- Branch: `checkpoint/large-working-tree-20260523`
- Last pushed commit observed locally: `2be398f Refactor agent prompts and project state tracking`
- Worktree: dirty and mixed across feature tracks, prompt packs, docs, tests, and generated reports.
- Safe-to-push now: no. A separate safe commit/push review is required.

## Files Safe To Consider For Commit

- Source code and tests created intentionally by completed prompt batches.
- Prompt pack source files only after confirming they contain exact intended prompt bodies and no secrets/private data.
- Redacted docs and tracker updates.
- `.env.example` placeholder-only changes.
- `.gitignore` hygiene changes.

## Files To Exclude Or Review Carefully

- `.env`, token files, OAuth caches, private keys, SQLite/database files.
- Raw session/audit logs.
- Reports that include raw personal data or unredacted command output.
- Disposable QA workspaces, caches, model outputs, and generated media outputs.
- Any prompt pack reconstructed without clear source evidence.

## Suggested Commit Groups

1. Prompt tracking and reconciliation docs.
2. Command registry/maturity/tracker updates.
3. Natural-language command understanding code/tests/docs.
4. Command QA sandbox code/tests/docs.
5. Brain/Hermes/Native Skill prompt-pack artifacts.
6. Generated reports/docs that are redacted and intentionally tracked.
7. Gitignore/config hygiene.

## Required Before Commit

- Full test suite.
- Startup policy validation.
- Capability manifest validation.
- Command registry validation.
- Prompt audit.
- Best-effort or external secret scan.
- `git diff --check`.
