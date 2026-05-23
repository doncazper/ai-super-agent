# Scheduler / Automation v1

Scheduler v1 is a local, opt-in, manual-run scheduler. It stores schedule records and lets the user run them explicitly. It does not install a LaunchAgent, cron job, daemon, login item, or other hidden background persistence.

## Commands

```bash
python smart_agent.py schedule list
python smart_agent.py schedule create --workflow connector_doctor --schedule daily@08:00 --name "Connector doctor"
python smart_agent.py schedule create --workflow daily_briefing --arg sections=weather --arg weather_location="Phoenix, AZ"
python smart_agent.py schedule create --workflow backup_create --arg backup_dir=workspace/backups
python smart_agent.py schedule run <schedule_id>
python smart_agent.py schedule pause <schedule_id>
python smart_agent.py schedule delete <schedule_id>
```

Supported workflows:

- `daily_briefing`
- `connector_doctor`
- `eval_safe`
- `memory_cleanup`
- `audit_summary`
- `backup_create`

## Safety Model

- Schedule records are created only by explicit user command.
- V1 has no background runner.
- Schedule storage is local JSON at `data/schedules.json` by default. Tests and advanced use may set `SCHEDULE_PATH`.
- Schedule create, pause, delete, run start, and run finish events are audited.
- Scheduled tool workflows still use `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Personal-data sections, such as calendar, tasks, and email metadata in Daily Briefing, require the same approvals they require outside the scheduler.
- Scheduled workflows may create Action Center items, but they do not execute CRITICAL actions automatically.
- No email sends, text sends, calendar writes, contact writes, task writes, or self-improvement commits run automatically.
- `memory_cleanup` is intentionally conservative in v1 and does not delete memory automatically.
- `backup_create` invokes `backup.create` through `ToolBroker`, forces redacted backups, reads no personal connectors, and writes only local backup archives.

## Background Automation

System-level automation such as LaunchAgents, cron, login items, long-running daemons, or overnight runs is deferred. Adding one requires a decision record, explicit user approval, and a separate release gate.

## Known Limitations

- V1 stores schedule intent and supports manual `schedule run`; it does not wake itself up.
- Schedules are not calendar-aware and do not parse recurrence rules.
- Manual QA results should be logged in `docs/COMMAND_TEST_MATRIX.md`.
