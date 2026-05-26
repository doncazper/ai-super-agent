# Performance Scanner Track

Status: specified in PERF-01.

The Performance Bottleneck Scanner track adds a safe, local-first way to find likely performance risks before they become release blockers. It must prefer static analysis, dry-runs, fixture parsing, and bounded local subprocess measurements over broad profiling or live-provider checks.

## Scope

- Find code and workflow bottlenecks in startup, CLI dispatch, command registry loading, prompt tracker loading, capability manifest parsing, ToolBroker overhead, audit/redaction overhead, file IO, JSON/YAML loads, regex usage, retries, subprocess calls, tests, provider health checks, model startup paths, memory search, reports, and tracker/doc update workflows.
- Produce redacted reports with severity, evidence, likely cause, recommended fix, effort, risk, tests, docs, rollback, and next action.
- Build from documentation and local mock/fixture tests first.

## Non-Goals

- No package installation.
- No live provider calls by default.
- No paid APIs.
- No model downloads or runtime installation.
- No personal-data access.
- No background services.
- No broad automatic refactors.
- No commits or pushes.
- No optimization patches applied automatically.

## Planned Commands

- `python smart_agent.py perf scan`
- `python smart_agent.py perf scan --static`
- `python smart_agent.py perf scan --startup`
- `python smart_agent.py perf scan --commands`
- `python smart_agent.py perf benchmark --safe`
- `python smart_agent.py perf report --last`
- `python smart_agent.py perf findings`
- `python smart_agent.py perf suggest-fixes`
- `python smart_agent.py perf regressions`
- `python smart_agent.py perf baseline create`
- `python smart_agent.py perf baseline compare`

## Execution Boundary

Scanner commands that inspect the repo or run safe subprocess benchmarks must route through ToolBroker once implemented. PolicyEngine remains final authority. ApprovalManager remains required for any future HIGH/CRITICAL action. AuditLogger records scan, benchmark, report, and recommendation actions with redacted paths/arguments.

## Maturity Plan

PERF-01 specifies policy. PERF-02 through PERF-10 add models, report storage, scanners, benchmark/profiler helpers, recommendations, baselines, patch planning, and dashboard surfaces. PERF-11 runs the release gate.
