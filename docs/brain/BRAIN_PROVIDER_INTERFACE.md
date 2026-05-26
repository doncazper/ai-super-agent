# BrainProvider Interface

Status: BRAIN-02 scaffolded and locally tested

The `BrainProvider` contract is the provider-neutral model runtime boundary. It lets future LM Studio, llama.cpp server, Ollama, llama-cpp-python, MLX, and test providers expose the same chat, model listing, health, and capability metadata without changing tool execution semantics.

## Current Boundary

`BRAIN-02` added interfaces, dataclasses, a lazy registry, and a deterministic mock provider. `BRAIN-03` adds `LMStudioBrainProvider`, which delegates to the existing `LMStudioClient` so LM Studio/Qwopus remains the compatibility baseline.

## Provider Contract

Every provider implements:

- `provider_id()`
- `provider_name()`
- `is_configured()`
- `is_available()`
- `health_check()`
- `list_models()`
- `chat(messages, tools=None, tool_choice=None, settings=None)`
- `supports_tool_calls()`
- `supports_streaming()`
- `supports_reasoning_content()`
- `supports_json_schema()`
- optional `estimate_tokens()`
- optional `close()` / `shutdown()`

The provider returns model output and provider-neutral tool-call data. It must not execute tools, grant permissions, approve actions, write memory, start model runtimes, download models, or call paid/cloud services by default.

## Shared Models

- `BrainMessage`
- `BrainToolSpec`
- `BrainToolCall`
- `BrainChatRequest`
- `BrainChatResponse`
- `BrainProviderHealth`
- `BrainProviderStatus`
- `BrainModelInfo`
- `BrainGenerationSettings`
- `BrainProviderError`

`BrainGenerationSettings` carries `temperature`, `top_p`, `max_tokens`, `stop`, and `stream`. Provider errors normalize into `BrainProviderError` so CLI diagnostics and future fallback logic can report setup-required, unavailable, and provider-failure states consistently.

## Tool Safety

Tool calls are structured data only. Future orchestration may pass provider-neutral tool-call records to the existing ToolBroker path, but providers themselves must not invoke `ToolBroker`, bypass `PolicyEngine`, bypass `PermissionManager`, bypass `ApprovalManager`, bypass `AuditLogger`, or execute side effects.

## Mock Provider

`MockBrainProvider` exists for deterministic tests and evals. It supports:

- configured/unavailable states;
- deterministic no-tool responses;
- mocked provider-neutral tool calls;
- normalized unavailable-provider errors;
- lightweight model metadata;
- simple side-effect-free token estimates.

The mock provider is enabled only by explicit test config such as `BRAIN_MOCK_PROVIDER_ENABLED=true`.

## LM Studio Provider

`LMStudioBrainProvider` preserves the existing low-level LM Studio client and returns provider-neutral `BrainChatResponse` records. It normalizes tool calls into `BrainToolCall` while preserving malformed raw tool arguments so the existing ToolBroker error path still handles them. It does not execute tools directly.
