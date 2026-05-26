---
prompt_id: CANON-09
pack_id: canonical-runtime-gateway-hardening-v1
title: Tracker-to-canonical-state migration plan
category: prompt_tracking
risk_level: LOW
approval_gate: false
depends_on: ["CANON-08"]
status: completed
order: 9
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:46:46+00:00
completed_at: 2026-05-26T05:51:09+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tracker sync/canonical dashboard/canonical state tests 15 passed; command registry validation 587; policy-check passed
docs_updated: yes
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
notes: Added read-only tracker-sync-preview and tracker-conflicts commands/docs; no auto-overwrite, broad rewrite, provider call, or tracker mutation.
---

# Prompt

Create migration plan from dense markdown trackers toward canonical runtime state as machine-readable truth.

Create/update:
- docs/runtime/TRACKER_TO_CANONICAL_STATE_MIGRATION.md
- docs/runtime/CANONICAL_STATE_TRACKER_SYNC_POLICY.md
- docs/prompt_tracker/CANONICAL_STATE_INTEGRATION.md
- tests/runtime/test_tracker_canonical_state_sync.py

Plan:
- canonical state is machine-readable truth for active work
- prompt ledger remains historical evidence
- prompt queue remains planned-order view
- prompt audit remains reconciliation view
- project state becomes human-readable resume summary
- completion report remains release evidence
- tracker dashboard remains summary only
- handoff file becomes external communication summary

Commands if practical:
- python smart_agent.py runtime tracker-sync-preview
- python smart_agent.py runtime tracker-conflicts

Do not auto-overwrite trackers broadly.
Use conflict reports and small anchored edits only.
