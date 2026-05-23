---
prompt_id: SCHEDULER-V1
pack_id: direct-user-task
title: Build Scheduler / Automation v1
category: automation
risk_level: MEDIUM
approval_gate: false
depends_on: ["COMMAND-REGISTRY-QA"]
status: completed
created_at: 2026-05-23
imported_at: 2026-05-23
started_at: 2026-05-23
completed_at: 2026-05-23
branch: main
commit_hash: pending
related_feature_ids: ["SCHEDULER-V1"]
expected_outputs:
  - schedule list/create/run/pause/delete commands
  - local schedule storage
  - audited scheduled runs
  - scheduler docs and tests
tests_expected:
  - tests/test_scheduler.py
tests_run:
  - tests/test_scheduler.py
  - tests/test_command_registry.py
  - tests/test_feature_maturity_docs.py
  - full pytest suite
  - startup policy validation
  - capability manifest validation
  - command registry validation
test_result: "focused tests 25 passed; full suite 528 passed; startup policy ok; capability manifest ok; command registry ok"
docs_updated: true
changelog_updated: true
feature_registry_updated: true
feature_maturity_updated: true
completion_report_updated: true
blockers: []
next_prompt_id: FULL-FEATURE-MATURITY-REVIEW
supersedes: []
superseded_by: []
notes: "Scheduler v1 is manual-run only. It creates no LaunchAgents, cron jobs, daemons, login items, or hidden background persistence."
---

# Prompt

Build Scheduler / Automation v1.

Allow opt-in scheduled workflows without dangerous background autonomy. Support daily briefing, connector doctor, eval run --safe, memory cleanup, and audit summary. Do not create hidden persistence, do not run personal-data workflows without approval, and do not execute CRITICAL actions automatically.
