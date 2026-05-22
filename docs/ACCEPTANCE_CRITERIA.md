# Acceptance Criteria

## Global

- Normal chat uses the minimal system prompt and preserves the user message.
- Tools are attached only when needed or allowed by the selected mode.
- Every tool execution goes through `ToolBroker.execute()`.
- Policy decisions are enforced by Python code.
- High and critical actions cannot be approved by the model.
- Unknown tools and capabilities are denied.
- Denials, approvals, executions, and failures are audited.
- Secrets are redacted from logs.
- Untrusted content is treated as data, never instructions.

## M0

- `python smart_agent.py --no-tools "Explain RCS vs iMessage"` sends no tool schemas.
- `python smart_agent.py --debug "What time is it?"` can expose the time tool.
- `time.get_current_time` is allowed.
- Unknown tools are denied.
- Tool results are appended with matching `tool_call_id`.
- Audit log records execution and denial.
