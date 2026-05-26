---
prompt_id: PERF-09
pack_id: performance-bottleneck-scanner-v1
title: Safe optimization patch planner
category: performance
risk_level: LOW
approval_gate: false
depends_on: ["PERF-08"]
status: completed
order: 9
created_at: 2026-05-26T00:56:39+00:00
imported_at: 2026-05-26T00:56:39+00:00
source_pack: prompts/packs/performance-bottleneck-scanner-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T04:14:49+00:00
completed_at: 2026-05-26T04:19:40+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: 46 focused performance tests passed; feature maturity docs tests passed; perf patch-plan smoke passed with applied_patches=0; command registry validation passed; make policy-check passed
docs_updated: docs/performance/PERFORMANCE_PATCH_PLANNER.md, CHANGELOG.md, PROJECT_STATE pending, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, TEST_PLAN, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Implemented metadata-only patch planning with applied_patches=0.
---

# Prompt

Create agent/performance/patch_planner.py, tests/performance/test_performance_patch_planner.py, and docs/performance/PERFORMANCE_PATCH_PLANNER.md.

Given recommendations, create patch plans only. Do not patch by default. Safe-only default. Broad refactors are blocked. Policy/approval/audit/security-control changes require human review. No package installs, commits, or pushes. Patch plan fields: patch_id, recommendation_id, allowed_to_patch, reason, risk_level, expected_files, expected_behavior_change, tests_required, docs_required, rollback_plan, human_review_required, self_heal_compatible. Add perf patch-plan commands. Add tests.
