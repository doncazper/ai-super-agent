<<<PROMPT_PACK_START>>>
pack_id: brain-runtime-independence-v1
pack_title: Brain Runtime Independence Track
created_by: user
mode: controlled_batch_until_blocked
default_execution: sequential
requires_sdlc: true
requires_prompt_ledger: true
requires_feature_maturity_update: true
priority: high

pack_summary:
  - This prompt pack removes hard dependency on LM Studio by introducing a Brain Runtime Gateway and multiple model-provider backends.
  - LM Studio remains supported, but becomes one provider among several.
  - Target backends include LM Studio, llama.cpp server, Ollama, llama-cpp-python in-process, MLX/Apple Silicon strategy/stub, cloud API optional/stub, and mock/test provider.
  - This pack does not remove LM Studio immediately.
  - This pack does not change the ToolBroker/Policy/Approval/Audit safety model.
  - This pack does not require MCP.
  - MCP is treated as optional interoperability, not the model runtime.
  - This pack prioritizes lower overhead, provider abstraction, model health, benchmarks, fallback, and safe migration.

global_rules:
  - Follow SPEC.md.
  - Follow docs/SDLC.md.
  - Follow AGENTS.md.
  - Build safety first, capabilities second.
  - Preserve normal no-tool chat quality.
  - Preserve existing Qwopus/LM Studio behavior while adding abstraction.
  - Do not weaken policy.
  - Do not bypass ToolBroker.
  - Do not bypass PolicyEngine.
  - Do not bypass PermissionManager.
  - Do not bypass ApprovalManager.
  - Do not bypass AuditLogger.
  - Do not enable personal-data tools by default.
  - Do not change tool execution semantics without tests.
  - Do not make the harness write final answers.
  - Do not add MCP as required dependency.
  - Do not install model runtimes automatically.
  - Do not download models automatically.
  - Do not call paid/cloud APIs by default.
  - Do not introduce heavy imports at startup.
  - Do not break CLI-only operation.
  - Update CHANGELOG.md.
  - Update docs/PROJECT_STATE.md.
  - Update docs/FEATURE_REGISTRY.md.
  - Update docs/FEATURE_MATURITY.md.
  - Update docs/FEATURE_ROADMAP.md if status/order changes.
  - Update docs/COMMAND_REGISTRY.md if commands are added/changed.
  - Update docs/COMMAND_TEST_MATRIX.md if QA steps are added/changed.
  - Update docs/COMPLETION_REPORT.md.
  - Update docs/RISK_REGISTER.md if risk changed.
  - Update docs/THREAT_MODEL.md if threat surface changed.
  - Update docs/RELEASE_CHECKLIST.md where release-gate checks change.

stop_conditions:
  - approval_gate
  - failing_tests_not_safely_fixable
  - docs_validation_failure_not_safely_fixable
  - package_install_required
  - model_download_required
  - paid_api_required
  - personal_data_access_required
  - security_policy_change_required
  - runtime_behavior_change_required_beyond_scope
  - startup_overhead_regression_not_understood
  - ambiguous_requirements

expected_prompt_ids:
  - BRAIN-01
  - BRAIN-02
  - BRAIN-03
  - BRAIN-04
  - BRAIN-05
  - BRAIN-06
  - BRAIN-07
  - BRAIN-08
  - BRAIN-09
  - BRAIN-10
  - BRAIN-11

<<<PROMPT_START id="BRAIN-01" order="1">>
title: Brain runtime architecture and LM Studio decoupling
category: core
risk_level: LOW
approval_gate: false
depends_on: []
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create Brain Runtime Independence architecture and roadmap.

Goal:
Plan the transition from LM Studio being the hardcoded model runtime to a provider-neutral Brain Runtime Gateway. LM Studio should remain supported, but the agent should be able to use multiple model runtimes while preserving no-tool chat quality, tool-call behavior, policy, audit, and tests.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- agent/core/lmstudio_client.py, if present
- agent/core/orchestrator.py
- agent/core/router.py
- agent/core/tool_broker.py
- tests/

Follow the mini-SDLC.

Scope:
- Documentation and roadmap.
- Architecture decision record.
- No provider implementation yet.
- No breaking runtime changes.

Non-goals:
- Do not remove LM Studio.
- Do not add model downloads.
- Do not install llama.cpp/Ollama/MLX.
- Do not require MCP.
- Do not call external paid/cloud APIs.
- Do not change ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger behavior.
- Do not change normal chat behavior.

