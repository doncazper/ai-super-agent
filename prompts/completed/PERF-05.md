---
prompt_id: PERF-05
pack_id: performance-bottleneck-scanner-v1
title: Safe command benchmark runner
category: performance
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-04"]
status: completed
order: 5
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T01:22:12+00:00
completed_at: 2026-05-26T01:30:49+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 23 focused performance tests passed; benchmark smoke passed; command registry validation passed; make policy-check passed
docs_updated: docs/performance/SAFE_COMMAND_BENCHMARKS.md, CHANGELOG.md, PROJECT_STATE pending, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, TEST_PLAN, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Implemented safe command benchmark runner with registry gating and redacted reports.
---

# Prompt

Create agent/performance/benchmark_runner.py, tests/performance/test_benchmark_runner.py, and docs/performance/SAFE_COMMAND_BENCHMARKS.md.

Benchmark only SAFE/LOW read-only commands by default using command registry metadata. Reject HIGH/CRITICAL/personal-data/mutating commands. No live providers by default. Run each command a small N times with timeout, capture median/min/max, redact output, and store report. Add perf benchmark --safe, perf benchmark --group core, and perf benchmark --command "...". Add tests.
