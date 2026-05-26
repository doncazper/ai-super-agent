# llama.cpp Server Provider

Status: BRAIN-04 scaffolded and locally tested with mocked HTTP responses

The `llama_cpp_server` provider supports a user-managed OpenAI-compatible llama.cpp server. The agent never installs llama.cpp, never downloads models, and never starts `llama-server` automatically.

## Configuration

```bash
LLAMA_CPP_SERVER_ENABLED=false
LLAMA_CPP_SERVER_BASE_URL=http://localhost:8080/v1
LLAMA_CPP_SERVER_MODEL=
LLAMA_CPP_SERVER_TIMEOUT_SECONDS=60
LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS=false
LLAMA_CPP_SERVER_SUPPORTS_STREAMING=false
```

The provider remains disabled until `LLAMA_CPP_SERVER_ENABLED=true` and `LLAMA_CPP_SERVER_MODEL` are set. LM Studio remains the default provider.

## Commands

```bash
python smart_agent.py brain providers
python smart_agent.py brain doctor --provider llama_cpp_server
python smart_agent.py brain health --provider llama_cpp_server
```

`brain providers` is metadata-only. `brain doctor` and `brain health` may run a lightweight `/v1/models` check when the provider is enabled, but they do not generate model text, execute tools, start a server, download models, or write memory.

## Tool Calls

Tool-call support is disabled by default. Set `LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS=true` only after verifying the specific server build supports OpenAI-compatible tool calls. If tools are attached while support is disabled, the provider fails closed with a setup hint instead of silently dropping or executing tool calls.

## Safety Boundary

The provider:

- uses only the configured local OpenAI-compatible endpoint;
- returns `BrainChatResponse` and `BrainToolCall` data;
- does not execute tools;
- does not bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger;
- does not read personal data;
- does not store prompt history or model output in memory;
- does not call cloud or paid APIs by default.

Live validation is opt-in and requires the user to start/configure the server outside the agent.
