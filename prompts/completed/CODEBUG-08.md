---
prompt_id: CODEBUG-08
pack_id: codebase-bug-review-and-hardening-v1
title: Codebase bug review release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["CODEBUG-07"]
status: completed
order: 8
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:41:34+00:00
completed_at: 2026-05-25T22:00:15+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: completed prompt file and prompt audit evidence verified during SOURCE-TRUTH-RECONCILE-01
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
notes: Reconciled stale imported row from completed prompt file and prompt audit evidence; no prompt was run by this reconciliation.
---

# Prompt

You are Codex working in this repo.

Task:
Run Codebase Bug Review release gate.

Goal:
Validate all bug review fixes, update maturity/tracking docs, and produce a final bug review summary.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation if available
5. command registry validation if available
6. prompt tracker validation if available
7. safe eval suite if available
8. dogfood validation with mocks if available

Verify:
- no P0 safety bugs remain open without explicit blocker
- no known ToolBroker bypass
- no known PolicyEngine bypass
- no known ApprovalManager bypass
- no known AuditLogger bypass
- no personal-data tools enabled by default
- no CRITICAL approval reuse
- command registry consistent enough
- docs updated
- regression tests added for fixed bugs
- feature maturity conservative

Create/update:
- docs/bugfix/CODEBASE_BUG_REVIEW_RELEASE_GATE.md
- docs/bugfix/CODEBASE_BUG_REVIEW_SUMMARY.md

Update:
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md if needed
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md if commands changed
- docs/COMMAND_TEST_MATRIX.md if QA changed
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validations run/results
- bugs fixed
- bugs deferred
- regression tests added
- remaining blockers
- next recommended prompt/pack
