---
prompt_id: MEDIA-01
pack_id: creative-media-generation-v1
title: Creative media roadmap and risk model
category: media
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:15:21+00:00
completed_at: 2026-05-25T22:21:07+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: creative media docs tests 3 passed; command registry validation ok with 522 commands; startup policy and capability manifest validation passed via make policy-check
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
notes: Completed docs-only creative media roadmap/risk model milestone. Created docs/media track docs and ADR, planned command registry/test matrix rows, feature/risk/threat/tracker updates. No runtime media generation or provider behavior added.
---

# Prompt

You are Codex working in this repo.

Task:
Create Creative Media Generation roadmap and risk model.

Goal:
Define a safe, provider-based architecture for image, video, sound, music, TTS, thumbnails, social creatives, and future creative media workflows.

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

Follow the mini-SDLC.

Scope:
- Documentation and roadmap.
- No model/provider runtime implementation yet.
- No media generation yet.

Non-goals:
- Do not install ComfyUI or model dependencies.
- Do not download models.
- Do not call paid APIs.
- Do not generate media yet.
- Do not enable social publishing.
- Do not implement voice cloning.
- Do not implement real-person likeness workflows.

Create:
- docs/media/CREATIVE_MEDIA_GENERATION_TRACK.md
- docs/media/MEDIA_PROVIDER_STRATEGY.md
- docs/media/MEDIA_RISK_MODEL.md
- docs/media/MEDIA_LICENSE_POLICY.md
- docs/media/MEDIA_ASSET_POLICY.md
- docs/media/MEDIA_SAFETY_POLICY.md
- docs/decisions/creative_media_generation_architecture.md

Define provider categories:
- image_generation
- image_editing
- image_to_video
- text_to_video
- audio_generation
- music_generation
- tts
- voice_generation
- video_editing
- thumbnail/social_creative
- mock/test

Define candidate providers:
- ComfyUI
- Diffusers
- Stable Diffusion / SDXL
- FLUX
- Stable Diffusion 3.x
- Qwen-Image
- Wan / LTX / HunyuanVideo / Stable Video Diffusion
- AudioCraft / MusicGen / AudioGen
- Stable Audio Open
- ACE-Step
- TTS providers, future only
- Cloud providers, optional and disabled by default
- mock provider for tests

Define risk levels:
- media provider status: SAFE
- prompt planning: LOW
- local image generation: MEDIUM
- image editing with user images: MEDIUM/HIGH depending personal likeness
- video generation: MEDIUM/HIGH due cost/resources/content risk
- audio/music generation: MEDIUM
- voice cloning: CRITICAL or FORBIDDEN unless explicit consent workflow exists
- social posting/uploading: CRITICAL
- paid API generation: approval/config-gated
- real-person likeness generation: approval/policy-gated
- copyrighted/style imitation risk: review/caveat-gated
- unsafe/NSFW/extremist/abusive media: FORBIDDEN unless a future policy explicitly allows narrow safe cases

Planned commands to add to COMMAND_REGISTRY as planned/stubbed:
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media assets list
- python smart_agent.py media generate image "prompt"
- python smart_agent.py media generate video "prompt"
- python smart_agent.py media generate audio "prompt"
- python smart_agent.py media generate music "prompt"
- python smart_agent.py media thumbnail "prompt"
- python smart_agent.py media workflow list
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media license report
- python smart_agent.py media dogfood

Update:
- docs/FEATURE_ROADMAP.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if present
- docs/PROJECT_STATE.md
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- CHANGELOG.md

Run docs validation/tests if available.

Final report:
- docs created
- planned commands
- risks added
- tests/validations run
- next recommended prompt
