# Performance Scanner Release Gate

Last run: 2026-05-25 local release gate with `./.venv/bin/python` 3.12.13.

## Scope

This gate validates the Performance Bottleneck Scanner through PERF-11. It covers local static scanning, startup/import timing, safe command benchmarking, test duration profiling, advisory recommendations, redacted baselines/regression comparisons, metadata-only patch planning, and read-only dashboard/status surfaces.

It does not validate live providers, paid APIs, model downloads, personal-data scans, broad optimization refactors, package installs, automatic patching, commits, pushes, or background services.

## Release Gate Results

| Check | Result | Evidence |
|---|---:|---|
| Full test suite | Pass | `1665 passed in 150.79s` |
| Performance unit tests | Pass | `49 passed in 0.43s` |
| Startup policy validation | Pass | `make policy-check` reported `startup policy ok` |
| Capability manifest validation | Pass | `make policy-check` exited 0 |
| Command registry validation | Pass | `561` commands, no invalid records |
| Static scan | Pass with findings | `static_20260526T042812Z`, 200 files, 49 heuristic findings |
| Startup scan | Pass | `startup_20260526T042821Z`, 3 commands and 3 imports |
| Safe command benchmark | Pass | `benchmark_20260526T042831Z`, `commands validate` median 457.688 ms |
| Test duration profiler | Pass | `test_profile_20260526T042837Z`, `tests/performance`, return code 0 |
| Recommendation generation | Pass | `recommendations_20260526T042843Z`, 1 advisory recommendation |
| Baseline create/compare/regressions | Pass | `baseline_20260526T042849Z`, no regression findings |
| Dashboard/status/next/trends | Pass | Read-only true, `commands_executed=[]` |

## Safety Verification

- Static scanning did not execute scanned code or import scanned modules.
- Startup scanning used bounded subprocesses and did not call LM Studio chat, live providers, model downloads, or background services.
- Safe command benchmarking remained registry-gated and used the existing denial tests for HIGH, CRITICAL, approval-required, personal-data, mutating, live-provider, paid-provider, background, and network/model commands.
- Test profiling did not delete, skip, xfail, edit, or hide tests.
- Recommendations were evidence-based and advisory only.
- Patch planning remained metadata-only with `applied_patches=0`.
- Reports, baselines, recommendation summaries, dashboard output, and trend summaries are redacted local artifacts.
- No package installs, model downloads, background jobs, commits, pushes, live provider calls, or personal-data access were performed.

## Top Bottlenecks Found

The release static scan found 49 heuristic findings in 200 Python files:

| Category | Count |
|---|---:|
| Subprocess timeout | 22 |
| Broad traversal | 8 |
| Unbounded IO | 7 |
| Repeated config loads in loops | 6 |
| Slow commands | 3 |
| Missing timeouts | 1 |
| Unbounded retries | 1 |
| Repeated regex compilation | 1 |

Representative findings:

- `tests/test_command_registry.py:76`: subprocess call without timeout.
- `tests/test_secret_config_doctor.py:50`: subprocess call without timeout.
- `tests/test_news_capability_provider_policy.py:62`: repeated config load candidate.
- `tests/test_backup_restore.py:71`: broad recursive traversal candidate.
- `agent/connectors/secret_doctor.py:744`: broad recursive traversal candidate.

These are heuristic candidates. They are not release blockers by themselves and require scoped human review before any optimization patch.

## Recommendation Summary

The latest recommendation report produced one safe advisory recommendation from the performance test profile:

| Recommendation | Risk | Self-heal safe | Human review |
|---|---:|---:|---:|
| Narrow the profiled test target | LOW | true | false |

This recommendation is about iteration speed only. It does not change full-suite release-gate expectations.

## Baseline And Regression Status

`baseline_20260526T042849Z` was created from the latest safe local report and compared with tolerance `0.2`. Regression status was `ok` with no regression findings.

## Dashboard Status

`perf dashboard`, `perf status`, `perf next-fix`, and `perf trends` returned `status=ok`, `read_only=true`, and `commands_executed=[]`. The dashboard summarizes existing reports only and does not run scans, tests, benchmarks, patch plans, or fixes.

## Release Decision

Performance Bottleneck Scanner is locally release-gated and may be treated as `5 Hardened` for local performance evidence and advisory optimization planning. It is not `Live-Validated`, `User-Ready`, or a `Mature Pattern` yet because it lacks long-running manual QA, clean release-candidate review, and real-world optimization follow-through. The final PERF-11 full-suite rerun passed with `1665` tests.
