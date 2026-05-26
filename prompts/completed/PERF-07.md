---
prompt_id: PERF-07
pack_id: performance-bottleneck-scanner-v1
title: Optimization recommendation engine
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-06"]
status: completed
order: 7
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T03:53:48+00:00
completed_at: 2026-05-26T04:10:00+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 35 focused performance tests passed; feature maturity docs tests passed; perf suggest-fixes smoke passed with applied_patches=0; command registry validation passed; make policy-check passed
docs_updated: docs/performance/OPTIMIZATION_RECOMMENDATIONS.md, CHANGELOG.md, PROJECT_STATE pending, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, TEST_PLAN, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Implemented advisory optimization recommendations with no patch application.
---

# Prompt

Create agent/performance/recommendations.py, tests/performance/test_optimization_recommendations.py, and docs/performance/OPTIMIZATION_RECOMMENDATIONS.md.

Convert findings into prioritized recommendations with expected impact, effort, risk, patch area, required tests, docs, rollback, safe_for_self_heal, human_review_required, and status. Categories include lazy imports, add timeout, bound file scan, cache parsed config, cache command registry, avoid repeated glob, avoid full tracker read in hot path, use streaming/chunking, TTL cache, compile regex once, narrow test target, add fixture, defer live provider check, docs/UX only, and needs architecture review. Add perf suggest-fixes. Do not apply fixes.
