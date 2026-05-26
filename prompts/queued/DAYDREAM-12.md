---
prompt_id: DAYDREAM-12
pack_id: daydream-lab-idle-research-v1
title: Idea ranking, scoring, novelty, and boredom detection
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-11"]
status: queued
order: 12
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

Build idea ranking, scoring, novelty, and boredom detection.

Create:
- agent/daydream/scoring.py
- agent/daydream/novelty.py
- agent/daydream/boredom.py
- tests/daydream/test_scoring_novelty_boredom.py
- docs/daydream/IDEA_RANKING_SCORING.md
- docs/daydream/NOVELTY_AND_BOREDOM_DETECTION.md

Score:
- usefulness_to_sam
- usefulness_to_agent
- implementation_difficulty
- safety_risk
- maintenance_burden
- dependency_burden
- cost
- privacy_risk
- cool_factor
- business_upside
- compound_value
- architecture_fit
- source_quality
- novelty

Boredom/saturation:
- repeated idea
- repeated source
- topic over-mined
- no new signal
- low novelty
- archive/reduce-frequency recommendation

Commands:
- daydream ideas --ranked
- daydream score <idea_id>
- daydream novelty <idea_id>
- daydream boredom-report
