---
prompt_id: DAYDREAM-10
pack_id: daydream-lab-idle-research-v1
title: User-interest research digest
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-09"]
status: queued
order: 10
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

Build user-interest research digest.

Create:
- agent/daydream/interest_digest.py
- tests/daydream/test_interest_digest.py
- docs/daydream/USER_INTEREST_DIGEST.md

Digest types:
- quick
- deep
- weird finds
- business ideas
- agent improvements
- content ideas
- model/tool finds
- local opportunities
- “ask Sam” questions

Commands:
- daydream digest --quick
- daydream digest --deep
- daydream weird-finds
- daydream ask-sam

Rules:
- Use only approved interest map and safe/public research plans.
- No personal-data search.
- No creepy/sensitive inference.
- Cite sources or label as internal idea/speculation.
- Include what was not verified.
