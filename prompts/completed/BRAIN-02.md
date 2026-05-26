---
prompt_id: BRAIN-02
pack_id: brain-runtime-independence-v1
title: BrainProvider interface and model registry
category: core
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-01"]
status: completed
order: 2
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T15:40:30+00:00
completed_at: 2026-05-25T15:48:33+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Targeted brain interface/registry tests passed: 13 passed; focused brain/docs/feature-maturity tests passed: 28 passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands; full suite passed: 1220 passed, 1 skipped.
docs_updated: Created docs/brain/BRAIN_PROVIDER_INTERFACE.md and docs/brain/MODEL_REGISTRY.md; updated README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, PROMPT_QUEUE, PROMPT_LEDGER, COMPLETION_REPORT, RISK_REGISTER, and THREAT_MODEL.
changelog_updated:
feature_registry_updated:
feature_maturity_updated:
command_registry_updated:
completion_report_updated:
evidence_links:
blockers:
next_prompt_id:
supersedes:
superseded_by:
notes: Completed BRAIN-02 interface/registry scaffold. LM Studio remains current runtime path; no provider migration, llama.cpp/Ollama/MLX implementation, model/runtime install, model download, paid/cloud default, MCP enablement, network listener, tool semantic change, memory write, or safety-control bypass.
---

# Prompt

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
