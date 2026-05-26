---
prompt_id: MEDIA-07
pack_id: creative-media-generation-v1
title: Video generation provider strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-06"]
status: completed
order: 7
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:58:05+00:00
completed_at: 2026-05-25T23:04:29+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/docs/command registry tests passed: 57 passed. CLI smokes passed for media video providers, media video plan, and media generate video --dry-run. commands validate passed with 522 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added video provider candidate metadata, dry-run video planning, resource warnings, mock video-provider metadata scaffolding, brokered commands, manifest entries, command tracking, and conservative docs. No real video generation, model install/download, provider SDK import, paid API, source-image/source-video input, upload/publish, voice cloning, real-person likeness workflow, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build video generation provider strategy and scaffolding.

Goal:
Prepare for text-to-video and image-to-video generation using local/free providers where possible, while keeping actual generation disabled until providers/models are configured and tested.

Scope:
- Video provider strategy.
- Mock video provider.
- Request/result models if needed.
- Tests/docs.

Non-goals:
- Do not download video models.
- Do not install video generation dependencies.
- Do not generate real videos.
- Do not upload/post videos.
- Do not generate real-person likeness videos without future consent workflow.

Create:
- agent/media/providers/mock_video.py
- agent/media/video_generation.py
- tests/media/test_video_generation_scaffolding.py
- docs/media/VIDEO_GENERATION_STRATEGY.md
- docs/media/providers/VIDEO_PROVIDER_CANDIDATES.md

Candidate models/providers to document:
- ComfyUI video workflows
- Wan
- LTX-Video
- HunyuanVideo
- Stable Video Diffusion
- image-to-video workflows
- text-to-video workflows

Commands:
- python smart_agent.py media generate video "prompt" --dry-run
- python smart_agent.py media video providers
- python smart_agent.py media video plan "prompt"

Requirements:
1. Dry-run by default.
2. Safety preflight required.
3. Hardware/resource requirements documented.
4. Provider license tracked.
5. Mock video result for tests.
6. No real generation until configured.
7. No upload/publish.
8. Command registry updated.

Tests:
- dry-run plan generated.
- resource warning included.
- unsafe prompt denied.
- mock video metadata created.
- unconfigured provider setup hint.
- command registry updated.

Update docs/tracking.

Final report:
- video generation scaffolding added
- tests run/results
- next recommended prompt
