---
prompt_id: DAYDREAM-05
pack_id: daydream-lab-idle-research-v1
title: Source diet and research provider strategy
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-04"]
status: queued
order: 5
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

Build source diet and research provider strategy.

Create:
- agent/daydream/sources.py
- agent/daydream/provider_strategy.py
- tests/daydream/test_source_diet_provider_strategy.py
- docs/daydream/SOURCE_DIET.md
- docs/daydream/RESEARCH_PROVIDER_STRATEGY.md

Source lanes:
- AI agent repos
- Hugging Face/model releases
- GitHub trending/releases
- arXiv papers
- official product changelogs
- Apple developer news
- real estate/investing public sources
- creator economy trends
- restaurant/food media trends
- healthcare business/regulatory public sources
- sports/content trends
- internal repo gaps
- QA/performance/self-heal reports
- Memory Kernel gaps

Each source:
- source_id
- allowed
- frequency
- cost
- official/API available
- trust level
- retention policy
- no-bypass policy
- live_provider_required
- implementation_status

Commands:
- daydream sources
- daydream sources show <source_id>
- daydream sources policy

Default is free/public/API-first/mock-first.
No live source fetch in this prompt.
