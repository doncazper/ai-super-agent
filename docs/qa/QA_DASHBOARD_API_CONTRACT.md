# QA Dashboard API Contract

This contract describes the JSON payloads future frontends should consume from the Command QA backend service. It is an in-process Python service contract, not a web server.

## Envelope

Read-only methods return:

```json
{
  "status": "ok",
  "generated_at": "2026-05-25T00:00:00+00:00",
  "read_only": true,
  "data": {},
  "warnings": []
}
```

Action methods return:

```json
{
  "status": "ok",
  "generated_at": "2026-05-25T00:00:00+00:00",
  "action": "run_safe_batch",
  "safe_only": true,
  "data": {},
  "warnings": []
}
```

All payloads must remain JSON-serializable and secret-redacted.

## Read-Only Methods

| Method | Purpose | Side effects |
|---|---|---|
| `get_qa_status()` | Overall QA report, bug, and command counts | none |
| `get_latest_run_summary()` | Latest redacted run-report pointer | none |
| `get_command_coverage()` | Command registry coverage and metadata gaps | none |
| `get_failures_by_severity()` | Ranked redacted failures grouped by severity | none |
| `get_failures_by_feature()` | Ranked redacted failures grouped by feature or area | none |
| `get_open_bugs()` | Open local bug summaries | none |
| `get_regression_coverage()` | Open bug regression coverage counts | none |
| `get_next_safe_batch()` | Dry-run next safe Tier 1 batch selection | none |
| `get_next_safe_fix()` | Next safe self-heal candidate summary | none |
| `get_maturity_impact()` | Conservative maturity-impact summary | none |

## Action Methods

| Method | Purpose | Safety behavior |
|---|---|---|
| `create_plan()` | Generate QA plan metadata | no command execution |
| `run_safe_batch()` | Run bounded safe Tier 0/Tier 1 or sandboxed Tier 3 command QA | blocks HIGH/CRITICAL/FORBIDDEN/personal-data candidates |
| `create_bug_from_run()` | Generate redacted local bugs from a QA run | writes bug records only |
| `create_regression_from_bug()` | Generate a skipped regression scaffold from a bug | writes test scaffold only |
| `create_regression_from_run()` | Generate bugs and skipped regression scaffolds from a run | writes local bug/test scaffolds only |
| `create_self_heal_plan()` | Create a conservative self-heal patch plan | plan/report only; no patch application |

## Frontend Rules

- Frontends call service methods, not shell commands.
- Dashboard/status views call only read-only methods.
- Action buttons must clearly show the backend action name and safety tier before calling an action method.
- Frontends must display service warnings and blocked results without retrying through alternate execution paths.
- Frontends must not receive raw command output beyond redacted excerpts already stored in QA reports.
- Future remote or GUI frontends must add their own pairing/authentication contract before use.

