# Performance Finding Schema

Performance findings are normalized records that can be written as JSON or summarized as Markdown.

## Required Fields

- `finding_id`: stable ID derived from category, path, line, and title.
- `category`: scan category such as `startup_import`, `missing_timeout`, or `slow_test`.
- `severity`: P0, P1, P2, P3, or P4.
- `title`: short human-readable issue name.
- `description`: concise explanation of the suspected bottleneck.
- `evidence`: one or more evidence records with path, line, command, metric, or excerpt.
- `likely_cause`: best current explanation.
- `recommended_fix`: proposed fix direction.
- `effort`: small, medium, large, or needs investigation.
- `risk_level`: SAFE, LOW, MEDIUM, HIGH, or CRITICAL.
- `tests_required`: tests needed before applying a fix.
- `docs_required`: docs to update if a fix changes user-visible behavior.
- `status`: open, planned, needs_review, fixed, false_positive, or deferred.

## Evidence Limits

Evidence must be redacted, short, and source-grounded. Reports must not include raw secrets, environment values, full logs, personal-data content, or large generated artifacts.

## Stable IDs

Stable finding IDs should change only when the underlying category/path/line/title changes. This allows baselines and regression checks to compare repeated scans.
