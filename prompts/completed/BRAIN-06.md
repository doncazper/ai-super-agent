---
prompt_id: BRAIN-06
pack_id: brain-runtime-independence-v1
title: llama-cpp-python in-process provider
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-05"]
status: completed
order: 6
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T16:33:00+00:00
completed_at: 2026-05-25T16:42:30+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused llama-cpp-python/model-registry tests passed with 17 passed; broader brain/docs/feature-maturity/command-registry tests passed with 66 passed; brain providers, brain health --provider llama_cpp_inprocess, and brain doctor --provider llama_cpp_inprocess CLI smokes passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands.
docs_updated: Created docs/brain/providers/llama_cpp_inprocess.md; updated README, .env.example, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, PROMPT_QUEUE, PROMPT_LEDGER, PROMPT_AUDIT, COMPLETION_REPORT, RISK_REGISTER, THREAT_MODEL, brain provider docs, model registry docs, provider strategy docs, and brain runtime decision docs.
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
notes: Completed BRAIN-06 llama-cpp-python in-process provider scaffold. LM Studio remains default; in-process provider is disabled unless explicitly enabled/configured; no package install, model download, model load on startup/health, default-provider change, cloud API call, MCP enablement, listener startup, memory write, unverified tool-call support, ToolBroker semantic change, or safety-control bypass.
---

# Prompt

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
