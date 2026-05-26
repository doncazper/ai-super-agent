# Self-Healing Loop Policy

The self-healing loop is evidence-based and conservative. It may propose fixes from QA failures, but it must not become autonomous release engineering.

## Allowed

- Create patch plans from ranked bugs.
- Identify scoped files and required tests.
- Generate or update regression tests for confirmed bugs.
- Apply low-risk local patches only when the bug and fix are narrow.
- Run targeted tests and record results.
- Update docs and trackers for any fix attempted.

## Forbidden

- No policy weakening.
- No disabling tests to pass.
- No package installation.
- No background persistence.
- No commits, pushes, merges, or pull requests without explicit approval.
- No personal-data access.
- No send/write behavior enablement.
- No broad rewrites from ambiguous bug evidence.

## Patch Plan Requirements

Each patch plan must record `patch_id`, `bug_id`, `severity`, `allowed_to_patch`, `reason`, `branch_name`, `files_expected`, `tests_required`, `docs_required`, `risk`, `rollback_plan`, and `human_review_required`.

P0/P1 safety bugs may receive plans immediately, but automatic patching is allowed only when the fix is obviously local and safer than leaving the bug. Otherwise, the loop stops for human review.
