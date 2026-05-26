---
prompt_id: HERMES-06
pack_id: hermes-inspired-safe-autonomy-v1
title: Scheduler UX for safe automations
category: scheduler
risk_level: MEDIUM
approval_gate: false
depends_on: ["HERMES-05"]
status: completed
order: 6
created_at: 2026-05-25T17:28:14+00:00
imported_at: 2026-05-25T17:28:14+00:00
source_pack: prompts/packs/hermes-inspired-safe-autonomy-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T18:05:05+00:00
completed_at: 2026-05-25T18:09:43+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused scheduler UX plus existing scheduler policy tests passed with 21 passed; command registry validation passed with 464 commands; make policy-check passed
docs_updated: README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, RISK_REGISTER, THREAT_MODEL, RELEASE_CHECKLIST, COMPLETION_REPORT
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
notes: Completed HERMES-06 as metadata/dry-run scheduler UX; no background runner, OS persistence, workflow/tool execution from dry-run, unattended HIGH/CRITICAL action, send/write behavior, or personal-data default enablement.
---

# Prompt

You are Codex working in this repo.

Task:
Build Scheduler UX scaffolding for safe automations.

Goal:
Improve the user experience for reviewing, creating, pausing, running, and understanding scheduled workflows without enabling risky automatic actions or background persistence.

Scope:
- Scheduler UX/metadata.
- Dry-run/manual-run commands.
- Docs/tests.
- No OS background persistence.

Non-goals:
- Do not create cron/LaunchAgent/Login Item.
- Do not run schedules automatically.
- Do not run HIGH/CRITICAL actions automatically.
- Do not send messages/emails.
- Do not write calendar/contacts.
- Do not enable personal-data workflows by default.

Create:
- agent/autonomy/scheduler_ux.py
- tests/autonomy/test_scheduler_ux.py
- docs/autonomy/SCHEDULER_UX.md
- docs/autonomy/SCHEDULED_ACTION_GATES.md

Commands:
- python smart_agent.py schedule explain
- python smart_agent.py schedule templates
- python smart_agent.py schedule preview <workflow_id>
- python smart_agent.py schedule dry-run <workflow_id>
- python smart_agent.py schedule risks <workflow_id>
- python smart_agent.py schedule review

Scheduler UX should show:
- workflow name
- risk level
- required tools
- approval requirements
- personal-data use
- write/send behavior
- whether background execution is allowed
- whether Action Center item will be created
- tests/dogfood status
- last run result
- next safe action

Requirements:
1. Dry-run only by default.
2. High/critical workflows create action/approval requirements, not execution.
3. Personal-data workflows disabled by default.
4. Scheduler explains why a workflow is blocked.
5. No OS persistence.
6. No background service.
7. Command registry updated.
8. Feature maturity conservative.

Tests:
- schedule templates list safe templates.
- preview shows risk/approval.
- dry-run executes no tools.
- high-risk workflow blocked/approval-required.
- critical workflow never auto-runs.
- personal workflow disabled.
- command registry updated.

Update docs/tracking.

Final report:
- Scheduler UX added
- tests run/results
- next recommended prompt
