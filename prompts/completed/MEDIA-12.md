---
prompt_id: MEDIA-12
pack_id: creative-media-generation-v1
title: Creative media release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["MEDIA-11"]
status: completed
order: 12
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T23:46:39+00:00
completed_at: 2026-05-25T23:55:15+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Full suite passed: 1580 passed. Focused media release suite passed: 77 passed. Dogfood metadata checks passed for media_core, media_safety, media_image_planning, and media_video_audio_planning. eval run --media passed: 6 pass, 0 fail, 5 personal-data skips. commands validate passed with 529 commands. make policy-check passed startup policy and capability manifest validation. Dedicated deterministic docs validation is not available; docs evidence came from docs-focused tests and full suite.
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
notes: Completed Creative Media release gate and conservative maturity review. Added release-gate and maturity-review docs and kept maturity at local 4 Tested/readiness 77. No real generation/editing, provider call, model install/download, paid API, upload/publish, voice cloning, real-person likeness workflow, personal-data access, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Run Creative Media Generation release gate and maturity review.

Goal:
Validate that creative media generation groundwork is safe, provider-based, documented, tested, and ready for future provider implementation without adding unsafe media generation.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. media unit tests
7. media dogfood/eval suite with fixtures
8. media safety checks
9. asset manager bounds tests

Verify:
- media roadmap exists
- provider registry exists
- asset manager bounds outputs
- safety checker exists
- license policy exists
- consent policy exists
- ComfyUI stub disabled by default
- image/video/audio/music/TTS generation are dry-run/stubbed unless configured
- no real model downloads
- no paid API calls by default
- no auto-upload/publishing
- voice cloning denied/deferred
- real-person likeness consent-gated
- command registry updated
- feature maturity conservative

Create/update:
- docs/media/CREATIVE_MEDIA_RELEASE_GATE.md
- docs/media/CREATIVE_MEDIA_MATURITY_REVIEW.md

Maturity assessment:
- Creative media roadmap
- Provider registry
- Asset manager
- Safety/license/consent policy
- ComfyUI provider stub
- Image generation scaffolding
- Thumbnail/social workflows
- Video generation scaffolding
- Audio/music scaffolding
- TTS/voice strategy
- NL routing/commands
- Dogfood/evals
- Release gate

Update:
- CHANGELOG.md
- README.md if needed
- docs/USER_GUIDE.md if present
- docs/HELP.md if present
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
- dogfood/eval results
- maturity score
- remaining blockers
- whether creative media groundwork is safe to rely on
- next recommended feature track
