# M0 Minimal Working Skeleton

## Scope

Prove LM Studio/Qwopus chat, one safe tool, `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

## Non-Goals

No file access, web access, memory, email, contacts, calendar, messages, browser automation, or self-improvement.

## Requirements

- `smart_agent.py`
- LM Studio OpenAI-compatible `/v1/chat/completions`.
- Default base URL `http://localhost:1234/v1`.
- Model from `LMSTUDIO_MODEL`.
- `--no-tools` mode attaches no tools.
- `--debug` mode prints redacted debug details.
- Minimal system prompt only.
- No forced JSON, ReAct, or manual chat template.
- Preserve user message exactly.
- Safe `time.get_current_time` tool.
- Unknown tools denied.
- Tool calls and denials audited.

## Risks

- Model output may request unknown tools.
- Audit logs may leak arguments.
- Harness may accidentally answer instead of model.

## Tests

- No-tool mode attaches no tools.
- Safe time tool is allowed.
- Unknown tool is denied.
- Tool result is appended with matching `tool_call_id`.
- Audit log records execution and denial.

## Approval Gate

None.
