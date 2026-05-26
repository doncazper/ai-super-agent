# Model Registry

Status: BRAIN-07 scaffolded and locally tested

The model registry is a lightweight provider catalog for brain runtimes. It records provider factories and metadata, lists providers without model loading, and runs explicit health checks only when requested.

## Safe Defaults

Configuration defaults:

- `BRAIN_DEFAULT_PROVIDER=lmstudio`
- `BRAIN_PROVIDER_ORDER=lmstudio,llama_cpp_server,ollama,llama_cpp_inprocess,mlx`
- `BRAIN_TASK_PROVIDER_MAP={}`
- `BRAIN_FALLBACK_ENABLED=false`
- `BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS=true`
- `BRAIN_AUTO_SWITCH_ON_FAILURE=false`
- `BRAIN_MAX_FALLBACK_ATTEMPTS=1`
- `BRAIN_ALLOW_CLOUD_FALLBACK=false`
- `BRAIN_PROVIDER_HEALTH_TIMEOUT_SECONDS=5`
- `BRAIN_MOCK_PROVIDER_ENABLED=false` by default, true only in tests when explicitly set

LM Studio remains the default compatibility target. `BRAIN-03` registers LM Studio lazily and keeps it as the default provider. `BRAIN-04`, `BRAIN-05`, `BRAIN-06`, and `BRAIN-07` add lazy disabled-by-default llama.cpp server, Ollama, llama-cpp-python in-process, and MLX stub registrations.

## Registry API

- `register_provider`
- `list_providers`
- `list_provider_status`
- `provider_status`
- `get_provider`
- `require_provider`
- `default_provider`
- `configured_providers`
- `health_summary`

`list_providers`, `list_provider_status`, and `provider_status` are metadata-first and do not instantiate providers unless an instance is already cached. `health_summary`, `configured_providers`, `get_provider`, and `default_provider` may instantiate a registered provider and are explicit runtime checks.

The default registry includes lazy LM Studio, llama.cpp server, Ollama, llama-cpp-python in-process, and MLX stub registrations. Listing providers does not import concrete provider modules; the llama.cpp server, Ollama, llama-cpp-python, and MLX registrations report `disabled` unless explicitly enabled in config.

## Provider Status

Unknown providers return structured `unknown` status with setup hints. Registered lazy providers report `registered_lazy` before initialization. Initialized providers report configured and available booleans.

## Startup and Overhead

Importing the registry must not import LM Studio, Ollama, llama.cpp, MLX, model packages, native runtimes, or MCP adapters. Provider implementations are lazy-loaded by explicit provider access, and health checks must not load or download a large model unless that provider explicitly documents such behavior and tests cover it.

## Safety Boundary

The registry is not a permission system, tool executor, or fallback policy engine. It must not:

- execute tools;
- enable providers without config;
- call paid/cloud APIs by default;
- start network listeners or provider daemons;
- install packages or download models;
- write prompt history or model output to memory;
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

BRAIN-09 adds provider routing/fallback decision logic in `agent.brain.provider_router` and `agent.brain.fallback`, but default runtime behavior remains unchanged. Routing decisions are metadata only unless a future approved gateway uses them to select a configured provider.
