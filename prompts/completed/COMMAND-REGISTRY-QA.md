---
prompt_id: COMMAND-REGISTRY-QA
pack_id: direct-user-task
title: Build Command Registry + Manual QA System
category: command_tracking
risk_level: SAFE
approval_gate: false
depends_on: ["PROMPTOPS-WORKBENCH"]
status: completed
created_at: 2026-05-23
imported_at: 2026-05-23
started_at: 2026-05-23
completed_at: 2026-05-23
branch: main
commit_hash: pending
related_feature_ids: ["COMMAND-REGISTRY"]
expected_outputs:
  - docs/COMMAND_REGISTRY.md
  - docs/COMMAND_TEST_MATRIX.md
  - docs/COMMAND_LEGACY.md
  - docs/COMMAND_QA_RUNBOOK.md
  - commands CLI inspection commands
tests_expected:
  - tests/test_command_registry.py
tests_run:
  - tests/test_command_registry.py
  - tests/test_feature_maturity_docs.py
  - full pytest suite
  - startup policy validation
  - capability manifest validation
  - command registry validation
test_result: "focused tests 13 passed; full suite 521 passed; startup policy ok; capability manifest ok; registry validation ok"
docs_updated: true
changelog_updated: true
feature_registry_updated: true
feature_maturity_updated: true
completion_report_updated: true
blockers: []
next_prompt_id: NATIVE-SKILLS-FOUNDATION
supersedes: []
superseded_by: []
notes: "Metadata-only command catalog and manual QA workflow. The qa-run command prints safe command examples and does not execute them in v1."
---

# Prompt

Build Command Registry + Manual QA System.

Create a durable command catalog, manual QA/test matrix, legacy command tracker, QA runbook, validation, and optional CLI commands for inspecting the command registry. Do not add risky runtime capabilities, enable personal-data tools, send email/messages, weaken policy, bypass ToolBroker, or mark commands user-ready without evidence.
