# Scheduler UX

Status: HERMES-06 scaffold.

## Scope

Scheduler UX commands explain and preview scheduled workflow metadata. They help users understand risk, approval requirements, personal-data use, write/send behavior, tests, last run status, and the next safe action before creating or manually running a local schedule.

They do not install cron jobs, LaunchAgents, daemons, login items, polling loops, background workers, or long-running services.

## Commands

```bash
python smart_agent.py schedule explain
python smart_agent.py schedule templates
python smart_agent.py schedule preview connector_doctor
python smart_agent.py schedule dry-run connector_doctor
python smart_agent.py schedule risks daily_briefing
python smart_agent.py schedule review
```

Existing schedule lifecycle commands remain manual:

```bash
python smart_agent.py schedule create --workflow connector_doctor --schedule daily@08:00
python smart_agent.py schedule run <schedule_id>
python smart_agent.py schedule pause <schedule_id>
python smart_agent.py schedule delete <schedule_id>
```

## Safety Model

- Dry-run is the safe default for UX review.
- `schedule dry-run` reports `workflow_executed=false` and `tools_executed=[]`.
- HIGH or personal-data workflows report approval requirements instead of executing.
- CRITICAL send/write workflows are blocked from automatic scheduling.
- Personal-data workflows are disabled by default.
- Background execution is not allowed in v1.
- Action Center items are not created by UX dry-runs.
- The UX layer reads static workflow metadata and optional local schedule records only.

## Template Fields

Each workflow template reports:

- workflow name
- risk level
- required tools
- approval requirements
- personal-data use
- write/send behavior
- whether background execution is allowed
- whether an Action Center item would be needed in a future manual flow
- tests/dogfood status
- last run result when previewing an existing schedule
- next safe action

## Non-Goals

- No OS persistence.
- No automatic schedule execution.
- No unattended HIGH/CRITICAL actions.
- No message/email/calendar/contact sends or writes.
- No personal-data tool enablement.
- No background scheduler service.