Create:
- docs/decisions/brain_runtime_independence.md
- docs/brain/BRAIN_RUNTIME_STRATEGY.md
- docs/brain/MODEL_PROVIDER_STRATEGY.md
- docs/brain/LM_STUDIO_DECOUPLING_PLAN.md
- docs/brain/MODEL_PROVIDER_REQUIREMENTS.md
- docs/brain/MCP_INTEROP_DECISION.md

Define:
1. BrainRuntimeGateway as provider-neutral model interface.
2. LM Studio as current provider.
3. llama.cpp server as lightweight OpenAI-compatible local provider.
4. Ollama as local daemon/provider option.
5. llama-cpp-python in-process as optional lower-external-dependency provider.
6. MLX as Apple Silicon experimental strategy/stub.
7. Cloud API provider as optional/stubbed and disabled by default.
8. Mock/test provider as required for tests.
9. MCP as optional tool interoperability, not brain runtime.
10. Provider health checks.
11. Provider benchmarks/evals.
12. Provider fallback rules.
13. Tool-call compatibility requirements.
14. No-tools chat preservation.
15. Model quality regression strategy.
16. Startup overhead and lazy-load requirements.

Add roadmap track:
"Brain Runtime Independence Track"

Planned prompts:
1. Brain runtime architecture and LM Studio decoupling
2. BrainProvider interface and model registry
3. LM Studio provider refactor
4. llama.cpp server provider
5. Ollama provider
6. llama-cpp-python in-process provider
7. MLX provider strategy/stub
8. Model health, benchmark, and quality evals
9. Provider fallback and model router
10. Optional MCP interop decision and adapters
11. Brain runtime release gate

Planned commands to add to COMMAND_REGISTRY as planned/stubbed:
- python smart_agent.py brain providers
- python smart_agent.py brain status
- python smart_agent.py brain doctor
- python smart_agent.py brain health
- python smart_agent.py brain benchmark
- python smart_agent.py brain eval
- python smart_agent.py brain switch <provider>
- python smart_agent.py brain fallback-status
- python smart_agent.py brain mcp-decision

Update:
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md

Run:
- docs validation if present
- startup policy validation
- command registry validation if present
- full test suite if practical

Final report:
- docs created
- roadmap updates
- risk updates
- tests/validations run
- next recommended prompt
<<<PROMPT_END id="BRAIN-01">>

<<<PROMPT_START id="BRAIN-02" order="2">>
title: BrainProvider interface and model registry
category: core
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-01"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build BrainProvider interface and model registry.

Goal:
Create the provider-neutral interface that all model runtimes must implement, plus a registry that can list, configure, health-check, and select model providers without hardcoding LM Studio.

Scope:
- Interfaces/models/registry.
- Mock/test provider.
- Tests.
- No real provider migration yet.

Non-goals:
- Do not remove LM Studio.
- Do not implement llama.cpp/Ollama/MLX yet.
- Do not call external/cloud providers.
- Do not download models.
- Do not change tool execution semantics.

Create:
- agent/brain/
  - __init__.py
  - base.py
  - models.py
  - registry.py
  - errors.py
  - config.py
  - mock_provider.py
- tests/brain/test_brain_provider_interface.py
- tests/brain/test_model_registry.py
- docs/brain/BRAIN_PROVIDER_INTERFACE.md
- docs/brain/MODEL_REGISTRY.md

BrainProvider interface:
- provider_id()
- provider_name()
- is_configured()
- is_available()
- health_check()
- list_models()
- chat(messages, tools=None, tool_choice=None, settings=None)
- supports_tool_calls()
- supports_streaming()
- supports_reasoning_content()
- supports_json_schema()
- estimate_tokens(), optional
- close()/shutdown(), optional

Models:
- BrainMessage
- BrainToolSpec
- BrainToolCall
- BrainChatRequest
- BrainChatResponse
- BrainProviderHealth
- BrainModelInfo
- BrainGenerationSettings
- BrainProviderError

Registry:
- register_provider
- list_providers
- get_provider
- default_provider
- configured_providers
- health_summary
- provider status without heavy initialization where possible

