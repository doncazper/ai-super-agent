# Performance Baseline Strategy

Baselines compare safe local scan, startup, benchmark, and test-profiler results across time. Baselines are advisory until release gates decide their impact.

## Baseline Contents

- Branch and commit when available.
- Python version and platform.
- Command timing metrics.
- Startup/import timing metrics.
- Test duration summaries.
- Finding counts by severity/category.
- Notes and run conditions.

## Storage

Baselines live under `reports/performance/baselines/`. Reports must be redacted and avoid raw personal data, secrets, environment values, and full command output.

## Regression Rules

- Compare medians or stable summary metrics with a variance tolerance.
- Rank regressions by user impact, risk, and confidence.
- Treat flaky timing as `needs_review`, not a blocker.
- Prefer trends over one-off timing spikes.

## Release Use

Release gates can use baselines to decide whether to keep hardening, file bugs, or proceed. A missing baseline is not a release failure, but it should be called out.
