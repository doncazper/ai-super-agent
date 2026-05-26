---
prompt_id: MEDIA-03
pack_id: creative-media-generation-v1
title: Media prompt/output safety, copyright, consent, and license policy
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["MEDIA-02"]
status: completed
order: 3
created_at: 2026-05-25T22:15:16+00:00
imported_at: 2026-05-25T22:15:16+00:00
source_pack: prompts/packs/creative-media-generation-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T22:31:32+00:00
completed_at: 2026-05-25T22:37:49+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: focused media safety/provider/asset/docs/command registry tests passed 27; CLI smokes for safety/license/consent passed; command registry validation ok with 522 commands; make policy-check passed startup policy and capability manifest validation
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
notes: Implemented deterministic local media prompt safety checker, provider license report, consent policy, brokered media safety/license/consent commands, docs, manifest entries, and trackers. No generation/providers/external moderation/voice/likeness/personal-data access.
---

# Prompt

You are Codex working in this repo.

Task:
Build media prompt/output safety, copyright, consent, and license policy.

Goal:
Before generation providers are added, define and implement a safety preflight that classifies media prompts, identifies policy/consent/license risks, and blocks/flags unsafe requests.

Scope:
- Safety docs.
- Prompt safety checker.
- License metadata model.
- Tests.
- No generation.

Non-goals:
- Do not implement media generation.
- Do not call external moderation APIs.
- Do not build voice cloning.
- Do not create real-person impersonation workflows.
- Do not provide legal advice; provide operational risk flags.

Create:
- agent/media/safety.py
- agent/media/licenses.py
- tests/media/test_media_safety_license.py
- docs/media/MEDIA_PROMPT_SAFETY.md
- docs/media/MEDIA_COPYRIGHT_AND_LICENSE_POLICY.md
- docs/media/MEDIA_CONSENT_POLICY.md

Safety categories:
- safe_general
- commercial_use_unclear
- copyrighted_character_or_brand
- living_person_likeness
- private_person_likeness
- celebrity_likeness
- voice_clone
- impersonation
- sexual_content
- graphic_violence
- extremist_or_hate
- illegal_instructional_content
- medical/legal/financial claim risk
- political persuasion risk
- privacy_sensitive_input
- unknown_risk

Safety outcomes:
- allow
- warn
- require_license_review
- require_consent
- require_human_review
- deny

Requirements:
1. Prompt safety runs before generation.
2. License review required for provider/model commercial-use uncertainty.
3. Voice cloning requires explicit consent workflow; otherwise denied/deferred.
4. Real-person likeness requires consent/human review.
5. Unsafe categories denied.
6. Output metadata includes safety outcome.
7. Safety checker is deterministic first; model-based later optional.
8. No external calls.
9. Tests cover categories.
10. Command registry updated if command added.

Commands:
- python smart_agent.py media safety-check "prompt"
- python smart_agent.py media license report
- python smart_agent.py media consent policy

Tests:
- safe prompt allowed.
- celebrity/voice clone flagged.
- copyrighted character flagged.
- unsafe content denied.
- commercial uncertainty warns.
- consent required for real-person likeness.
- license info attached to mock provider.
- command registry updated.

Update docs/tracking.

Final report:
- safety checker added
- license policy added
- tests run/results
- next recommended prompt
