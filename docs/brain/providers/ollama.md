# Ollama Brain Provider

Status: local scaffold, disabled by default.

The `ollama` BrainProvider adapts a user-managed local Ollama daemon through its OpenAI-compatible chat endpoint. It is optional and does not replace LM Studio as the default provider.

## Configuration

```env
OLLAMA_ENABLED=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=
OLLAMA_OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1
OLLAMA_TIMEOUT_SECONDS=60
OLLAMA_SUPPORTS_TOOL_CALLS=false
OLLAMA_SUPPORTS_STREAMING=false
```

Enable it only after Ollama is already installed, running, and has the model available locally. The agent does not install Ollama, pull models, start the daemon, or start listeners.

## Commands

```bash
python smart_agent.py brain providers
python smart_agent.py brain health --provider ollama
python smart_agent.py brain doctor --provider ollama
```

`brain providers` is metadata-only. `brain health --provider ollama` checks the configured local daemon status endpoint when the provider is enabled; it does not generate text. `brain doctor --provider ollama` reports setup and safety status.

## Behavior

- Chat uses `OLLAMA_OPENAI_COMPAT_BASE_URL` plus `/chat/completions`.
- Health checks use `OLLAMA_BASE_URL` plus `/api/tags`.
- Missing model config returns `requires_setup`.
- Daemon connection, timeout, HTTP, and malformed-response errors are normalized.
- Tool-call support is off by default and must be explicitly enabled only after local verification.
- Streaming is off by default and remains future work.

## Safety Boundary

Ollama provider work must not:

- remove or weaken LM Studio support
- change the default provider
- install Ollama
- pull or download models
- start the Ollama daemon
- call cloud APIs
- enable MCP
- execute tools directly
- store prompt history or model output in memory by default
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger

Runtime independence remains partial until provider fallback/router, benchmarks/evals, live validation, and the BRAIN release gate are complete.
