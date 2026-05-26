---
prompt_id: MEDIA-05
pack_id: creative-media-generation-v1
title: Image generation provider track
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-04"]
status: completed
order: 5
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:43:49+00:00
completed_at: 2026-05-25T22:51:00+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/docs/command registry tests passed: 43 passed. CLI smokes passed for media image providers, media image plan, and media generate image --dry-run. commands validate passed with 522 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added image-generation dry-run planner, mock image-provider metadata scaffolding, provider candidate docs, brokered dry-run commands, manifest entries, command tracking, and conservative tracker updates. No real image generation, model install/download, provider SDK import, paid API, asset write from CLI generation, personal-photo input, upload/publish, voice cloning, real-person likeness workflow, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build image generation provider track scaffolding.

Goal:
Prepare image generation workflows using free/local/open providers while keeping generation disabled/stubbed until providers/models are configured and safe.

Scope:
- Image request/result models if not already present.
- Mock image provider.
- Provider strategy docs.
- Tests.
- No actual image generation.

Non-goals:
- Do not download models.
- Do not install diffusion libraries.
- Do not call paid APIs.
- Do not generate real images.
- Do not use personal photos without explicit future consent flow.

Create:
- agent/media/providers/mock_image.py
- agent/media/image_generation.py
- tests/media/test_image_generation_scaffolding.py
- docs/media/IMAGE_GENERATION_STRATEGY.md
- docs/media/providers/IMAGE_PROVIDER_CANDIDATES.md

Candidate providers/models to document:
- ComfyUI workflows
- Diffusers local provider
- SDXL
- FLUX.1-schnell / FLUX.1-dev
- Stable Diffusion 3.x
- Qwen-Image
- ControlNet/LoRA workflows, future

Commands:
- python smart_agent.py media generate image "prompt" --dry-run
- python smart_agent.py media image providers
- python smart_agent.py media image plan "prompt"

Requirements:
1. Dry-run by default for unconfigured providers.
2. Safety preflight required.
3. License info required for provider/model before commercial-use claims.
4. Mock provider can create fake metadata/result for tests.
5. Real provider unavailable returns setup hint.
6. Output asset manager used for any generated/fake outputs.
7. No personal image editing yet.
8. Command registry updated.

Tests:
- dry-run plan generated.
- unsafe prompt blocked.
- license uncertainty warning.
- mock image result metadata created.
- unconfigured provider setup hint.
- asset manager integration.
- command registry updated.

Update docs/tracking.

Final report:
- image generation scaffolding added
- tests run/results
- next recommended prompt
