---
prompt_id: MEDIA-06
pack_id: creative-media-generation-v1
title: Image editing, thumbnail, and social creative workflows
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-05"]
status: completed
order: 6
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:51:10+00:00
completed_at: 2026-05-25T22:57:56+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/docs/command registry tests passed: 49 passed. CLI smokes passed for media creative templates, media creative plan, and media thumbnail --dry-run. commands validate passed with 522 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added thumbnail/social creative workflow templates, dry-run creative planning, mock workflow asset metadata helper, brokered commands, manifest entries, command tracking, and conservative docs. No real image editing/generation, personal-image input, upload/publish, model install/download, provider API, voice cloning, real-person likeness workflow, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build image editing, thumbnail, and social creative workflow scaffolding.

Goal:
Support future use cases such as YouTube thumbnails, real estate marketing graphics, vlog title cards, podcast covers, and social media images.

Scope:
- Workflow definitions.
- Dry-run planning.
- Mock outputs.
- Docs/tests.
- No real image editing yet.

Non-goals:
- Do not edit real user images by default.
- Do not generate real media.
- Do not upload/post.
- Do not create real-person likeness edits without future consent policy.

Create:
- agent/media/creative_workflows.py
- tests/media/test_creative_workflows.py
- docs/media/THUMBNAIL_SOCIAL_CREATIVE_WORKFLOWS.md

Workflow types:
- youtube_thumbnail
- short_form_video_cover
- podcast_cover
- real_estate_listing_graphic
- food_review_thumbnail
- family_vlog_title_card
- social_post_image
- ad_creative
- before_after_layout
- product_mockup

Commands:
- python smart_agent.py media thumbnail "prompt" --dry-run
- python smart_agent.py media creative plan "prompt"
- python smart_agent.py media creative templates

Requirements:
1. Workflow planning only by default.
2. Safety preflight runs.
3. Output size/aspect ratio suggestions.
4. Prompt templates stored as docs/config, not model secrets.
5. Asset manager integration.
6. No upload/publish.
7. Command registry updated.

Tests:
- thumbnail plan generated.
- social creative templates listed.
- unsafe prompt denied.
- commercial/license caution included where relevant.
- mock asset metadata created.
- command registry updated.

Update docs/tracking.

Final report:
- creative workflows scaffolded
- tests run/results
- next recommended prompt
