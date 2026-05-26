---
prompt_id: MEDIA-11
pack_id: creative-media-generation-v1
title: Media dogfood and eval suite
category: tests
risk_level: LOW
approval_gate: false
depends_on: ["MEDIA-10"]
status: completed
order: 11
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T23:35:13+00:00
completed_at: 2026-05-25T23:46:29+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/dogfood/eval/docs/command-registry tests passed: 109 passed. CLI smokes passed for dogfood show media_core, eval run --media, and eval report --media. commands validate passed with 529 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added mock/fixture-first creative media dogfood suites, media eval cases, eval --media/report --media CLI support, command registry/test matrix rows, media dogfood runbook, and conservative tracker updates. No real generation/editing, provider call, model install/download, paid API, upload/publish, personal-data access, voice cloning, real-person likeness workflow, safety-control bypass, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build Creative Media dogfood and eval suite.

Goal:
Create tests and dogfood commands to validate media planning, provider status, asset management, safety checks, license warnings, and dry-run workflows.

Create:
- dogfood_suites/media_core.yaml
- dogfood_suites/media_safety.yaml
- dogfood_suites/media_image_planning.yaml
- dogfood_suites/media_video_audio_planning.yaml
- eval_cases/media/
- docs/media/MEDIA_DOGFOOD_RUNBOOK.md

Dogfood:
- media providers
- media doctor
- media assets list
- media safety-check safe prompt
- media safety-check unsafe prompt
- image dry-run
- video dry-run
- audio dry-run
- music dry-run
- thumbnail dry-run
- missing provider setup hint
- license warning fixture

Eval checks:
- no real generation
- no paid APIs
- no model downloads
- unsafe prompts denied
- voice clone denied/deferred
- license uncertainty warned
- assets bounded to workspace
- command registry complete

Commands:
- python smart_agent.py dogfood run media_core --session
- python smart_agent.py dogfood run media_safety --session
- python smart_agent.py eval run --media
- python smart_agent.py eval report --media

Tests:
- dogfood YAML validates.
- eval fixtures load.
- media safety tests pass.
- no real media generated.
- command registry updated.

Update docs/tracking.

Final report:
- dogfood/eval suites added
- tests run/results
- next recommended prompt
