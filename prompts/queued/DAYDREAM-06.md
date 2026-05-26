---
prompt_id: DAYDREAM-06
pack_id: daydream-lab-idle-research-v1
title: Curiosity engine and serendipity budget
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-05"]
status: queued
order: 6
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

Build curiosity engine and serendipity budget.

Create:
- agent/daydream/curiosity.py
- agent/daydream/serendipity.py
- tests/daydream/test_curiosity_serendipity.py
- docs/daydream/CURIOSITY_ENGINE.md
- docs/daydream/SERENDIPITY_BUDGET.md

Curiosity questions:
- What changed in the world?
- What changed in the repo?
- What is newly possible?
- What is obsolete?
- What should Sam know about?
- What should this agent become next?
- What feature would compound the most?
- What bottleneck keeps appearing?
- What tool did another AI agent/project build that we should study?
- What has been repeatedly blocked?
- What should be revisited later?

Serendipity:
- 80% known interests/current agent needs by default
- 20% adjacent/weird discoveries by default
- novelty score
- source diversity
- boredom/saturation input later

Commands:
- daydream curiosity
- daydream topics --suggest
- daydream serendipity --dry-run

No external research yet. Generates topic plans.
