---
prompt_id: PERF-10
pack_id: performance-bottleneck-scanner-v1
title: Performance dashboard and QA integration
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-09"]
status: completed
order: 10
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:19:41+00:00
completed_at: 2026-05-26T04:27:47+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 49 focused performance tests passed; dashboard/status/next-fix/trends smokes returned read_only=true and commands_executed=[]; command registry validation passed; make policy-check passed; feature maturity docs tests passed
docs_updated: docs/performance/PERFORMANCE_DASHBOARD.md, CHANGELOG.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/COMMAND_REGISTRY.md, docs/COMMAND_TEST_MATRIX.md, docs/TEST_PLAN.md, docs/RELEASE_CHECKLIST.md, docs/COMPLETION_REPORT.md
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
notes: Implemented read-only performance dashboard/status/next-fix/trends summaries.
---

# Prompt

Create agent/performance/dashboard.py, tests/performance/test_performance_dashboard.py, and docs/performance/PERFORMANCE_DASHBOARD.md.

Add read-only dashboard/status/next-fix/trends commands that show latest scan summary, top bottlenecks, slowest safe commands, slowest tests, regression warnings, baseline status, recommendations, patch plan candidates, feature maturity impact, and next safe action. Dashboard must not execute scans/benchmarks or auto-fix. Integrate with QA docs/hooks if present. Add tests.
