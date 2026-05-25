---
prompt_id: ORCH-06
pack_id: agent-runtime-orchestration-v1
title: Workflow runner and job queue
category: feature
risk_level: MEDIUM
approval_gate: false
depends_on: ["ORCH-05"]
status: completed
order: 6
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
test_result: ./.venv/bin/python -m pytest tests/runtime -q: 31 passed; workflows run connector_doctor smoke passed
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
notes: Added workflow metadata runner and in-process job queue; HIGH approval-required and CRITICAL blocked.
---

# Prompt

You are Codex working in this repo.

Task:
Build safe WorkflowRunner and JobQueue scaffolding.

Goal:
Create a controlled way to represent and coordinate workflows/jobs without letting them bypass ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger.

Scope:
- Workflow runner scaffolding.
- Job queue scaffolding.
- Safe metadata/state only.
- Tests.
- No risky workflow implementation.

Non-goals:
- Do not execute existing high-risk workflows automatically.
- Do not run tools directly.
- Do not start background workers.
- Do not run CRITICAL actions.
- Do not enable personal-data workflows by default.
- Do not schedule jobs persistently.
- Do not send messages/emails.
- Do not write calendar/contacts.

Create:
- agent/runtime/workflow_runner.py
- agent/runtime/job_queue.py
- tests/runtime/test_workflow_runner.py
- tests/runtime/test_job_queue.py

WorkflowRunner responsibilities:
- register workflow metadata
- list workflows
- validate workflow request
- create workflow run record
- update run status
- enforce that workflow steps request tools through ToolBroker
- refuse unknown workflow
- refuse disabled workflow
- stop at approval gates
- produce action items instead of executing high/critical actions

JobQueue responsibilities:
- create job metadata
- list jobs
- show job
- update job status
- retry safe jobs only
- mark blocked/failed/completed
- store error summary
- no background execution by default
- no CRITICAL job execution
- optional persistence only if safe and existing local state supports it

Workflow statuses:
- registered
- disabled
- planned
- running
- completed
- failed
- blocked
- approval_required

Job statuses:
- queued
- running
- completed
- failed
- blocked
- cancelled
- approval_required

Requirements:
1. WorkflowRunner does not call tools directly.
2. WorkflowRunner must be able to reference ToolBroker without bypassing it.
3. JobQueue must not run jobs automatically by default.
4. HIGH/CRITICAL workflows return approval_required/action_center style status.
5. Unknown workflows refused.
6. Disabled workflows refused.
7. Personal workflows disabled by default.
8. Workflow/job state contains no raw secrets.
9. Workflow/job state contains no raw personal data by default.
10. Audit correlation fields included.

Commands can remain planned/stubbed in COMMAND_REGISTRY for now:
- python smart_agent.py workflows list
- python smart_agent.py workflows run <workflow_id>
- python smart_agent.py jobs list
- python smart_agent.py jobs show <job_id>

Tests:
- workflow registry/list works
- unknown workflow refused
- disabled workflow refused
- high-risk workflow returns approval_required
- workflow step cannot bypass ToolBroker, or this is enforced by architecture/documented test
- job create/list/show works
- safe retry metadata works
- job queue does not auto-run by default
- CRITICAL job blocked
- personal workflow disabled by default
- secrets redacted

Update:
- docs/runtime/WORKFLOW_RUNNER.md
- docs/runtime/JOB_QUEUE.md
- docs/COMMAND_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md

Run targeted tests and validations.

Final report:
- workflow runner added
- job queue added
- tests run/results
- command registry updates
- next recommended prompt
