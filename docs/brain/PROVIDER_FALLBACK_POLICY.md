# Provider Fallback Policy

Provider fallback is fail-closed by default.

## Defaults

- `BRAIN_FALLBACK_ENABLED=false`
- `BRAIN_AUTO_SWITCH_ON_FAILURE=false`
- `BRAIN_MAX_FALLBACK_ATTEMPTS=1`
- `BRAIN_ALLOW_CLOUD_FALLBACK=false`
- `BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS=true`

LM Studio remains the default provider unless `BRAIN_DEFAULT_PROVIDER` is explicitly configured. The default provider order is local-only: `lmstudio,llama_cpp_server,ollama,llama_cpp_inprocess,mlx`.

## Rules

1. An explicit user-selected provider wins when it is configured, available, and supports the requested task.
2. If the explicit provider is unavailable and fallback is disabled, the decision is blocked with a setup hint.
3. If fallback is enabled, fallback is bounded by `BRAIN_MAX_FALLBACK_ATTEMPTS`.
4. Cloud or paid providers are never fallback candidates unless `BRAIN_ALLOW_CLOUD_FALLBACK=true` and a future policy review approves the provider.
5. Tool-call tasks require provider tool-call support when `BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS=true`.
6. No-tools chat may use providers that do not support tool calls.
7. Provider routing does not execute model calls, tools, approvals, memory writes, or provider config changes.
8. Routing decisions are returned as structured evidence with `audit_event` metadata for callers to persist through the approved audit path.

## Commands

```bash
python smart_agent.py brain fallback-status
python smart_agent.py brain switch lmstudio --dry-run
```

`brain switch` is dry-run only in this milestone. It does not persist config or switch the live runtime.
