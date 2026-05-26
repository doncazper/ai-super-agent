---
prompt_id: DAYDREAM-08
pack_id: daydream-lab-idle-research-v1
title: Safe public research planner
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-07"]
status: queued
order: 8
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

Build safe public research planner.

Create:
- agent/daydream/research_planner.py
- tests/daydream/test_safe_research_planner.py
- docs/daydream/SAFE_PUBLIC_RESEARCH_PLANNER.md

Planner:
- accepts topic/interest/idea
- selects allowed source lanes
- respects budgets
- free-first
- official/API-first
- no bypass
- no paid APIs by default
- no personal data
- no memory write
- no large downloads
- no source content training
- returns research plan and what it will not do

Commands:
- daydream research-plan "<topic>"
- daydream run --topic "<topic>" --dry-run
- daydream run --safe --dry-run

If Web/AI Ecosystem/Authorized Scan modules exist, plan through them. Otherwise use mock/planned providers only.
No live research yet unless existing safe provider commands are explicitly safe and mocked.
