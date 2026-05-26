---
prompt_id: PERF-06
pack_id: performance-bottleneck-scanner-v1
title: Test suite performance profiler
category: performance
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-05"]
status: completed
order: 6
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T01:30:54+00:00
completed_at: 2026-05-26T03:53:42+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 29 focused performance tests passed; perf tests profile/report smokes passed; command registry validation passed; make policy-check passed; full suite passed with 1645 tests after tracker table formatting fix
docs_updated: docs/performance/TEST_SUITE_PERFORMANCE.md, CHANGELOG.md, PROJECT_STATE pending, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, TEST_PLAN, RELEASE_CHECKLIST, COMPLETION_REPORT
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Implemented safe pytest duration profiler with explicit full-suite opt-in and redacted reports.
---

# Prompt

Create agent/performance/test_profiler.py, tests/performance/test_test_profiler.py, and docs/performance/TEST_SUITE_PERFORMANCE.md.

Run pytest with --durations=25 for safe targets, parse durations, identify slow tests/modules, suggest fixture/cache improvements, and store reports. Do not delete/skip tests to make performance look better. Full-suite profiling must be explicit. Add perf tests --durations, perf tests --target <path>, and perf tests report --last. Add tests using fixture output.
