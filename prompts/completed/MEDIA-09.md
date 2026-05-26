---
prompt_id: MEDIA-09
pack_id: creative-media-generation-v1
title: TTS and voice generation strategy
category: media
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-08"]
status: completed
order: 9
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T23:13:19+00:00
completed_at: 2026-05-25T23:21:32+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: Focused media/docs/command registry tests passed: 71 passed. CLI smokes passed for media tts plan, media voice consent-policy, and media voice providers. commands validate passed with 522 commands. make policy-check passed startup policy and capability manifest validation.
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
notes: Added TTS/voice category planning, voice consent policy metadata, TTS/voice provider stubs, brokered commands, manifest entries, command tracking, and conservative docs. No real voice generation, voice cloning, public/private person voice imitation, personal voice sample use, upload/publish, model install/download, provider API, consent record storage, commit, or push.
---

# Prompt

You are Codex working in this repo.

Task:
Build TTS and voice generation strategy.

Goal:
Prepare a safe path for future TTS and voice generation while explicitly separating ordinary TTS from voice cloning/impersonation.

Scope:
- Docs.
- Stub models/providers.
- Safety gates.
- Tests.

Non-goals:
- Do not implement voice cloning.
- Do not generate real voice audio.
- Do not imitate real people.
- Do not use personal voice samples.
- Do not upload/publish.

Create:
- agent/media/tts.py
- tests/media/test_tts_strategy.py
- docs/media/TTS_VOICE_GENERATION_STRATEGY.md
- docs/media/VOICE_CONSENT_POLICY.md

Voice categories:
- generic_tts
- character_voice
- user_owned_voice_with_consent
- public_figure_voice
- private_person_voice
- voice_clone
- impersonation

Rules:
1. Generic TTS can be future MEDIUM risk.
2. Voice cloning is CRITICAL or FORBIDDEN until consent system exists.
3. Public/private person voice imitation denied/deferred.
4. Consent records required before any future user-owned voice cloning.
5. Voice outputs require watermark/provenance strategy if implemented later.
6. No real generation in this prompt.

Commands as planned/stubbed:
- python smart_agent.py media tts plan "text"
- python smart_agent.py media voice consent-policy
- python smart_agent.py media voice providers

Tests:
- generic TTS plan allowed/stubbed.
- public figure voice denied.
- private person voice denied.
- user-owned voice requires consent.
- command registry updated.

Update docs/tracking.

Final report:
- TTS strategy added
- tests run/results
- next recommended prompt
