---
prompt_id: EXTREV-01
pack_id: canonical-runtime-gateway-hardening-v1
title: External architecture review hardening parity checks
category: review
risk_level: MEDIUM
approval_gate: false
depends_on: ["CANON-09"]
status: completed
order: 10
created_at: 2026-05-26T04:45:51+00:00
imported_at: 2026-05-26T04:45:51+00:00
source_pack: prompts/packs/canonical-runtime-gateway-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-26T05:51:09+00:00
completed_at: 2026-05-26T05:56:56+00:00
branch:
commit_hash:
related_feature_ids: []
expected_outputs:
files_expected:
files_changed:
tests_expected:
tests_run:
test_result: tests/test_external_review_parity_docs.py and tests/test_command_registry.py passed: 9 passed; commands validate ok with 589 commands
docs_updated: docs/reviews/EXTERNAL_ARCHITECTURE_REVIEW_FINDINGS.md, docs/reviews/EXTERNAL_REVIEW_HARDENING_PLAN.md, docs/reviews/EXTERNAL_REVIEW_PARITY_CHECKLIST.md, docs/COMMAND_REGISTRY.md, docs/COMMAND_TEST_MATRIX.md
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
notes: External architecture review parity docs completed; audit receipt commands tracked as planned only; no runtime command implemented.
---

# Prompt

Convert external architecture review findings into targeted hardening follow-ups.

Context:
A third-party source/documentation architecture review identified:
1. Tamper-evident audit receipts.
2. Native skill vetting diagnostics.
3. Source/provider explainability.
4. High-risk action approval semantics.
5. Backup restore policy-weakening checks.
6. Self-improvement safety lints.
It warned not to overclaim planned/scaffolded capabilities as product-ready.

Create:
- docs/reviews/EXTERNAL_ARCHITECTURE_REVIEW_FINDINGS.md
- docs/reviews/EXTERNAL_REVIEW_HARDENING_PLAN.md
- docs/reviews/EXTERNAL_REVIEW_PARITY_CHECKLIST.md

Check/report:
A. Audit receipts:
- audit hash-chain verification
- audit receipt export
- action/tool execution tied to audit receipt
- if missing, add planned command rows or small safe diagnostics only

B. Native skill diagnostics:
- manifest validation
- trust/provenance/lockfile/conflict/test harness status
- correct tracker overclaims if clear

C. Source/provider explainability:
- router explain path
- selected/skipped provider reporting
- no-store/no-memory flags visible

D. High-risk approval semantics:
- exact preview matching
- edit invalidates approval
- consume-once approval
- CRITICAL no approval reuse
- execution re-enters ToolBroker

E. Backup restore policy weakening:
- restore rejects policy/capability weakening
- pre-restore copy/hash verification

F. Self-improvement safety lints:
- protected safety files and policy-weakening diff checks

G. Overclaim cleanup:
- scan FEATURE_MATURITY and FEATURE_REGISTRY for planned/stubbed/metadata-only capabilities marked too mature
- correct only clear overclaims

Run targeted tests and validations. Do not rebuild major systems.
