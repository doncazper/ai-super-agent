---
prompt_id: DAYDREAM-07
pack_id: daydream-lab-idle-research-v1
title: Idea card, research brief, and dream provenance models
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-06"]
status: queued
order: 7
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

Build idea card, research brief, and dream provenance models.

Create:
- agent/daydream/idea_models.py
- agent/daydream/provenance.py
- tests/daydream/test_idea_models_provenance.py
- docs/daydream/IDEA_CARDS.md
- docs/daydream/RESEARCH_BRIEFS.md
- docs/daydream/DREAM_PROVENANCE.md

Idea lifecycle states:
- raw_idea
- researched
- ranked
- needs_more_research
- blocked
- unsafe_or_not_allowed
- not_worth_it
- worth_later
- worth_building
- prompt_pack_candidate
- promoted_to_prompt_pack
- accepted
- rejected
- archived

Idea fields:
- idea_id
- title
- summary
- category
- source/provenance
- user_interest_match
- agent_improvement_match
- novelty
- usefulness_to_sam
- usefulness_to_agent
- compound_value
- business_upside
- cool_factor
- difficulty
- safety_risk
- privacy_risk
- dependency_burden
- maintenance_burden
- cost
- status
- sources
- limitations
- ask_sam_questions
- next_action

Provenance:
- user_interest
- repo_gap
- source_article
- GitHub repo
- Hugging Face model
- competitor feature
- bug pattern
- performance bottleneck
- random exploration
- prior rejected idea

Commands:
- daydream ideas
- daydream ideas show <idea_id>
- daydream briefs
- daydream provenance <idea_id>
