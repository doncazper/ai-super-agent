---
prompt_id: DAYDREAM-13
pack_id: daydream-lab-idle-research-v1
title: Blocked, risky, fantasy, and not-worth-it idea classifier
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-12"]
status: queued
order: 13
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

Build blocked/risky/fantasy/not-worth-it idea classifier.

Create:
- agent/daydream/risk_classifier.py
- tests/daydream/test_risk_classifier.py
- docs/daydream/BLOCKED_RISKY_FANTASY_IDEAS.md

Classifications:
- safe_to_build
- needs_approval
- research_only
- legal_compliance_risk
- privacy_risk
- high_cost
- too_hard_now
- blocked_do_not_implement
- fantasy
- not_worth_it
- revisit_later

Blocked categories:
- bypass tooling
- credential abuse
- stealth scraping
- hidden persistence
- unapproved sends/writes
- personal-data mining
- auto code changes
- auto purchases/downloads
- unsafe medical/legal/financial advice

Commands:
- daydream blocked-ideas
- daydream risky-ideas
- daydream classify <idea_id>
- daydream revisit-later <idea_id> --after <condition>

Document safe alternative path for risky ideas.
