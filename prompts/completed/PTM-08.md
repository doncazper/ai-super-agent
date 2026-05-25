---
prompt_id: PTM-08
pack_id: prompt-tracker-maturity-v1
title: Prompt tracker dogfood and QA suite
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["PTM-07"]
status: completed
order: 8
created_at: 2026-05-23T18:34:04+00:00
imported_at: 2026-05-23T18:34:04+00:00
source_pack: prompts/packs/prompt-tracker-maturity-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T19:28:15+00:00
completed_at: 2026-05-23T19:28:15+00:00
branch:
commit_hash:
related_feature_ids: [PROMPT-LEDGER, PROMPTOPS-WORKBENCH]
expected_outputs:
tests_expected:
tests_run:
test_result: targeted prompt tracker tests passed: 54 passed
docs_updated: yes
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
completion_report_updated:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Completed during controlled PTM batch run; evidence recorded in docs/prompt_tracker and targeted tests.
---

# Prompt

You are Codex working in this repo.

Task:
Build Prompt Tracker Dogfood and QA Suite.

Goal:
Create manual and automated tests that prove the prompt tracker works in real use.

Create:
- dogfood_suites/prompt_tracker_core.yaml
- dogfood_suites/prompt_pack_import.yaml
- dogfood_suites/promptops_workbench.yaml
- eval_cases/prompt_tracker/
- docs/prompt_tracker/PROMPT_TRACKER_DOGFOOD_RUNBOOK.md

Dogfood scenarios:
1. import a valid prompt pack
2. reject invalid prompt pack
3. list prompts
4. show next prompt
5. mark prompt active
6. mark prompt complete with evidence
7. mark prompt failed with reason
8. mark prompt superseded
9. audit missing evidence
10. resume from PROJECT_STATE
11. import from clipboard if available
12. copy next prompt if available
13. autopilot dry-run safe prompts only

Commands:
- python smart_agent.py dogfood run prompt_tracker_core --session
- python smart_agent.py dogfood run prompt_pack_import --session
- python smart_agent.py eval run --prompt-tracker
- python smart_agent.py eval report --prompt-tracker

Requirements:
1. Dogfood uses fixtures.
2. Dogfood does not run high-risk prompts.
3. No personal data.
4. No prompt execution unless mocked/safe.
5. Session logging supported if available.
6. Failures generate clear bug signals.
7. Command registry updated.

Tests:
- suite YAML validates.
- fixtures parse.
- dogfood run works with mocks.
- invalid pack fixture fails as expected.
- eval report produced.
- command registry updated.

Update docs and tracking.

Final report:
- suites created
- evals created
- tests run/results
- next recommended prompt
