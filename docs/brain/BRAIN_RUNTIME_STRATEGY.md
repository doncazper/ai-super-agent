# Brain Runtime Strategy

The Brain Runtime Independence Track decouples the agent brain from one concrete model runtime while preserving the current LM Studio/Qwopus path.

## Scope

The future `BrainRuntimeGateway` is the model-facing boundary for chat completions, tool-call-capable completions, health checks, setup hints, fallback decisions, and benchmark/eval metadata.

The gateway is not a tool executor. It must not bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger. It must not decide permissions or execute platform, web, file, connector, memory, send, or write actions.

## Baseline Behavior

Current baseline:

- `LMStudioClient` is the concrete model client.
- `Orchestrator` sends messages to that client.
- Tool schemas are attached only after deterministic routing.
- Model tool calls are executed only by `ToolBroker`.
- `--no-tools` remains clean no-tool chat.

`BRAIN-01` is documentation and roadmap only. It does not change this baseline. `BRAIN-02` through `BRAIN-09` add the provider-neutral interface, lazy registry, LM Studio adapter, disabled-by-default llama.cpp server, Ollama, llama-cpp-python in-process and MLX scaffolds, mock-first benchmark/eval/report commands, and dry-run provider routing/fallback decisions. LM Studio remains the default compatibility baseline, fallback remains disabled by default, and no provider router decision changes the live runtime unless a future approved gateway wires it in.

## Gateway Responsibilities

Future gateway responsibilities:

- select a configured provider;
- call the provider using a shared message/tool schema contract;
- normalize provider errors;
- report setup-required/unavailable states;
- expose provider health and capability metadata;
- keep provider imports lazy;
- support deterministic mock providers for tests.

## Non-Responsibilities

The gateway must not:

- install or download model runtimes;
- start provider daemons or network listeners;
- enable MCP servers;
- call paid/cloud APIs by default;
- rewrite user messages for routing;
- attach tools in no-tools mode;
- approve or execute tools;
- store prompts, responses, tool args, or personal data in memory by default.

## Planned Track

1. Brain runtime architecture and LM Studio decoupling.
2. BrainProvider interface and model registry.
3. LM Studio provider refactor.
4. llama.cpp server provider.
5. Ollama provider.
6. llama-cpp-python in-process provider.
7. MLX provider strategy/stub.
8. Model health, benchmark, and quality evals.
9. Provider fallback and model router.
10. Optional MCP interop decision and adapters.
11. Brain runtime release gate.
