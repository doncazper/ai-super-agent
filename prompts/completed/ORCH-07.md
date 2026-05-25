---
prompt_id: ORCH-07
pack_id: agent-runtime-orchestration-v1
title: Scheduler policy and safe automation hooks
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-06"]
status: completed
order: 7
created_at: 2026-05-23T21:24:19+00:00
imported_at: 2026-05-23T21:24:19+00:00
source_pack: prompts/packs/agent-runtime-orchestration-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-23T21:31:13+00:00
completed_at: 2026-05-23T21:31:13+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed
docs_updated: yes
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
notes: Added manual-run scheduler policy that blocks CRITICAL and hidden background persistence.
---

# Prompt

You are Codex working in this repo.

Task:
Build SchedulerPolicy and safe automation hooks.

Goal:
Prepare for future scheduled workflows without adding hidden background persistence or allowing risky unattended actions.

Scope:
- Scheduler policy.
- Scheduled job metadata.
- Safe/manual-run scaffolding.
- Tests.
- No actual OS-level background service.

Non-goals:
- Do not create cron jobs.
- Do not create LaunchAgents.
- Do not create login items.
- Do not start background daemon.
- Do not auto-run personal workflows.
- Do not execute CRITICAL actions.
- Do not send messages/emails.
- Do not write calendar/contacts.
- Do not install persistence.

Create:
- agent/runtime/scheduler.py
- tests/runtime/test_scheduler_policy.py
- docs/runtime/SCHEDULER_POLICY.md

SchedulerPolicy must define:
- allowed scheduled workflow categories
- forbidden scheduled workflow categories
- approval behavior
- personal-data behavior
- CRITICAL action behavior
- manual-run-only mode
- future background-run requirements
- audit requirements
- user-visible setup requirements

Allowed v1 scheduled workflows:
- connector doctor
- safe eval suite
- command registry validation
- docs weekly review dry-run
- memory cleanup if no personal data is exposed
- audit summary metadata
- backup metadata/dry-run
- dogfood dry-run/mock suites

Forbidden v1 scheduled workflows:
- email send
- message send
- calendar write
- contact write
- personal-data full scans
- browser automation
- package install
- code execution with network
- policy changes
- audit deletion
- persistence creation

Requirements:
1. Scheduler is disabled by default.
2. Scheduler has no OS-level persistence.
3. Scheduler cannot execute CRITICAL actions.
4. Scheduler cannot execute HIGH actions without approval.
5. Scheduler can create Action Center items but not execute them.
6. Scheduler commands are stubbed/planned unless safe.
7. Scheduled job metadata does not contain secrets/raw personal data.
8. Scheduled run events are auditable.
9. Manual-run mode can be modeled without actual background execution.

Commands can be planned/stubbed in COMMAND_REGISTRY:
- python smart_agent.py schedule list
- python smart_agent.py schedule create
- python smart_agent.py schedule run <schedule_id>
- python smart_agent.py schedule pause <schedule_id>
- python smart_agent.py schedule delete <schedule_id>

Tests:
- scheduler disabled by default
- safe workflow category allowed
- CRITICAL workflow blocked
- HIGH workflow requires approval
- personal-data workflow blocked/approval-required
- no OS persistence created
- no background worker started
- scheduled job metadata redacts secrets
- command registry updated

Update:
- docs/runtime/SCHEDULER_POLICY.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/COMMAND_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run targeted tests and validations.

Final report:
- scheduler policy added
- tests run/results
- forbidden/allowed categories
- next recommended prompt
