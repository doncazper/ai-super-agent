---
prompt_id: DAYDREAM-17
pack_id: daydream-lab-idle-research-v1
title: Roadmap advisor and build-next shortlist
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-16"]
status: queued
order: 17
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

Build roadmap advisor and build-next shortlist.

Create:
- agent/daydream/roadmap_advisor.py
- tests/daydream/test_roadmap_advisor.py
- docs/daydream/ROADMAP_ADVISOR.md
- docs/daydream/BUILD_NEXT_SHORTLIST.md

Advisor answers:
- What should we build next?
- What should wait?
- What is blocked by architecture?
- What has highest compound value?
- What is fun but low priority?
- What should be revisited later?
- What prompt pack should be next?
- What cleanup should happen before feature work?

Inputs:
- idea rankings
- feature maturity
- prompt queue
- repo gaps
- performance findings
- QA reports
- memory gaps
- user interests

Commands:
- daydream build-next
- daydream roadmap-advice
- daydream waitlist
- daydream revisit

No automatic queue changes.
