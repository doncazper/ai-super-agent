---
prompt_id: DAYDREAM-14
pack_id: daydream-lab-idle-research-v1
title: Daydream journal and report store
category: daydream
risk_level: LOW
approval_gate: false
depends_on: ["DAYDREAM-13"]
status: queued
order: 14
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

Build Daydream journal and report store.

Create:
- agent/daydream/reports.py
- agent/daydream/journal.py
- tests/daydream/test_journal_reports.py
- docs/daydream/DAYDREAM_JOURNAL.md
- docs/daydream/DAYDREAM_REPORT_STORE.md
- reports/daydream/.gitkeep

Report types:
- session report
- idea card
- research brief
- source note
- blocked/risky idea list
- prompt-pack candidate
- digest
- watchlist/change report
- roadmap recommendation
- ask-sam questions

Rules:
- Redacted.
- No raw secrets.
- No personal data by default.
- No raw full source storage by default.
- Source IDs and limitations required.
- Reports stored locally under reports/daydream or configured path.
- Generated reports policy documented.

Commands:
- daydream journal --last
- daydream report --last
- daydream reports list
- daydream reports show <report_id>
