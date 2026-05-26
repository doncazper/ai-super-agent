# Test Suite Performance Profiling

`PERF-06` adds a local pytest duration profiler for safe test targets.

## Commands

- `python smart_agent.py perf tests --durations 25`
- `python smart_agent.py perf tests --target tests/performance --durations 25`
- `python smart_agent.py perf tests report --last`

Broad targets such as `tests` or `.` require explicit opt-in:

```bash
python smart_agent.py perf tests --target tests --full-suite --durations 25
```

## Safety Rules

The profiler runs `pytest` with `--durations=N` in a bounded subprocess. It does not delete, skip, xfail, or edit tests to make performance look better. It does not install packages, call live providers, use paid APIs, download models, access personal data, start background services, apply patches, commit, or push.

Raw pytest stdout and stderr are not stored. Reports retain parsed duration rows, module summaries, return code, elapsed time, byte counts, and conservative optimization suggestions only.

## Reports

Reports are written under `reports/performance/` as redacted local artifacts. The `.profile.json` companion report contains parsed duration rows and module summaries for dashboard/recommendation use.
