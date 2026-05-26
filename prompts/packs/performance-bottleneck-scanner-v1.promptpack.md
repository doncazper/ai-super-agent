<<<PROMPT_PACK_START>>>
pack_id: performance-bottleneck-scanner-v1
pack_title: Performance Bottleneck Scanner and Optimization Advisor
mode: controlled_batch_until_blocked
requires_sdlc: true
priority: high

pack_summary:
  - Build a safe performance scanner for code bottlenecks, startup overhead, slow commands, slow tests, repeated IO, missing timeouts, inefficient scans, cache gaps, and provider/model overhead risks.
  - Generate reports with severity, evidence, likely cause, recommended fix, effort, risk, tests, and next actions.
  - Do not install packages, call live providers, access personal data, download models, start background services, commit, push, or broadly rewrite code.

global_rules:
  - Follow SPEC.md, docs/SDLC.md, and AGENTS.md.
  - Preserve ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger.
  - Do not enable personal-data tools or paid/live providers by default.
  - Prefer static analysis, safe local benchmarks, mocks, fixtures, dry-runs, and redacted reports.
  - Update CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md, docs/COMMAND_TEST_MATRIX.md if present, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/RELEASE_CHECKLIST.md, and prompt tracking if present.

stop_conditions:
  - package_install_required
  - personal_data_access_required
  - live_provider_required
  - paid_api_required
  - model_download_required
  - background_persistence_required
  - broad_refactor_required
  - security_policy_change_required
  - failing_tests_not_safely_fixable
  - ambiguous_requirements

<<<PROMPT_START id="PERF-01" order="1">>
title: Performance scanner architecture and policy
category: performance
risk_level: LOW
approval_gate: false
depends_on: []
status: queued
PROMPT:
Create docs/performance/PERFORMANCE_SCANNER_TRACK.md, PERFORMANCE_BOTTLENECK_POLICY.md, PERFORMANCE_FINDING_SCHEMA.md, PERFORMANCE_OPTIMIZATION_POLICY.md, PERFORMANCE_BASELINE_STRATEGY.md, and docs/decisions/performance_bottleneck_scanner.md.

Define scan categories: startup/import overhead, CLI dispatch, command registry loading, prompt tracker loading, capability manifest parsing, ToolBroker overhead, audit/redaction overhead, file IO hotspots, full-file scans, JSON/YAML load hotspots, regex in loops, unbounded loops/retries, missing timeouts, network risks, cache gaps, subprocess inefficiencies, slow tests, provider health overhead, model startup overhead, memory search overhead, report generation overhead, and excessive tracker/doc rewrites.

Define severity P0-P4 and planned commands: perf scan, perf scan --static, perf scan --startup, perf scan --commands, perf benchmark --safe, perf report --last, perf findings, perf suggest-fixes, perf regressions, perf baseline create, perf baseline compare. Update tracking docs and run validations.
<<<PROMPT_END id="PERF-01">>

<<<PROMPT_START id="PERF-02" order="2">>
title: Performance finding models and report store
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-01"]
status: queued
PROMPT:
Create agent/performance/{__init__.py,models.py,reports.py,severity.py,errors.py}, tests/performance/test_performance_models_reports.py, reports/performance/.gitkeep, and docs/performance/PERFORMANCE_REPORTS.md.

Implement JSON-serializable PerformanceFinding, PerformanceReport, PerformanceScanConfig, PerformanceScanResult, PerformanceBenchmarkResult, OptimizationRecommendation, PerformanceBaseline, PerformanceMetric, and PerformanceEvidence. Reports must redact secrets, avoid personal data, write JSON/Markdown under reports/performance/, handle no-report states, and create stable finding IDs. Add commands perf report --last and perf findings if practical. Add tests and update command/tracking docs.
<<<PROMPT_END id="PERF-02">>

<<<PROMPT_START id="PERF-03" order="3">>
title: Static bottleneck scanner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-02"]
status: queued
PROMPT:
Create agent/performance/static_scanner.py, patterns.py, tests/performance/test_static_bottleneck_scanner.py, and docs/performance/STATIC_BOTTLENECK_SCANNER.md.

Scanner must not execute scanned code. It should exclude .venv, .git, __pycache__, logs, reports, media_outputs, .qa_workspace by default. Detect heuristic patterns: module-level IO/network calls, optional heavy imports in startup paths, repeated config loads in loops, unbounded file reads, broad os.walk/rglob, subprocess without timeout, requests/httpx without timeout, repeated regex compilation, unbounded retries, large reads in status/dashboard paths, direct live provider calls in doctor/status, and full test suite runs in normal commands. Add perf scan --static and perf scan. Store redacted reports. Add tests.
<<<PROMPT_END id="PERF-03">>

<<<PROMPT_START id="PERF-04" order="4">>
title: Startup and import overhead scanner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-03"]
status: queued
PROMPT:
Create agent/performance/startup_scanner.py, tests/performance/test_startup_scanner.py, and docs/performance/STARTUP_OVERHEAD_SCANNER.md.

Use subprocesses with timeout to measure safe startup/import timings. Do not call LM Studio, live providers, personal-data commands, or load models. Measure safe paths such as ./scripts/agent --help, doctor, status --json, commands list, runtime status, brain providers, and selected module import timings. Missing commands should be skipped, not failed. Add perf scan --startup, perf startup, and perf startup --json. Store report. Add tests.
<<<PROMPT_END id="PERF-04">>

