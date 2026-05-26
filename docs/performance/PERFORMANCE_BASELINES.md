# Performance Baselines

`PERF-08` adds redacted local baseline and regression tracking for performance reports.

## Commands

- `python smart_agent.py perf baseline create`
- `python smart_agent.py perf baseline compare`
- `python smart_agent.py perf regressions`

Optional controls:

- `perf baseline create --notes "short note"`
- `perf baseline compare --baseline <baseline_id> --tolerance 0.2`
- `perf regressions --tolerance 0.2`

## Stored Metadata

Baselines are stored under `reports/performance/baselines/` and include:

- command timings
- startup timings
- test durations
- finding counts
- branch
- commit
- Python version
- platform
- notes
- source report id/type

Baselines must not store raw prompts, raw provider content, raw command output, raw pytest output, secrets, personal data, search history, or model output.

## Regression Comparison

Comparison uses relative variance tolerance and ranks local timing/finding-count regressions. It is evidence for review, not an automatic optimization trigger.

No live providers, paid APIs, model downloads, background services, personal-data tools, patches, commits, or pushes are run by baseline commands.
