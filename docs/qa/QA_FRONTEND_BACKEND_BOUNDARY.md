# QA Frontend / Backend Boundary

The Command QA Sandbox now exposes a backend service boundary for future CLI, local dashboard, Mac app, Windows app, iOS companion, or web frontend views.

## Backend Ownership

`agent/qa/service.py` owns the reusable backend boundary:

- command inventory and coverage summaries
- QA plan generation
- safe-tier batch execution through the existing runner
- disposable workspace action constraints
- local QA report and run-summary reads
- failure ranking by severity and feature
- bug and regression generation wrappers
- self-heal plan creation
- conservative maturity impact calculation

The service returns JSON-serializable envelopes from `agent/qa/api_models.py`. Read-only methods set `read_only=true` and do not execute commands. Action methods return action envelopes and still enforce QA tier safety.

## Frontend Ownership

`agent/qa/dashboard.py` is a presentation adapter. It formats service outputs for the current CLI dashboard and is the intended model for future frontends.

Frontends may:

- display QA status
- display run progress and latest summaries
- display pass/fail counts
- display bug and failure rankings
- display next recommended safe batches
- display maturity impact
- request backend actions through service methods

Frontends must not:

- execute shell commands directly
- bypass the QA service
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger
- access raw secrets or raw personal data
- run HIGH, CRITICAL, personal-data, send, write, or destructive commands
- create background persistence

## Safety Boundary

Read-only methods:

- `get_qa_status()`
- `get_latest_run_summary()`
- `get_command_coverage()`
- `get_failures_by_severity()`
- `get_failures_by_feature()`
- `get_open_bugs()`
- `get_regression_coverage()`
- `get_next_safe_batch()`
- `get_next_safe_fix()`
- `get_maturity_impact()`

Action methods:

- `create_plan()`
- `run_safe_batch()`
- `create_bug_from_run()`
- `create_regression_from_bug()`
- `create_regression_from_run()`
- `create_self_heal_plan()`

`run_safe_batch()` supports only Tier 0, Tier 1, and sandboxed Tier 3. It blocks HIGH, CRITICAL, FORBIDDEN, and personal-data command candidates before delegating to the existing safe runner.

## Current CLI Behavior

`python smart_agent.py qa dashboard` and `python smart_agent.py qa status` consume the service boundary. They remain read-only and do not execute commands.

Existing QA action commands continue to use safe backend methods or the existing safe runner paths; they do not allow a frontend to execute arbitrary commands.