Config:
- BRAIN_DEFAULT_PROVIDER=lmstudio
- BRAIN_PROVIDER_ORDER=lmstudio,llama_cpp_server,ollama,llama_cpp_inprocess,mlx,mock
- BRAIN_FALLBACK_ENABLED=false by default
- BRAIN_PROVIDER_HEALTH_TIMEOUT_SECONDS=5
- BRAIN_MOCK_PROVIDER_ENABLED=true in tests only

Requirements:
1. Registry import must be lightweight.
2. Provider status should not load a large model.
3. Provider health checks must be explicit.
4. Mock provider must support deterministic no-tool responses and mocked tool calls.
5. Tool-call response schema must be provider-neutral.
6. Settings must include temperature, top_p, max_tokens, stop, stream.
7. Provider errors must be normalized.
8. No personal data access.
9. No ToolBroker bypass.
10. Existing tests should still pass.

Tests:
- BrainProvider interface can be implemented by mock.
- Registry loads providers.
- Unknown provider handled.
- Default provider configurable.
- Mock no-tool chat works.
- Mock tool-call response works.
- Provider error normalized.
- Registry import does not import heavy provider modules.
- Health summary uses mock provider.

Update:
- docs/brain/BRAIN_PROVIDER_INTERFACE.md
- docs/brain/MODEL_REGISTRY.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- CHANGELOG.md

Run:
- targeted brain tests
- full test suite if practical
- startup policy validation

Final report:
- interface created
- registry created
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-02">>

<<<PROMPT_START id="BRAIN-03" order="3">>
title: LM Studio provider refactor
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-02"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Refactor LM Studio into a BrainProvider.

Goal:
Keep existing LM Studio behavior working while moving direct LM Studio access behind the new BrainProvider interface.

Scope:
- Refactor existing lmstudio client into provider adapter.
- Preserve current commands and behavior.
- Tests.

Non-goals:
- Do not remove old code until compatibility is proven.
- Do not change prompt quality.
- Do not change no-tools mode behavior.
- Do not change ToolBroker flow.
- Do not make LM Studio less reliable.
- Do not add new model providers in this prompt.

Create/update:
- agent/brain/providers/lmstudio.py
- agent/core/lmstudio_client.py, if needed for compatibility wrapper
- agent/core/orchestrator.py, only as needed to route through BrainRuntimeGateway/provider
- tests/brain/test_lmstudio_provider.py
- tests/test_lmstudio_loop.py or existing tests

Requirements:
1. LM Studio provider uses existing base URL/model env vars.
2. Existing LMSTUDIO_BASE_URL and LMSTUDIO_MODEL continue to work.
3. Existing no-tools command path still attaches no tools.
4. Existing debug tool-call path still works.
5. Provider returns provider-neutral BrainChatResponse.
6. Tool calls are normalized into BrainToolCall.
7. Reasoning content cleanup remains compatible.
8. Error messages remain user-friendly:
   - server not reachable
   - model missing
   - model not loaded/unknown
   - malformed response
   - timeout
9. Doctor should show LM Studio provider status.
10. LM Studio remains default provider until later prompt changes default selection.
11. Tests use mocks where possible; live LM Studio tests remain opt-in.

Commands:
- python smart_agent.py brain status
- python smart_agent.py brain doctor
- python smart_agent.py brain providers
if practical.

Tests:
- no-tools mode still attaches no tools.
- LM Studio provider request format matches existing expected payload.
- tool-call normalization works.
- missing LMSTUDIO_MODEL error remains clear.
- server unavailable handled.
- provider registry lists lmstudio.
- doctor includes lmstudio.
- no ToolBroker bypass introduced.
- full tests pass.

Update:
- README.md LM Studio setup if wording changes.
- docs/COMMAND_REGISTRY.md if commands added/changed.
- docs/brain/LM_STUDIO_DECOUPLING_PLAN.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run targeted tests and full tests if practical.

Final report:
- refactor summary
- compatibility status
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-03">>

<<<PROMPT_START id="BRAIN-04" order="4">>
title: llama.cpp server provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-03"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add llama.cpp server BrainProvider.

Goal:
Support a lightweight local model runtime using an OpenAI-compatible llama.cpp server, without requiring LM Studio.

Scope:
- Provider adapter.
- Config.
- Doctor/status.
- Tests with mocked HTTP responses.
- No model download.
- No server installation.

Non-goals:
- Do not install llama.cpp.
- Do not download models.
- Do not start llama-server automatically.
- Do not remove LM Studio.
- Do not change default provider yet.
- Do not assume tool-call support unless verified/configured.

