---
prompt_id: MEDIA-04
pack_id: creative-media-generation-v1
title: ComfyUI provider strategy and stub
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-03"]
status: completed
order: 4
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:37:56+00:00
completed_at: 2026-05-25T22:43:44+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused media/ComfyUI/docs/command registry tests passed 35; CLI smokes for ComfyUI doctor and workflows list passed; command registry validation ok with 522 commands; make policy-check passed startup policy and capability manifest validation
docs_updated: yes
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
notes: Implemented disabled-by-default ComfyUI provider config/status/doctor/workflow-list stub, safe env defaults, docs, manifest entries, and tests. No install/server start/model download/workflow submission/custom nodes/generation.
---

# Prompt

You are Codex working in this repo.

Task:
Build ComfyUI provider strategy and stub.

Goal:
Prepare ComfyUI as the primary local workflow engine candidate for image/video/audio diffusion workflows without requiring installation or model downloads yet.

Scope:
- Provider stub.
- Config.
- Doctor/status.
- Mocked tests.
- Docs.

Non-goals:
- Do not install ComfyUI.
- Do not start ComfyUI server.
- Do not download models.
- Do not run workflows.
- Do not generate media yet.

Create:
- agent/media/providers/
  - __init__.py
  - comfyui.py
- tests/media/test_comfyui_provider_stub.py
- docs/media/providers/COMFYUI_PROVIDER.md
- docs/decisions/comfyui_provider_strategy.md

Config:
- COMFYUI_ENABLED=false
- COMFYUI_BASE_URL=http://127.0.0.1:8188
- COMFYUI_TIMEOUT_SECONDS=120
- COMFYUI_OUTPUT_DIR=
- COMFYUI_ALLOW_WORKFLOW_SUBMIT=false by default
- COMFYUI_ALLOW_CUSTOM_NODES=false by default unless reviewed
- COMFYUI_REQUIRE_SAFETY_PREFLIGHT=true

Provider status:
- disabled
- not_configured
- server_unreachable
- reachable
- workflow_submit_disabled
- ready_mock_only
- ready

Commands:
- python smart_agent.py media comfyui doctor
- python smart_agent.py media providers
- python smart_agent.py media workflows list --provider comfyui

Requirements:
1. Disabled by default.
2. No generation submissions by default.
3. Health check does not submit workflow.
4. Custom nodes treated as supply-chain risk.
5. Workflow JSON treated as UNTRUSTED_DOCUMENT unless vetted.
6. Provider errors normalized.
7. Mock tests only.
8. Command registry updated.

Tests:
- provider disabled by default.
- missing config setup hint.
- mock server reachable.
- workflow submit denied by default.
- custom nodes warning.
- provider registry lists comfyui.
- command registry updated.

Update docs/tracking.

Final report:
- ComfyUI stub added
- tests run/results
- next recommended prompt
