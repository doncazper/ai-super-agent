---
prompt_id: PERF-04
pack_id: performance-bottleneck-scanner-v1
title: Startup and import overhead scanner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-03"]
status: completed
order: 4
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T01:17:51+00:00
completed_at: 2026-05-26T01:22:01+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/performance startup/static/models/docs: 17 passed; perf startup --json --timeout 5 --max-commands 1 --max-imports 1 wrote redacted startup report; commands validate: ok with 553 commands; make policy-check: startup policy and capability manifest ok
docs_updated: docs/performance/STARTUP_OVERHEAD_SCANNER.md, CHANGELOG.md, feature registry/maturity/roadmap, release checklist, command registry/test matrix, project state, completion report
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
notes: PERF-04 adds bounded startup/import timing only; no LM Studio chat, live providers, personal-data commands, model loads/downloads, background services, full-suite runs, patches, commit, or push.
---

# Prompt

Create agent/performance/startup_scanner.py, tests/performance/test_startup_scanner.py, and docs/performance/STARTUP_OVERHEAD_SCANNER.md.

Use subprocesses with timeout to measure safe startup/import timings. Do not call LM Studio, live providers, personal-data commands, or load models. Measure safe paths such as ./scripts/agent --help, doctor, status --json, commands list, runtime status, brain providers, and selected module import timings. Missing commands should be skipped, not failed. Add perf scan --startup, perf startup, and perf startup --json. Store report. Add tests.
