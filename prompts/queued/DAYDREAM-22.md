---
prompt_id: DAYDREAM-22
pack_id: daydream-lab-idle-research-v1
title: Daydream release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["DAYDREAM-21"]
status: queued
order: 22
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

Run Daydream Lab release gate and maturity review.

Run:
- full test suite if practical
- startup policy validation
- capability manifest validation
- command registry validation
- prompt tracker validation if available
- daydream tests
- idle/controller tests
- config/budget tests
- interest/source/curiosity tests
- idea/scoring/risk tests
- journal/report tests
- what-were-you-thinking smokes
- prompt-pack incubator dry-run
- roadmap advisor smokes
- integration tests
- eval run --daydream
- dogfood dry-runs

Verify:
- automatic idle-run disabled by default
- no LaunchAgent/cron/daemon installed
- no hidden background persistence
- idle-run blocked during active prompt/job/approval/test/git/user activity
- budgets enforced
- no code changes from daydream
- no prompt-pack execution
- no sends/publishing/buying/downloading/installing
- no personal-data access
- no memory write by default
- no paid APIs/live providers by default
- no bypass
- reports are redacted and source-grounded
- dreams/recommendations/prompt-pack candidates separated
- risky/blocked ideas classified
- prompt-pack promotion is dry-run only
- maturity conservative

Create:
- docs/daydream/DAYDREAM_RELEASE_GATE.md
- docs/daydream/DAYDREAM_MATURITY_REVIEW.md

Update trackers and final report.