Create:
- agent/brain/providers/llama_cpp_server.py
- tests/brain/test_llama_cpp_server_provider.py
- docs/brain/providers/llama_cpp_server.md

Config:
- LLAMA_CPP_SERVER_ENABLED=false
- LLAMA_CPP_SERVER_BASE_URL=http://localhost:8080/v1
- LLAMA_CPP_SERVER_MODEL=
- LLAMA_CPP_SERVER_TIMEOUT_SECONDS=60
- LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS=false by default unless verified
- LLAMA_CPP_SERVER_SUPPORTS_STREAMING=false or config-based

Commands:
- python smart_agent.py brain doctor --provider llama_cpp_server
- python smart_agent.py brain providers
- python smart_agent.py brain health --provider llama_cpp_server

Provider behavior:
1. OpenAI-compatible chat endpoint.
2. Optional /v1/models check.
3. Missing base URL/model returns setup hint.
4. Server unavailable returns clear error.
5. Tool-call support explicit/configurable.
6. If provider does not support tool calls, no-tool chat can still work.
7. Provider errors normalized.
8. No search/personal data behavior.
9. No server process start by default.
10. Registry lists provider as disabled unless enabled.

Tests:
- missing config returns setup hint.
- server health mock success.
- server unavailable handled.
- no-tool chat mock works.
- malformed response handled.
- tool-call unsupported path handled.
- provider registry lists llama_cpp_server.
- command registry updated.

Update:
- docs/brain/providers/llama_cpp_server.md
- README model runtimes section.
- .env.example.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/PROJECT_STATE.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- provider added
- config added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-04">>

<<<PROMPT_START id="BRAIN-05" order="5">>
title: Ollama provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-04"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add Ollama BrainProvider.

Goal:
Support Ollama as an optional local model runtime provider while preserving LM Studio and llama.cpp server behavior.

Scope:
- Provider adapter.
- Config.
- Doctor/status.
- Mocked tests.
- No model pulls/downloads.

Non-goals:
- Do not install Ollama.
- Do not pull models.
- Do not start Ollama daemon.
- Do not change default provider.
- Do not assume full OpenAI compatibility for every feature.
- Do not call cloud APIs.

Create:
- agent/brain/providers/ollama.py
- tests/brain/test_ollama_provider.py
- docs/brain/providers/ollama.md

Config:
- OLLAMA_ENABLED=false
- OLLAMA_BASE_URL=http://localhost:11434
- OLLAMA_MODEL=
- OLLAMA_OPENAI_COMPAT_BASE_URL=http://localhost:11434/v1
- OLLAMA_TIMEOUT_SECONDS=60
- OLLAMA_SUPPORTS_TOOL_CALLS=config-based false by default unless verified
- OLLAMA_SUPPORTS_STREAMING=config-based

Provider behavior:
1. Support OpenAI-compatible endpoint if configured.
2. Optionally support native Ollama endpoint if existing architecture allows; otherwise document as future.
3. Missing model returns setup hint.
4. Daemon unavailable returns clear error.
5. Provider errors normalized.
6. Tool-call support explicit/configurable.
7. No model pull/download.
8. Registry lists provider disabled unless enabled.
9. Health check does not generate text unless explicitly requested.

Commands:
- python smart_agent.py brain doctor --provider ollama
- python smart_agent.py brain health --provider ollama
- python smart_agent.py brain providers

Tests:
- missing model returns setup hint.
- health mock success.
- daemon unavailable handled.
- no-tool chat mock works.
- malformed response handled.
- tool-call unsupported path handled.
- provider registry lists ollama.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- provider added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-05">>

<<<PROMPT_START id="BRAIN-06" order="6">>
title: llama-cpp-python in-process provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-05"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add llama-cpp-python in-process provider scaffolding.

Goal:
Prepare an optional in-process local model backend to reduce dependency on external model server apps. Because in-process model loading can be heavy and installation-sensitive, implement safely as optional/stubbed unless dependency is already installed.

Scope:
- Provider scaffolding.
- Dependency detection.
- Config.
- Mocked tests.
- Docs.
- No automatic package install.
- No model download.

Non-goals:
- Do not install llama-cpp-python.
- Do not download GGUF models.
- Do not load a real model in tests.
- Do not make in-process provider default.
- Do not crash if dependency missing.
- Do not sacrifice process isolation without clear docs.

