---
prompt_id: BRAIN-07
pack_id: brain-runtime-independence-v1
title: MLX provider strategy/stub
category: core
risk_level: LOW
approval_gate: false
depends_on: ["BRAIN-06"]
status: completed
order: 7
created_at: 2026-05-25T15:32:48+00:00
imported_at: 2026-05-25T15:32:48+00:00
source_pack: prompts/packs/brain-runtime-independence-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T16:42:56+00:00
completed_at: 2026-05-25T16:51:40+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused MLX/model-registry tests passed with 15 passed; broader brain/docs/feature-maturity/command-registry tests passed with 73 passed; brain providers, brain health --provider mlx, and brain doctor --provider mlx CLI smokes passed; startup policy and capability manifest validation passed via make policy-check; command registry validation passed with 437 commands.
docs_updated: Created docs/brain/providers/mlx.md and docs/decisions/mlx_provider_strategy.md; updated README, .env.example, CHANGELOG, PROJECT_STATE, TRACKER_DASHBOARD, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, PROMPT_QUEUE, PROMPT_LEDGER, PROMPT_AUDIT, COMPLETION_REPORT, RISK_REGISTER, THREAT_MODEL, brain provider docs, model registry docs, provider strategy docs, and brain runtime decision docs.
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
notes: Completed BRAIN-07 MLX provider strategy/stub. LM Studio remains default; MLX is disabled and non-generating unless a future approved implementation lands; no MLX install, model download, native startup import, model load, server start, text generation, default-provider change, cloud API call, MCP enablement, listener startup, memory write, unverified tool-call support, ToolBroker semantic change, or safety-control bypass.
---

# Prompt

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
