---
prompt_id: FULL-FEATURE-MATURITY-REVIEW
pack_id: controlled-actions-workflow-batch
title: Full feature maturity review
category: release-gate
risk_level: LOW
approval_gate: false
depends_on: ["SCHEDULER-V1"]
status: completed
created_at: 2026-05-23T00:55:00-07:00
imported_at: 2026-05-23T00:55:00-07:00
started_at: 2026-05-23T00:12:00-07:00
completed_at: 2026-05-23T00:20:00-07:00
branch: main
commit_hash: pending
related_feature_ids: ["FEATURE-MATURITY", "SCHEDULER-V1", "ACTION-CENTER"]
tests_expected: ["full pytest", "startup policy", "capability manifest", "safe eval", "command registry validation"]
tests_run: ["529 passed", "startup policy ok", "capability manifest ok", "safe eval ok", "command registry ok"]
test_result: pass
docs_updated: true
changelog_updated: true
feature_registry_updated: true
feature_maturity_updated: true
completion_report_updated: true
next_prompt_id: NATIVE-SKILLS-FOUNDATION
---

# Prompt

Run full feature maturity review and release gate for this feature batch.

Update the project source of truth after the controlled actions and workflow batch, identify maturity levels conservatively, run the safety/release checks, update tracking docs, and commit if tests pass.
