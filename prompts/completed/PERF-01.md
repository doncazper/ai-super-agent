---
prompt_id: PERF-01
pack_id: performance-bottleneck-scanner-v1
title: Performance scanner architecture and policy
category: performance
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T00:56:45+00:00
completed_at: 2026-05-26T01:04:48+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/performance/test_performance_docs.py: 3 passed; commands validate: ok with 552 commands; make policy-check: startup policy and capability manifest ok
docs_updated: docs/performance/*, docs/decisions/performance_bottleneck_scanner.md, CHANGELOG.md, project trackers, command registry/test matrix, completion report
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
notes: PERF-01 docs/metadata only; no runtime scanner, benchmark, live provider, paid API, personal-data access, background service, broad refactor, commit, or push.
---

# Prompt

Create docs/performance/PERFORMANCE_SCANNER_TRACK.md, PERFORMANCE_BOTTLENECK_POLICY.md, PERFORMANCE_FINDING_SCHEMA.md, PERFORMANCE_OPTIMIZATION_POLICY.md, PERFORMANCE_BASELINE_STRATEGY.md, and docs/decisions/performance_bottleneck_scanner.md.

Define scan categories: startup/import overhead, CLI dispatch, command registry loading, prompt tracker loading, capability manifest parsing, ToolBroker overhead, audit/redaction overhead, file IO hotspots, full-file scans, JSON/YAML load hotspots, regex in loops, unbounded loops/retries, missing timeouts, network risks, cache gaps, subprocess inefficiencies, slow tests, provider health overhead, model startup overhead, memory search overhead, report generation overhead, and excessive tracker/doc rewrites.

Define severity P0-P4 and planned commands: perf scan, perf scan --static, perf scan --startup, perf scan --commands, perf benchmark --safe, perf report --last, perf findings, perf suggest-fixes, perf regressions, perf baseline create, perf baseline compare. Update tracking docs and run validations.
