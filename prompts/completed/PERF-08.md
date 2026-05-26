---
prompt_id: PERF-08
pack_id: performance-bottleneck-scanner-v1
title: Performance baseline and regression tracking
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-07"]
status: completed
order: 8
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:10:00+00:00
completed_at: 2026-05-26T04:14:48+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 40 focused performance tests passed; feature maturity docs tests passed; baseline create/compare/regressions smokes passed; command registry validation passed; make policy-check passed
docs_updated: docs/performance/PERFORMANCE_BASELINES.md, CHANGELOG.md, PROJECT_STATE pending, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, TEST_PLAN, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Implemented redacted local baselines and tolerance-based regression tracking.
---

# Prompt

Create agent/performance/baselines.py, tests/performance/test_performance_baselines.py, and docs/performance/PERFORMANCE_BASELINES.md.

Store baselines under reports/performance/baselines/ containing command timings, startup timings, test durations, finding counts, branch, commit, Python version, platform, and notes. Compare future reports with variance tolerance and rank regressions. No live providers by default. Add perf baseline create, perf baseline compare, and perf regressions. Add tests.
