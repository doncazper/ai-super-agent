# Command QA Dashboard

The command QA dashboard reads local command registry metadata, QA reports, bug reports, and feature maturity docs through the reusable `agent.qa.service.QAService` backend boundary.

Commands:

```bash
python smart_agent.py qa dashboard
python smart_agent.py qa status
python smart_agent.py qa feature-maturity-impact
python smart_agent.py qa next-fix
```

Properties:

- Read-only.
- Does not run commands.
- Does not access personal data.
- Does not update maturity automatically.
- Reports conservative maturity impact only from available local evidence.
- Uses the same JSON-serializable service/API models intended for future CLI, local dashboard, Mac app, Windows app, or iOS companion views.

See also:

- `docs/qa/QA_FRONTEND_BACKEND_BOUNDARY.md`
- `docs/qa/QA_DASHBOARD_API_CONTRACT.md`
