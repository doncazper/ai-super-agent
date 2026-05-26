# Model Routing Policy

The model router chooses a brain provider from configuration and task metadata. It is not a policy engine, approval system, tool executor, or model runtime.

## Inputs

- requested provider
- task type
- tool-call requirement
- streaming requirement
- JSON/schema requirement
- configured provider order
- task-provider map
- safe/no-tools mode

Provider health checks are explicit diagnostics. Normal routing does not generate text or call provider `/chat/completions`.

## Decision Output

Router decisions include:

- `selected_provider`
- `reason`
- fallback status and attempts
- provider order considered
- whether health was checked
- audit metadata
- safety flags confirming no model call, no tool execution, unchanged policy, and unchanged approval rules

## Safety Boundaries

- Provider selection never grants tools.
- Provider selection never changes ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger behavior.
- Provider output remains model output and cannot approve or execute actions.
- `--no-tools` remains clean and may route to providers without tool-call support.
- Tool-call tasks fail closed when the selected provider lacks verified tool-call support.

## Command

```bash
python smart_agent.py brain route "Summarize this without tools" --no-tools
python smart_agent.py brain route "Use a tool-capable model for weather" --requires-tool-calls
```

The command is an explanation path only. It does not call the model.
