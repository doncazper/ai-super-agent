---
prompt_id: MEDIA-10
pack_id: creative-media-generation-v1
title: Media workflow commands and natural-language routing
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-09"]
status: completed
order: 10
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T23:21:46+00:00
completed_at: 2026-05-25T23:32:08+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/NL/docs/command registry tests passed: 105 passed. CLI smokes passed for media plan, unsafe media plan, and nl thumbnail request. commands validate passed with 523 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added brokered media plan dry-run planner, media workflow target inference, deterministic safety preflight before target planning, natural-language media.plan routing metadata, capability manifest entry, command registry/test matrix rows, README/User Guide/docs, and conservative tracker updates. No real media generation/editing, provider call, upload/publish, unsafe prompt execution, personal-media read, model install/download, paid API, automatic NL execution, safety-control bypass, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build media workflow commands and natural-language routing hooks.

Goal:
Make media generation discoverable and routable from natural-language requests without executing generation unsafely.

Scope:
- CLI command stubs/planners.
- NL routing hooks if natural-language system exists.
- Command registry.
- Tests.

Non-goals:
- Do not generate real media.
- Do not call providers.
- Do not upload/post.
- Do not execute unsafe prompts.

Commands:
- python smart_agent.py media plan "request"
- python smart_agent.py media providers
- python smart_agent.py media doctor
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media assets list
- python smart_agent.py media generate image "prompt" --dry-run
- python smart_agent.py media generate video "prompt" --dry-run
- python smart_agent.py media generate audio "prompt" --dry-run
- python smart_agent.py media generate music "prompt" --dry-run
- python smart_agent.py media thumbnail "prompt" --dry-run

Natural-language examples:
- make me a thumbnail for this vlog
- create a 10-second intro animation
- make a lo-fi music bed for a food review
- generate sound effects for my video
- turn this image into a short video
- make a podcast cover
- create a real estate listing graphic

Requirements:
1. Dry-run/planning first.
2. Safety preflight before all generation planning.
3. Real generation blocked until provider configured.
4. NL routing creates plan/preflight, not automatic generation.
5. Command registry updated.
6. User guide/help updated if present.
7. Tests cover routing if system exists.

Tests:
- media plan command works.
- image/video/audio/music dry-run works.
- unsafe prompt denied.
- missing provider setup hint.
- NL route maps thumbnail request if NL system exists.
- command registry updated.

Update docs/tracking.

Final report:
- commands added
- NL routing hooks
- tests run/results
- next recommended prompt
