---
prompt_id: CANON-07
pack_id: canonical-runtime-gateway-hardening-v1
title: Backup roundtrip and restore hardening lane
category: backup
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-06"]
status: completed
order: 7
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:29:55+00:00
completed_at: 2026-05-26T05:38:32+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: backup/restore and roundtrip policy tests 15 passed; command registry validation 583; policy-check passed
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
notes: Added brokered backup roundtrip --dry-run, policy-check, restore-check commands, restore hardening docs, and tests; no live restore outside disposable test workspace.
---

# Prompt

Create backup roundtrip validation and restore policy-weakening hardening.

Create/update:
- docs/backup/BACKUP_ROUNDTRIP_VALIDATION.md
- docs/backup/RESTORE_POLICY_WEAKENING_GUARDS.md
- tests/test_backup_roundtrip_policy.py or update existing backup tests

Check/add tests for:
- backup verifies file hashes
- backup exports redacted archives where required
- restore verifies hashes before writing
- restore creates pre-restore copy where practical
- restore refuses capability manifest that enables personal-data tools by default
- restore refuses CRITICAL approval reuse
- restore refuses policy/audit weakening
- restore refuses unredacted secret material
- restore refuses path traversal
- restore is approval-gated
- disposable project copy recommended for live smoke

Commands if practical:
- python smart_agent.py backup roundtrip --dry-run
- python smart_agent.py backup policy-check
- python smart_agent.py backup restore-check <backup_id>

Do not run real restore outside disposable workspace.
