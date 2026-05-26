---
prompt_id: PERF-03
pack_id: performance-bottleneck-scanner-v1
title: Static bottleneck scanner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-02"]
status: completed
order: 3
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T01:10:33+00:00
completed_at: 2026-05-26T01:17:44+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/performance/test_static_bottleneck_scanner.py + models/docs tests: 13 passed; perf scan --static --max-files 5 wrote redacted report with 0 findings after false-positive tuning; commands validate: ok with 552 commands; make policy-check: startup policy and capability manifest ok
docs_updated: docs/performance/STATIC_BOTTLENECK_SCANNER.md, CHANGELOG.md, feature registry/maturity/roadmap, release checklist, command registry/test matrix, project state, completion report
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
notes: PERF-03 adds static scanner only; no scanned-code execution, imports of scanned modules, benchmarks, live providers, paid APIs, personal-data access, background services, patches, commit, or push.
---

# Prompt

Create agent/performance/static_scanner.py, patterns.py, tests/performance/test_static_bottleneck_scanner.py, and docs/performance/STATIC_BOTTLENECK_SCANNER.md.

Scanner must not execute scanned code. It should exclude .venv, .git, __pycache__, logs, reports, media_outputs, .qa_workspace by default. Detect heuristic patterns: module-level IO/network calls, optional heavy imports in startup paths, repeated config loads in loops, unbounded file reads, broad os.walk/rglob, subprocess without timeout, requests/httpx without timeout, repeated regex compilation, unbounded retries, large reads in status/dashboard paths, direct live provider calls in doctor/status, and full test suite runs in normal commands. Add perf scan --static and perf scan. Store redacted reports. Add tests.
