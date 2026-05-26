# Codebase Bug Review Summary

Prompt pack: `codebase-bug-review-and-hardening-v1`
Prompt IDs: `CODEBUG-01` through `CODEBUG-08`
Date: 2026-05-25

## Executive Summary

The controlled CODEBUG batch completed locally with one scoped code fix and green validation. The batch did not add major features, install packages, remove tests, enable personal-data tools, commit, or push.

## Bugs Found

- `CODEBUG-P2-004`: `commands list` produced a Python `BrokenPipeError` traceback when piped into `head`.
- `CODEBUG-P2-001`: `smart_agent.py docs validate` is not a real docs validator and falls through to chat.
- `CODEBUG-P2-003`: connector/status UX is conservative but verbose and can surface stale historical errors.
- Memory policy ambiguity: `memory.store_personal` is HIGH and approval-required but appears default-enabled in static capability metadata; needs dedicated policy review.
- Static scan follow-up: approved subprocess and cache-deletion call sites need an allowlist-based review.

## Bugs Fixed

- Fixed `BrokenPipeError` traceback at the top-level CLI boundary.
- Added regression coverage for command registry output piped to `head`.
- Reconciled CODEBUG prompt queue rows with actual prompt completion evidence.

## Bugs Deferred Or Blocked

- Clean release-candidate boundary remains P1.
- Broad prompt tracker stale-row/orphan-file reconciliation remains P1/P2.
- Dedicated docs validation command remains P2.
- Connector summary UX remains P3.
- Subprocess/file-deletion allowlist review remains P2/P3.

## Regression Tests Added

- `tests/test_command_registry.py::test_command_registry_list_handles_closed_pipe_without_traceback`

## Test Summary

- CODEBUG-02 safety tests: 61 passed.
- CODEBUG-03 command registry tests: 6 passed.
- CODEBUG-04 core/runtime/brain tests: 148 passed.
- CODEBUG-04 full suite: 1387 passed, 1 skipped.
- CODEBUG-05 connector/workflow tests: 440 passed.
- CODEBUG-06 prompt/tracker/docs tests: 66 passed.
- CODEBUG-08 final full suite: 1387 passed, 1 skipped.
- CODEBUG-08 docs-focused tests: 43 passed.
- Safe eval: 40 passed, 0 failed, 6 skipped.
- All-safe dogfood dry-run: status ok, 8 dry-run commands skipped by design.

## Validation Summary

- `make policy-check`: passed startup policy and capability manifest validation.
- `smart_agent.py commands validate`: passed with 484 commands and no problems.
- `smart_agent.py prompts audit`: final audit reported active_count 0, completed_count 215, completed_missing_evidence empty, queued_count 3.
- Dedicated docs validation command: not available.

## Remaining Blockers

1. Clean release-candidate boundary for the large dirty worktree.
2. Prompt tracker reconciliation beyond the CODEBUG rows.
3. Real docs validation command or documented replacement.
4. Approved subprocess/file-deletion allowlists.
5. Broader manual/live validation.

## Recommended Next Prompt

Run a focused release-hardening prompt: **Clean Release Candidate Boundary and Prompt Tracker Reconciliation**.

After that, return to the standing feature queue with `news-provider-registry-status-commands`.
