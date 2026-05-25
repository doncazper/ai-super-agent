# Scheduler Policy

Runtime scheduler policy v1 is manual-run only.

## Allowed Manual Categories

- diagnostics
- evals
- briefing
- maintenance
- backup

## Blocked Categories

- email send
- message send
- calendar write
- contact write
- policy relaxation
- hidden persistence

## Rules

- No hidden background persistence.
- No cron or launch agent without a future decision record and approval.
- No CRITICAL workflow runs automatically.
- Personal-data or HIGH-risk scheduled workflows require explicit approval/config.
- Scheduled workflows may create Action Center items, but cannot execute CRITICAL actions.

