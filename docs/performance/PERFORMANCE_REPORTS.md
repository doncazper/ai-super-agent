# Performance Reports

Status: implemented for PERF-02 report models and read-only report inspection.

Performance reports are local, redacted JSON/Markdown artifacts under `reports/performance/`. They are evidence records for scans, safe benchmarks, findings, recommendations, and future baselines. PERF-02 adds the report schema and store only; it does not add scanners, benchmarks, profiling, live providers, model calls, package installation, personal-data access, background services, or optimization patch application.

## Report Rules

- Reports must be JSON-serializable.
- Reports must redact secret-looking keys and token patterns before writing or displaying.
- Reports must avoid raw personal data and raw provider content.
- Reports must stay under `reports/performance/`.
- Findings must have stable IDs derived from finding content.
- No-report states must be structured and non-fatal.
- Read-only report commands must not run scans or benchmarks.

## Commands

- `python smart_agent.py perf report --last`
- `python smart_agent.py perf findings`

Both commands route through ToolBroker and read local redacted report metadata only. They do not execute shell commands, run pytest, scan files, benchmark commands, call providers, access personal data, write memory, or apply fixes.

## Future Work

PERF-03 through PERF-11 add static scanning, startup scanning, safe command benchmarks, test profiling, recommendations, baselines, patch planning, dashboard integration, and release-gate validation.
