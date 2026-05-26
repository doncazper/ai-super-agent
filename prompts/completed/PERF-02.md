---
prompt_id: PERF-02
pack_id: performance-bottleneck-scanner-v1
title: Performance finding models and report store
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-01"]
status: completed
order: 2
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T01:04:56+00:00
completed_at: 2026-05-26T01:10:28+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/performance/test_performance_models_reports.py + test_performance_docs.py: 8 passed; perf report --last and perf findings CLI smokes returned structured no-report states; commands validate: ok with 552 commands; make policy-check: startup policy and capability manifest ok
docs_updated: docs/performance/PERFORMANCE_REPORTS.md, CHANGELOG.md, feature registry/maturity/roadmap, command registry/test matrix, project state, completion report
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
notes: PERF-02 adds report models/store and read-only brokered report commands only; no scanner, benchmark, live provider, paid API, personal-data access, background service, patching, commit, or push.
---

# Prompt

Create agent/performance/{__init__.py,models.py,reports.py,severity.py,errors.py}, tests/performance/test_performance_models_reports.py, reports/performance/.gitkeep, and docs/performance/PERFORMANCE_REPORTS.md.

Implement JSON-serializable PerformanceFinding, PerformanceReport, PerformanceScanConfig, PerformanceScanResult, PerformanceBenchmarkResult, OptimizationRecommendation, PerformanceBaseline, PerformanceMetric, and PerformanceEvidence. Reports must redact secrets, avoid personal data, write JSON/Markdown under reports/performance/, handle no-report states, and create stable finding IDs. Add commands perf report --last and perf findings if practical. Add tests and update command/tracking docs.
