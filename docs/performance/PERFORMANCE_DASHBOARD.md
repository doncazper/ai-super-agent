# Performance Dashboard

`PERF-10` adds read-only performance dashboard and QA integration summaries over local redacted artifacts.

## Commands

- `python smart_agent.py perf dashboard`
- `python smart_agent.py perf status`
- `python smart_agent.py perf next-fix`
- `python smart_agent.py perf trends`

These commands only read local redacted reports. They do not execute scans, benchmarks, tests, live providers, patch plans, patches, package installs, commits, or pushes.

## Dashboard Sections

- latest scan summary
- top bottlenecks
- slowest safe commands
- slowest tests
- regression warnings
- baseline status
- recommendations
- patch plan candidates
- feature maturity impact
- next safe action

## QA Integration

The dashboard is designed as a read-only backend summary future QA dashboards can consume. It surfaces performance evidence and next safe actions, while actual QA command execution remains owned by the QA sandbox service and command safety tiers.