Create:
- agent/brain/providers/llama_cpp_inprocess.py
- tests/brain/test_llama_cpp_inprocess_provider.py
- docs/brain/providers/llama_cpp_inprocess.md

Config:
- LLAMA_CPP_INPROCESS_ENABLED=false
- LLAMA_CPP_INPROCESS_MODEL_PATH=
- LLAMA_CPP_INPROCESS_N_CTX=8192
- LLAMA_CPP_INPROCESS_N_GPU_LAYERS=-1
- LLAMA_CPP_INPROCESS_THREADS=auto
- LLAMA_CPP_INPROCESS_SUPPORTS_TOOL_CALLS=false by default
- LLAMA_CPP_INPROCESS_LOAD_ON_STARTUP=false
- LLAMA_CPP_INPROCESS_MAX_LOADED_MODELS=1

Provider behavior:
1. Detect dependency presence without importing heavy model runtime at core startup.
2. Missing dependency returns setup hint.
3. Missing model path returns setup hint.
4. Model loading is lazy and explicit.
5. Health check can report configured/missing without loading model.
6. In-process risks documented:
   - process memory
   - crash isolation
   - model load time
   - Metal/build complexity
7. No tests load real model.
8. Provider registry lists disabled unless enabled.
9. If dependency exists, still do not load model unless explicit.

Tests:
- dependency missing returns setup hint.
- model path missing returns setup hint.
- lazy import behavior.
- no model load on provider status.
- mock chat works via fake backend.
- provider error normalized.
- startup overhead safe.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- provider scaffolding added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-06">>

<<<PROMPT_START id="BRAIN-07" order="7">>
title: MLX provider strategy/stub
category: core
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-06"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Add MLX provider strategy and optional stub.

Goal:
Prepare for a future Apple Silicon optimized MLX/MLX-LM provider without making it a hard dependency or production default.

Scope:
- Decision record.
- Provider stub.
- Config.
- Tests for stub behavior.
- No MLX install.
- No model download.

Non-goals:
- Do not install MLX.
- Do not run MLX model.
- Do not start MLX server.
- Do not make MLX default.
- Do not load native modules at startup.

Create:
- agent/brain/providers/mlx.py
- tests/brain/test_mlx_provider_stub.py
- docs/brain/providers/mlx.md
- docs/decisions/mlx_provider_strategy.md

Config:
- MLX_PROVIDER_ENABLED=false
- MLX_PROVIDER_MODE=server|inprocess
- MLX_SERVER_BASE_URL=http://localhost:8081/v1
- MLX_MODEL=
- MLX_SUPPORTS_TOOL_CALLS=false
- MLX_LOAD_ON_STARTUP=false

Provider behavior:
1. Stub provider reports not configured by default.
2. Detects Apple Silicon if platform detection exists, but safely.
3. Missing dependency/server returns setup hint.
4. No model load.
5. No heavy import at startup.
6. Documents MLX as experimental until tested.
7. Supports future server/in-process modes.

Tests:
- stub lists provider.
- disabled by default.
- setup hint shown.
- no native import.
- no model load.
- Apple Silicon detection mocked.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- MLX strategy/stub added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-07">>

<<<PROMPT_START id="BRAIN-08" order="8">>
title: Model health, benchmark, and quality evals
category: tests
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-07"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build model health, benchmark, and quality evals.

Goal:
Compare brain providers safely using repeatable no-tool chat, tool-call compatibility, latency, error handling, and answer-quality evals.

Scope:
- Eval cases.
- Benchmark commands.
- Reports.
- Mock-first tests.
- Live provider evals opt-in.

Non-goals:
- Do not call paid/cloud providers by default.
- Do not access personal data.
- Do not run high-risk tools.
- Do not download models.
- Do not require every provider to be installed.

Create:
- agent/brain/health.py
- agent/brain/benchmark.py
- agent/brain/evals.py
- tests/brain/test_brain_health_benchmark_eval.py
- eval_cases/brain/
- reports/brain/.gitkeep
- docs/brain/BRAIN_EVALS.md
- docs/brain/BRAIN_BENCHMARKS.md

Commands:
- python smart_agent.py brain health
- python smart_agent.py brain health --provider <provider>
- python smart_agent.py brain benchmark --safe
- python smart_agent.py brain benchmark --provider <provider>
- python smart_agent.py brain eval --safe
- python smart_agent.py brain eval --provider <provider>
- python smart_agent.py brain report --last

