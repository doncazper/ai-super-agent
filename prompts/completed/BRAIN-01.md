---
prompt_id: BRAIN-01
pack_id: brain-runtime-independence-v1
title: Brain runtime architecture and LM Studio decoupling
category: core
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T15:33:04+00:00
completed_at: 2026-05-25T15:40:22+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused BRAIN docs/command registry tests passed: 7 passed; docs/registry tracker tests passed: 20 passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands; full suite passed: 1207 passed, 1 skipped.
docs_updated: Created brain runtime architecture docs and updated README, CHANGELOG, PROJECT_STATE, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, COMPLETION_REPORT, RISK_REGISTER, THREAT_MODEL, TRACKER_DASHBOARD.
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
notes: Completed docs-only BRAIN-01. LM Studio remains current provider; no runtime behavior changed, no provider implementation, no installs/downloads, no paid/cloud default, no MCP enablement, no network listener, no startup-heavy import, and no safety-control bypass.
---

# Prompt

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
