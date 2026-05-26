---
prompt_id: DAYDREAM-23
pack_id: daydream-lab-idle-research-v1
title: User guide, handoff, and production polish
category: daydream
risk_level: LOW
approval_gate: false
depends_on: ["DAYDREAM-22"]
status: queued
order: 23
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

Add user guide, handoff, and production polish for Daydream Lab.

Create/update:
- docs/daydream/DAYDREAM_USER_GUIDE.md
- docs/daydream/DAYDREAM_QUICKSTART.md
- docs/daydream/DAYDREAM_LIMITATIONS.md
- docs/daydream/DAYDREAM_AUTO_RUN_SETUP_FUTURE.md
- docs/HANDOFF_TO_CHATGPT.md, if this repo uses it
- README.md
- docs/USER_GUIDE.md if present
- docs/HELP.md if present

Guide must explain:
- what Daydream does
- what it does not do
- manual run
- idle-status
- idle-run dry-run
- automatic idle disabled by default
- safe budgets
- interest controls
- source diet
- journal/reports
- what-were-you-thinking command
- idea promotion
- build-next advisor
- no-send/no-code/no-prompt-run/no-memory-write boundaries
- future explicit auto-run setup requirements

Run docs/command validations.