Eval categories:
1. no-tool chat
2. no-tools mode attaches no tools
3. tool-call compatibility with mock safe tool
4. malformed tool-call handling
5. router prompt quality
6. refusal/approval-gate behavior
7. untrusted content handling
8. latency/timeouts
9. provider error handling
10. final answer quality rubric

Requirements:
1. Safe evals use mocks or no-risk prompts.
2. Live evals opt-in.
3. Personal data not used.
4. Tool calls use safe mock/time tool only.
5. Results include provider, model, latency, success/fail/skip.
6. Quality rubrics are conservative.
7. Reports saved under reports/brain.
8. Command registry updated.
9. Feature maturity updated based on evidence.

Tests:
- health report with mock providers.
- benchmark with mock provider.
- eval report generated.
- unavailable provider skipped.
- no-tools eval checks no tools.
- tool-call eval uses mock safe tool.
- no personal data.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- evals/benchmarks added
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-08">>

<<<PROMPT_START id="BRAIN-09" order="9">>
title: Provider fallback and model router
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-08"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Build provider fallback and model router.

Goal:
Allow the agent to select or fall back between brain providers safely based on configuration, provider health, task type, and capability support, without changing safety policy.

Scope:
- Provider selection/fallback logic.
- Config.
- Tests.
- No provider default switch unless explicitly configured.

Non-goals:
- Do not use cloud/paid providers by default.
- Do not run unavailable providers.
- Do not override user-selected provider silently.
- Do not bypass ToolBroker.
- Do not change approval rules.
- Do not call provider during routing unless health is explicitly checked.

Create:
- agent/brain/provider_router.py
- agent/brain/fallback.py
- tests/brain/test_provider_router_fallback.py
- docs/brain/PROVIDER_FALLBACK_POLICY.md
- docs/brain/MODEL_ROUTING_POLICY.md

Config:
- BRAIN_FALLBACK_ENABLED=false by default
- BRAIN_PROVIDER_ORDER=lmstudio,llama_cpp_server,ollama,llama_cpp_inprocess,mlx
- BRAIN_TASK_PROVIDER_MAP={}
- BRAIN_REQUIRE_TOOL_CALL_SUPPORT_FOR_TOOLS=true
- BRAIN_AUTO_SWITCH_ON_FAILURE=false by default
- BRAIN_MAX_FALLBACK_ATTEMPTS=1
- BRAIN_ALLOW_CLOUD_FALLBACK=false

Routing inputs:
- requested provider
- task type
- requires tool calls
- requires streaming
- requires JSON/schema
- provider health
- configured provider order
- user override
- safe mode/no-tools mode

Requirements:
1. Explicit user provider wins unless unavailable and fallback enabled.
2. Fallback disabled by default.
3. Cloud/paid fallback disabled by default.
4. Tool-call tasks require provider tool-call support.
5. No-tools chat can use providers without tool-call support.
6. Provider selection decision recorded/audited/logged.
7. Missing provider returns clear error.
8. Fallback attempts bounded.
9. No model/router decision can alter ToolBroker policy.
10. Tests cover edge cases.

Commands:
- python smart_agent.py brain providers
- python smart_agent.py brain switch <provider> --dry-run
- python smart_agent.py brain fallback-status
- python smart_agent.py brain route "message"

Tests:
- explicit provider selected.
- fallback disabled blocks fallback.
- fallback enabled selects next healthy provider.
- tool-call task rejects provider without tool support.
- no-tools task allows provider without tool support.
- cloud fallback blocked.
- provider decision recorded.
- command registry updated.

Update docs/tracking.

Run tests/validations.

Final report:
- provider router added
- fallback behavior
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-09">>

<<<PROMPT_START id="BRAIN-10" order="10">>
title: Optional MCP interop decision and adapters
category: connector
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-09"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Create MCP interop decision and optional adapter scaffolding.

Goal:
Clarify that MCP is optional interoperability for tools/resources/prompts, not the model runtime. Prepare safe adapter boundaries for future MCP server/client support without allowing MCP to bypass ToolBroker, PolicyEngine, ApprovalManager, or AuditLogger.

Scope:
- Decision record.
- Adapter interface/stubs if safe.
- No MCP server running.
- No external MCP connections.
- Tests for stubs.

