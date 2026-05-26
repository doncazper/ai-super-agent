---
prompt_id: DAYDREAM-16
pack_id: daydream-lab-idle-research-v1
title: Prompt-pack incubator and idea promotion
category: daydream
risk_level: MEDIUM
approval_gate: false
depends_on: ["DAYDREAM-15"]
status: queued
order: 16
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

Build prompt-pack incubator and idea promotion.

Create:
- agent/daydream/prompt_pack_incubator.py
- tests/daydream/test_prompt_pack_incubator.py
- docs/daydream/PROMPT_PACK_INCUBATOR.md

Flow:
- idea card
- research brief
- feature spec
- risk model
- prompt-pack outline
- full prompt-pack draft
- Sam approves later
- Codex imports/runs later

Commands:
- daydream promote <idea_id> --to-prompt-pack --dry-run
- daydream prompt-pack-outline <idea_id>
- daydream prompt-pack-draft <idea_id> --dry-run
- daydream promoted

Rules:
- Does not run prompt pack.
- Does not queue prompt pack unless explicitly approved in future.
- Drafts are saved as candidate artifacts only.
- Includes safety, non-goals, tests, docs, release gate, and Git gate.
- Marks risky/blocked ideas as not eligible for prompt-pack promotion unless safe alternative path exists.
