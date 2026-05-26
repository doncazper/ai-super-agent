---
prompt_id: PERF-11
pack_id: performance-bottleneck-scanner-v1
title: Performance scanner release gate
category: release_gate
risk_level: MEDIUM
approval_gate: false
depends_on: ["PERF-10"]
status: completed
order: 11
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:27:50+00:00
completed_at: 2026-05-26T04:39:40+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Full suite 1665 passed; tests/performance 49 passed; feature maturity docs 13 passed; commands validate ok with 561 commands; make policy-check passed; safe static/startup/benchmark/test-profile/recommendation/baseline/dashboard smokes passed
docs_updated: docs/performance/PERFORMANCE_SCANNER_RELEASE_GATE.md, docs/performance/PERFORMANCE_SCANNER_MATURITY_REVIEW.md, CHANGELOG.md, docs/PROJECT_STATE.md, docs/FEATURE_REGISTRY.md, docs/FEATURE_MATURITY.md, docs/FEATURE_ROADMAP.md, docs/PROMPT_QUEUE.md, docs/PROMPT_LEDGER.md, docs/PROMPT_AUDIT.md, docs/COMPLETION_REPORT.md, docs/RISK_REGISTER.md, docs/THREAT_MODEL.md, docs/TEST_PLAN.md, docs/RELEASE_CHECKLIST.md
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
notes: Completed local Performance Bottleneck Scanner release gate; no live providers, personal data, package installs, automatic patches, commits, or pushes.
---

# Prompt

Run release gate. Execute full tests if practical, startup policy validation, capability manifest validation, command registry validation, performance unit tests, static scan, safe startup scan, safe command benchmark, test duration profiler on safe subset, recommendation generation, baseline create/compare with fixture or safe run, and dashboard/status commands.

Verify no scanned code execution, no LM Studio/live provider calls from startup scan, HIGH/CRITICAL/personal commands blocked by benchmark runner, no test deletion/skipping, evidence-based recommendations, no auto-patching, redacted reports, no secrets printed, no package installs, no background jobs, and conservative maturity. Create docs/performance/PERFORMANCE_SCANNER_RELEASE_GATE.md and PERFORMANCE_SCANNER_MATURITY_REVIEW.md. Update all tracking docs. Final report must include top bottlenecks, recommendations, tests, validations, maturity, and next prompt.
