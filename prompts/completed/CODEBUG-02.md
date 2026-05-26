---
prompt_id: CODEBUG-02
pack_id: codebase-bug-review-and-hardening-v1
title: Safety-control-plane bug review
category: safety
risk_level: HIGH
approval_gate: false
depends_on: ["CODEBUG-01"]
status: completed
order: 2
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:32:28+00:00
completed_at: 2026-05-25T22:00:12+00:00
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
Review safety control plane for bugs.

Goal:
Find and fix safe/scoped bugs in ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, redaction, trust/risk models, and capability manifest validation.

Scope:
- Safety-control-plane review.
- Tests and regression tests.
- Safe/scoped fixes only.

Non-goals:
- Do not weaken policy.
- Do not make risky actions easier.
- Do not enable personal tools.
- Do not skip audits.
- Do not change CRITICAL approval reuse rules.

Check:
- unknown tools denied
- unknown capabilities denied
- ToolBroker-only execution
- PolicyEngine decisions
- approval requirements for HIGH/CRITICAL
- no approval reuse for CRITICAL
- personal-data tools disabled by default
- audit hash chain integrity
- secret redaction
- untrusted content cannot change policy
- rate limits if present
- capability manifest strictness

Create/update:
- docs/bugfix/SAFETY_CONTROL_PLANE_REVIEW.md
- tests/regressions/ for fixed bugs where practical

Run targeted safety tests and full tests if practical.

Final report:
- bugs found
- bugs fixed
- tests added
- remaining blockers
