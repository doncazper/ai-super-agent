---
prompt_id: MEDIA-08
pack_id: creative-media-generation-v1
title: Audio, music, and sound generation strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-07"]
status: completed
order: 8
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T23:04:41+00:00
completed_at: 2026-05-25T23:13:11+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/docs/command registry tests passed: 65 passed. CLI smokes passed for media audio providers, media music plan, media generate audio --dry-run, and media generate music --dry-run. commands validate passed with 522 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added audio/music provider candidate metadata, dry-run audio/music planning, voice-clone denial, artist/track imitation flags, mock audio-provider metadata scaffolding, brokered commands, manifest entries, command tracking, and conservative docs. No real audio/music generation, model install/download, provider SDK import, paid API, upload/publish, voice cloning, TTS runtime, commercial copyrighted-song/artist imitation workflow, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build audio, music, and sound generation strategy and scaffolding.

Goal:
Prepare for text-to-sound, text-to-music, short music beds, podcast intros, sound effects, and video backing tracks using local/free providers where possible.

Scope:
- Audio/music provider strategy.
- Mock audio provider.
- Request/result models if needed.
- Tests/docs.

Non-goals:
- Do not install audio/music models.
- Do not download models.
- Do not generate real audio.
- Do not clone voices.
- Do not generate copyrighted song/artist imitations as commercial output.
- Do not upload/publish.

Create:
- agent/media/providers/mock_audio.py
- agent/media/audio_generation.py
- tests/media/test_audio_generation_scaffolding.py
- docs/media/AUDIO_MUSIC_GENERATION_STRATEGY.md
- docs/media/providers/AUDIO_PROVIDER_CANDIDATES.md

Candidate providers/models:
- AudioCraft / MusicGen / AudioGen
- Stable Audio Open
- Stable Audio Open Small
- ACE-Step
- ComfyUI audio workflows
- TTS providers, future only

Commands:
- python smart_agent.py media generate audio "prompt" --dry-run
- python smart_agent.py media generate music "prompt" --dry-run
- python smart_agent.py media audio providers
- python smart_agent.py media music plan "prompt"

Requirements:
1. Dry-run by default.
2. Safety preflight required.
3. Voice cloning denied/deferred unless consent system exists.
4. Artist/track imitation flagged.
5. License/commercial-use warnings included.
6. Mock audio metadata for tests.
7. No real generation.
8. Command registry updated.

Tests:
- music plan generated.
- sound effect plan generated.
- voice clone request denied/deferred.
- artist imitation flagged.
- mock audio metadata created.
- command registry updated.

Update docs/tracking.

Final report:
- audio/music scaffolding added
- tests run/results
- next recommended prompt
