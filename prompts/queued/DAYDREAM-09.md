---
prompt_id: DAYDREAM-09
pack_id: daydream-lab-idle-research-v1
title: Feature wishlist generator
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-08"]
status: queued
order: 9
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

Build feature wishlist generator.

Create:
- agent/daydream/feature_wishlist.py
- tests/daydream/test_feature_wishlist_generator.py
- docs/daydream/FEATURE_WISHLIST_GENERATOR.md

Sources:
- repo feature roadmap
- feature maturity gaps
- command registry gaps
- performance bottlenecks
- QA/self-heal reports
- memory kernel gaps
- AI ecosystem findings
- user interests
- source diet topic plans

Wishlist categories:
- agent architecture
- safety/governance
- memory/knowledge
- research/intelligence
- creative media
- local model runtime
- business automation
- content creation
- real estate tools
- healthcare/NEMT tools
- productivity
- developer ergonomics
- weird/experimental ideas

Commands:
- daydream wishlist
- daydream wishlist --category <category>
- daydream feature-ideas
- daydream feature-ideas --from-gaps

Output: idea cards only, no implementation.