Non-goals:
- Do not implement full MCP server.
- Do not connect to external MCP servers.
- Do not expose tools externally.
- Do not bypass ToolBroker.
- Do not allow external clients to execute tools directly.
- Do not add network listener.
- Do not install MCP packages.
- Do not treat MCP as required to replace LM Studio.

Create:
- docs/decisions/mcp_interop_strategy.md
- docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md
- docs/mcp/MCP_ADAPTER_BOUNDARIES.md
- agent/mcp/
  - __init__.py
  - models.py
  - adapter.py
  - server_stub.py
  - client_stub.py
- tests/mcp/test_mcp_adapter_stubs.py

MCP strategy:
1. MCP is optional.
2. MCP does not load the model.
3. MCP does not replace BrainRuntimeGateway.
4. MCP server, if later implemented, exposes only policy-gated tools through ToolBroker.
5. MCP client, if later implemented, consumes external tools only through ToolBroker-like policy wrappers.
6. No external MCP tool can bypass approval/audit.
7. MCP server disabled by default.
8. Network listeners disabled by default.
9. External client access requires pairing/auth and audit.
10. Personal-data tools remain disabled by default.

Commands as planned/stubbed if practical:
- python smart_agent.py mcp status
- python smart_agent.py mcp doctor
- python smart_agent.py mcp server --dry-run
- python smart_agent.py mcp clients

Tests:
- MCP stubs disabled by default.
- MCP server not started.
- external tool call stub requires ToolBroker route.
- personal tools not exposed.
- config defaults safe.
- command registry updated if commands added.

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if commands added
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- CHANGELOG.md

Run tests/validations.

Final report:
- MCP decision created
- stubs added or not
- tests run/results
- next recommended prompt
<<<PROMPT_END id="BRAIN-10">>

<<<PROMPT_START id="BRAIN-11" order="11">>
title: Brain runtime release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-10"]
status: queued

PROMPT:
You are Codex working in this repo.

Task:
Run Brain Runtime Independence release gate and maturity review.

Goal:
Validate that LM Studio has been decoupled behind a provider abstraction, alternate providers are safely scaffolded, model health/evals exist, fallback rules are safe, and MCP is correctly treated as optional interoperability rather than the brain runtime.

Scope:
- Validation.
- Maturity review.
- Small fixes only if needed.
- No new provider implementation beyond pack scope.

Non-goals:
- Do not remove LM Studio.
- Do not change default provider unless explicitly configured and tests support it.
- Do not install model runtimes.
- Do not download models.
- Do not run paid/cloud APIs.
- Do not enable MCP server.
- Do not start network listeners.
- Do not enable personal-data tools.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation if present
6. brain provider tests
7. brain benchmark/eval tests with mocks
8. provider registry status
9. LM Studio provider mocked tests
10. optional live LM Studio doctor only if configured and existing test command supports it

Verify:
- BrainProvider interface exists.
- Model registry exists.
- LM Studio is a provider.
- Existing no-tools chat remains supported.
- Existing tool-call flow remains supported.
- llama.cpp server provider exists/stubbed and disabled by default.
- Ollama provider exists/stubbed and disabled by default.
- llama-cpp-python provider exists/stubbed and disabled by default.
- MLX provider is strategy/stubbed and disabled by default.
- Mock provider supports tests.
- Fallback disabled by default.
- Cloud/paid fallback disabled by default.
- Provider health/evals exist.
- MCP decision docs state MCP is not brain runtime.
- MCP adapters/stubs disabled by default.
- Startup overhead remains low.
- Command registry updated.
- Feature maturity conservative.

Create/update:
- docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md
- docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md

Maturity assessment:
- Brain runtime strategy
- BrainProvider interface
- Model registry
- LM Studio provider refactor
- llama.cpp server provider
- Ollama provider
- llama-cpp-python provider
- MLX provider strategy/stub
- health/benchmark/evals
- provider fallback/router
- MCP decision/adapters
- release gate

Classify each:
- Idea
- Specified
- Scaffolded
- Implemented
- Tested
- Hardened
- Live-Validated
- User-Ready
- Mature Pattern

Update:
- CHANGELOG.md
- README.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- live tests skipped or run
- provider status table
- default provider status
- maturity score
- remaining blockers
- whether LM Studio dependency is now optional or partially optional
- next recommended track
<<<PROMPT_END id="BRAIN-11">>

<<<PROMPT_PACK_END>>>