<<<PROMPT_START id="PERF-05" order="5">>
title: Safe command benchmark runner
category: performance
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-04"]
status: queued
PROMPT:
Create agent/performance/benchmark_runner.py, tests/performance/test_benchmark_runner.py, and docs/performance/SAFE_COMMAND_BENCHMARKS.md.

Benchmark only SAFE/LOW read-only commands by default using command registry metadata. Reject HIGH/CRITICAL/personal-data/mutating commands. No live providers by default. Run each command a small N times with timeout, capture median/min/max, redact output, and store report. Add perf benchmark --safe, perf benchmark --group core, and perf benchmark --command "...". Add tests.
<<<PROMPT_END id="PERF-05">>

<<<PROMPT_START id="PERF-06" order="6">>
title: Test suite performance profiler
category: performance
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-05"]
status: queued
PROMPT:
Create agent/performance/test_profiler.py, tests/performance/test_test_profiler.py, and docs/performance/TEST_SUITE_PERFORMANCE.md.

Run pytest with --durations=25 for safe targets, parse durations, identify slow tests/modules, suggest fixture/cache improvements, and store reports. Do not delete/skip tests to make performance look better. Full-suite profiling must be explicit. Add perf tests --durations, perf tests --target <path>, and perf tests report --last. Add tests using fixture output.
<<<PROMPT_END id="PERF-06">>

<<<PROMPT_START id="PERF-07" order="7">>
title: Optimization recommendation engine
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-06"]
status: queued
PROMPT:
Create agent/performance/recommendations.py, tests/performance/test_optimization_recommendations.py, and docs/performance/OPTIMIZATION_RECOMMENDATIONS.md.

Convert findings into prioritized recommendations with expected impact, effort, risk, patch area, required tests, docs, rollback, safe_for_self_heal, human_review_required, and status. Categories include lazy imports, add timeout, bound file scan, cache parsed config, cache command registry, avoid repeated glob, avoid full tracker read in hot path, use streaming/chunking, TTL cache, compile regex once, narrow test target, add fixture, defer live provider check, docs/UX only, and needs architecture review. Add perf suggest-fixes. Do not apply fixes.
<<<PROMPT_END id="PERF-07">>

<<<PROMPT_START id="PERF-08" order="8">>
title: Performance baseline and regression tracking
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-07"]
status: queued
PROMPT:
Create agent/performance/baselines.py, tests/performance/test_performance_baselines.py, and docs/performance/PERFORMANCE_BASELINES.md.

Store baselines under reports/performance/baselines/ containing command timings, startup timings, test durations, finding counts, branch, commit, Python version, platform, and notes. Compare future reports with variance tolerance and rank regressions. No live providers by default. Add perf baseline create, perf baseline compare, and perf regressions. Add tests.
<<<PROMPT_END id="PERF-08">>

<<<PROMPT_START id="PERF-09" order="9">>
title: Safe optimization patch planner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-08"]
status: queued
PROMPT:
Create agent/performance/patch_planner.py, tests/performance/test_performance_patch_planner.py, and docs/performance/PERFORMANCE_PATCH_PLANNER.md.

Given recommendations, create patch plans only. Do not patch by default. Safe-only default. Broad refactors are blocked. Policy/approval/audit/security-control changes require human review. No package installs, commits, or pushes. Patch plan fields: patch_id, recommendation_id, allowed_to_patch, reason, risk_level, expected_files, expected_behavior_change, tests_required, docs_required, rollback_plan, human_review_required, self_heal_compatible. Add perf patch-plan commands. Add tests.
<<<PROMPT_END id="PERF-09">>

<<<PROMPT_START id="PERF-10" order="10">>
title: Performance dashboard and QA integration
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-09"]
status: queued
PROMPT:
Create agent/performance/dashboard.py, tests/performance/test_performance_dashboard.py, and docs/performance/PERFORMANCE_DASHBOARD.md.

Add read-only dashboard/status/next-fix/trends commands that show latest scan summary, top bottlenecks, slowest safe commands, slowest tests, regression warnings, baseline status, recommendations, patch plan candidates, feature maturity impact, and next safe action. Dashboard must not execute scans/benchmarks or auto-fix. Integrate with QA docs/hooks if present. Add tests.
<<<PROMPT_END id="PERF-10">>

<<<PROMPT_START id="PERF-11" order="11">>
title: Performance scanner release gate
category: release_gate
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-10"]
status: queued
PROMPT:
Run release gate. Execute full tests if practical, startup policy validation, capability manifest validation, command registry validation, performance unit tests, static scan, safe startup scan, safe command benchmark, test duration profiler on safe subset, recommendation generation, baseline create/compare with fixture or safe run, and dashboard/status commands.

Verify no scanned code execution, no LM Studio/live provider calls from startup scan, HIGH/CRITICAL/personal commands blocked by benchmark runner, no test deletion/skipping, evidence-based recommendations, no auto-patching, redacted reports, no secrets printed, no package installs, no background jobs, and conservative maturity. Create docs/performance/PERFORMANCE_SCANNER_RELEASE_GATE.md and PERFORMANCE_SCANNER_MATURITY_REVIEW.md. Update all tracking docs. Final report must include top bottlenecks, recommendations, tests, validations, maturity, and next prompt.
<<<PROMPT_END id="PERF-11">>

<<<PROMPT_PACK_END>>>
