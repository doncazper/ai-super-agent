---
prompt_id: BRAIN-03
pack_id: brain-runtime-independence-v1
title: LM Studio provider refactor
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["BRAIN-02"]
status: completed
order: 3
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T15:48:41+00:00
completed_at: 2026-05-25T15:57:28+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused brain/LM Studio compatibility tests passed: 37 passed; broader brain/docs/command-registry tests passed: 55 passed; brain providers/status/doctor CLI smokes passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands; full suite passed: 1228 passed, 1 skipped.
docs_updated: Updated docs/brain/LM_STUDIO_DECOUPLING_PLAN.md, docs/brain/BRAIN_PROVIDER_INTERFACE.md, docs/brain/MODEL_REGISTRY.md, README, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, PROMPT_QUEUE, PROMPT_LEDGER, COMPLETION_REPORT, RISK_REGISTER, and THREAT_MODEL.
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
notes: Completed BRAIN-03 LM Studio provider refactor. LMStudioClient remains available; LM Studio remains default; no non-LM provider, model/runtime install, model download, paid/cloud default, MCP enablement, listener startup, memory write, no-tools regression, ToolBroker semantic change, or safety-control bypass.
---

# Prompt

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
