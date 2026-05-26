# MLX Provider Strategy And Stub

Status: experimental stub, disabled by default.

The MLX provider prepares a future Apple Silicon optimized brain backend without adding MLX as a hard dependency. The current scaffold is intentionally non-executable: it can be listed and diagnosed, but it cannot generate text, import MLX, load a model, start a server, download models, or become the default provider.

## Safe Defaults

```bash
MLX_PROVIDER_ENABLED=false
MLX_PROVIDER_MODE=server
MLX_SERVER_BASE_URL=http://localhost:8081/v1
MLX_MODEL=
MLX_SUPPORTS_TOOL_CALLS=false
MLX_LOAD_ON_STARTUP=false
```

`BRAIN_DEFAULT_PROVIDER` remains `lmstudio`.

## Modes

- `server`: future OpenAI-compatible MLX/MLX-LM server adapter.
- `inprocess`: future in-process MLX adapter.

Both modes are stubbed in BRAIN-07. Neither mode performs network calls, native imports, model loading, or model generation.

## Diagnostics

```bash
python smart_agent.py brain providers
python smart_agent.py brain doctor --provider mlx
python smart_agent.py brain health --provider mlx
```

These commands are metadata/setup diagnostics. They do not execute tools, generate model text, load MLX, or write memory.

## Risks

- MLX is Apple Silicon oriented and may not apply to all runtimes.
- Native package/build behavior needs a dedicated future implementation and release gate.
- In-process mode would share process memory and crash isolation with the agent.
- Server mode would need explicit local endpoint validation and timeout/error handling.
- Tool-call support is unverified and remains disabled by default.

## Future Approval Gates

A future implementation must add:

- no-startup-import tests;
- mocked server and/or in-process tests;
- no model download/install behavior;
- ToolBroker-only tool-call compatibility tests;
- provider routing/fallback policy tests;
- command registry and feature maturity updates;
- release-gate evidence before any default-provider change.
