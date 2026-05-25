# Runtime Workflow Runner

Runtime workflow runner v1 registers workflow metadata and creates job records. It does not execute tool calls.

## Supported Metadata Workflows

- `daily_briefing`
- `connector_doctor`
- `eval_safe`
- `audit_summary`
- `email_send` as a blocked CRITICAL example

## Execution Boundary

`workflows run <workflow_id>` creates an in-process job record only. A future executor must still route all real work through `ToolBroker` and preserve policy, permission, approval, and audit gates.

## Risk Rules

- SAFE/LOW workflows can become queued metadata jobs.
- HIGH workflows require approval before any future execution.
- CRITICAL workflows are blocked in runtime v1.
- Unknown workflows are denied.

## CLI

```bash
python smart_agent.py workflows list
python smart_agent.py workflows run connector_doctor
```

