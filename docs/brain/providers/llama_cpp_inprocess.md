# llama-cpp-python In-Process Provider

Status: optional scaffold, disabled by default.

The `llama_cpp_inprocess` BrainProvider prepares an in-process backend for the optional `llama-cpp-python` package. It is intentionally conservative because loading a model inside the agent process changes the reliability and isolation profile.

## Configuration

```env
LLAMA_CPP_INPROCESS_ENABLED=false
LLAMA_CPP_INPROCESS_MODEL_PATH=
LLAMA_CPP_INPROCESS_N_CTX=8192
LLAMA_CPP_INPROCESS_N_GPU_LAYERS=-1
LLAMA_CPP_INPROCESS_THREADS=auto
LLAMA_CPP_INPROCESS_SUPPORTS_TOOL_CALLS=false
LLAMA_CPP_INPROCESS_LOAD_ON_STARTUP=false
LLAMA_CPP_INPROCESS_MAX_LOADED_MODELS=1
```

The agent never installs `llama-cpp-python`, downloads GGUF models, or loads a model at startup. Enable this provider only after you have installed the optional dependency and selected a local model path yourself.

## Commands

```bash
python smart_agent.py brain providers
python smart_agent.py brain health --provider llama_cpp_inprocess
python smart_agent.py brain doctor --provider llama_cpp_inprocess
```

Health and doctor checks report dependency/configuration status. They do not load a model or generate text. Chat loads the backend lazily only when this provider is explicitly selected by future routing work.

## In-Process Risks

- Process memory: model weights share the agent process.
- Crash isolation: native runtime failures can affect the agent process.
- Load time: large GGUF models can take significant time to load.
- Build complexity: Metal/GPU acceleration depends on the local package build.
- Operational clarity: this provider should not become the default without a dedicated release gate.

## Safety Boundary

This provider must not:

- install `llama-cpp-python`
- download GGUF models
- load a real model in tests
- load a model at startup
- become the default provider
- assume tool-call support by default
- call paid/cloud APIs
- enable MCP
- execute tools directly
- store prompt history or model output in memory by default
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger

Runtime independence remains partial until provider fallback/router, benchmark/eval coverage, live validation, and the BRAIN release gate are complete.
