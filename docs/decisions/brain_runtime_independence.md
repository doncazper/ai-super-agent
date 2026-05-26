# Brain Runtime Independence Architecture

Status: accepted for staged implementation; complete through BRAIN-07 local provider scaffolds
Date: 2026-05-25
Prompt: BRAIN-01

## Context

The current Python agent talks directly to LM Studio through `agent/core/lmstudio_client.py`. That path is local, OpenAI-compatible, and already supports Qwopus-style no-tool chat and tool-call payloads, so it must remain supported. The hard dependency on one runtime, however, makes future local runtimes harder to test, benchmark, and swap without touching the orchestration core.

## Decision

Introduce a future `BrainRuntimeGateway` as a provider-neutral model interface. The gateway will sit between the orchestrator and concrete model runtimes, while preserving existing LM Studio behavior. As of BRAIN-07, LM Studio is wrapped behind a provider adapter and disabled-by-default llama.cpp server, Ollama, llama-cpp-python in-process, and MLX stub scaffolds exist; fallback routing and provider switching remain future work.

The gateway must support:

- no-tools chat with unchanged prompt/message semantics;
- OpenAI-style tool-call compatibility for brokered tools;
- provider health checks and setup diagnostics;
- local/mock providers for tests;
- fallback decisions that are explicit, audited where useful, and never silently move to paid/cloud APIs;
- lazy provider loading so startup does not import heavy runtime packages;
- quality regression checks before any default provider change.

## Provider Roles

LM Studio remains the current default provider and compatibility baseline. llama.cpp server and Ollama now have disabled-by-default local provider scaffolds for user-managed runtimes. `llama-cpp-python` is an optional in-process local provider that must never become an implicit dependency. MLX is an Apple Silicon experimental strategy/stub that cannot generate text until a later prompt approves implementation. Cloud APIs are optional/stubbed and disabled by default. Mock/test providers are required for deterministic tests.

MCP is not a brain runtime. It may be considered later as optional tool interoperability, but it must not be required to chat, route, or run local tools.

## Safety Boundary

This decision does not change runtime behavior. Future runtime work must not remove LM Studio, install runtimes, download models, call paid/cloud APIs by default, start network listeners, enable MCP servers, or weaken ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

All model-generated tool calls still go through ToolBroker. Provider selection must not grant tools, permissions, memory access, connector access, or approval.

## Consequences

- The orchestrator can later depend on a provider-neutral gateway instead of `LMStudioClient`.
- LM Studio/Qwopus behavior remains the regression baseline.
- Provider commands can be planned now, but executable commands require later implementation, command registry updates, tests, and release gates.
- Startup overhead becomes a first-class requirement for every provider.
