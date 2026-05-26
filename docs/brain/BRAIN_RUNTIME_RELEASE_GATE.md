# Brain Runtime Release Gate

Status: passed locally for the Brain Runtime Independence scaffold on 2026-05-25.

This gate validates the provider-neutral brain runtime groundwork without claiming that LM Studio is fully optional for normal chat yet.

## Scope

- Validate BrainProvider interface, model registry, LM Studio provider wrapping, local-provider scaffolds, model health/benchmark/eval commands, provider fallback/router metadata, and MCP interop stubs.
- Confirm current LM Studio/Qwopus behavior remains the compatibility baseline.
- Confirm alternate providers remain disabled, explicit, lazy, and setup-gated.
- Confirm MCP remains optional interoperability, not the brain runtime.

## Non-Goals

- No LM Studio removal.
- No default provider change.
- No model runtime installation.
- No model download or pull.
- No paid/cloud API call.
- No MCP server enablement.
- No network listener startup.
- No personal-data tool enablement.
- No ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger weakening.

## Validation Results

| Check | Result | Evidence |
|---|---|---|
| Brain provider tests | Passed | `./.venv/bin/python -m pytest tests/brain tests/mcp tests/test_brain_runtime_architecture_docs.py tests/test_feature_maturity_docs.py tests/test_command_registry.py -q`: 97 passed |
| Startup policy validation | Passed | `make policy-check`: startup policy ok |
| Capability manifest validation | Passed | `make policy-check`: capability validation exited successfully |
| Command registry validation | Passed | `./.venv/bin/python smart_agent.py commands validate`: status ok, 443 commands |
| Provider registry status | Passed | `brain providers` listed LM Studio plus disabled local-provider scaffolds without model generation |
| Default provider status | Passed | `brain status` reports `lmstudio` as default and fallback disabled |
| LM Studio health diagnostic | Passed | `brain health --provider lmstudio` returned configured/available metadata with `no_model_generation=true` and `no_tool_execution=true` |
| Mock benchmark | Passed | `brain benchmark --safe` wrote a redacted local report with no personal data and no high-risk tools |
| Mock eval | Passed | `brain eval --safe` passed 9 safe mock cases |
| Provider router smoke | Passed | `brain route "hello" --no-tools` selected LM Studio without model or tool calls |
| MCP decision/status | Passed | `brain mcp-decision`, `mcp status`, `mcp doctor`, `mcp server --dry-run`, and `mcp clients` report disabled/no-listener/no-tool-exposure states |
| Startup optional import guard | Passed | importing `smart_agent` did not load `llama_cpp`, `mlx`, `mlx_lm`, `ollama`, or `mcp` modules |

## Provider Status

| Provider | Status | Default | Live use |
|---|---|---:|---|
| `lmstudio` | Registered/configured compatibility provider | yes | Existing LM Studio/Qwopus path remains supported |
| `llama_cpp_server` | Disabled scaffold | no | Requires user-managed server and explicit config in a future approved run |
| `ollama` | Disabled scaffold | no | Requires user-managed daemon/model and explicit config in a future approved run |
| `llama_cpp_inprocess` | Disabled scaffold | no | Requires user-installed dependency and local model path in a future approved run |
| `mlx` | Disabled strategy/stub | no | Non-generating stub only |
| `mock` | Test-only provider | no | Used by safe benchmark/eval fixtures |

## Safety Findings

- Providers return model data and provider-neutral tool-call records only; tools still execute through the existing ToolBroker path.
- Fallback is disabled by default.
- Automatic switch-on-failure is disabled.
- Cloud/paid fallback is disabled.
- `brain switch` is dry-run only and does not persist provider config.
- Safe benchmark/eval commands use deterministic mock fixtures by default.
- MCP server/client stubs are disabled by default and expose no tools.
- No optional model runtime module loads at `smart_agent` import.

## Readiness Result

Release gate result: pass for local scaffold and safety boundary validation.

LM Studio dependency status: partially optional. The provider abstraction, registry, local-provider scaffolds, mock evals, fallback metadata, and MCP boundary exist, but normal live chat still relies on the existing LM Studio/Qwopus-compatible path until a future approved Brain Runtime Gateway wiring prompt.

## Remaining Limitations

- No live llama.cpp server, Ollama, llama-cpp-python, or MLX model validation was run.
- No live answer-quality baseline beyond provider health diagnostics was claimed.
- The router/fallback layer is metadata-only and is not yet wired as the normal chat gateway.
- MCP remains a disabled stub, not an enabled server/client integration.
- Manual QA remains needed for configured provider setup paths.
