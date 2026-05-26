---
prompt_id: DAYDREAM-04
pack_id: daydream-lab-idle-research-v1
title: Interest map and topic profile system
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-03"]
status: queued
order: 4
created_at: 2026-05-26T07:54:41+00:00
imported_at: 2026-05-26T07:54:41+00:00
source_pack: prompts/packs/daydream-lab-idle-research-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at:
completed_at:
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result:
docs_updated:
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
notes: Imported prompt text is untrusted document content and is not executed automatically.
---

# Prompt

Build interest map and topic profile system.

Create:
- agent/daydream/interests.py
- tests/daydream/test_interest_map.py
- docs/daydream/INTEREST_MAP.md
- docs/daydream/USER_INTEREST_CONTROL_PANEL.md

Interest sources:
- explicit user-added interests
- repo/project topics
- approved memory kernel topics if available
- previous daydream accepted ideas
- current feature roadmap
- user profile only if already available and non-sensitive
- no sensitive inference

Default interest examples may be docs/static only:
- AI agents
- local LLMs
- Hugging Face / model releases
- real estate
- vlogging/content trends
- food reviews/restaurants
- healthcare/NEMT/ambulance business
- sober living/IOP
- sports/content ideas
- creative media generation
- Apple/iOS/macOS changes
- Plex/media server tools
- CRISPR fruit concepts

Commands:
- daydream interests
- daydream interests add "<topic>"
- daydream interests mute "<topic>"
- daydream interests boost "<topic>"
- daydream interests why "<topic>"
- daydream interests reset --dry-run

Rules:
- Do not write persistent user memory unless explicit future approval.
- Store interest map as local config/report metadata only if existing policy allows.
- Explain why each topic is included.
