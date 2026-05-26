---
prompt_id: CODEBUG-06
pack_id: codebase-bug-review-and-hardening-v1
title: Prompt tracker, docs, and maturity bug review
category: docs
risk_level: LOW
approval_gate: false
depends_on: ["CODEBUG-05"]
status: completed
order: 6
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:39:24+00:00
completed_at: 2026-05-25T22:00:14+00:00
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
Review prompt tracker, docs, and maturity tracking for bugs.

Goal:
Find and fix inconsistencies in prompt ledger/queue/audit, feature maturity, feature registry, command registry, changelog, completion report, roadmap, and project state.

Scope:
- docs/tracking files
- prompt files
- command registry
- feature maturity
- completion report
- changelog

Non-goals:
- Do not broadly rewrite dense trackers.
- Do not mark prompts complete without evidence.
- Do not inflate feature maturity.
- Do not delete historical evidence.

Check:
- queued prompts missing evidence
- active prompt stale
- prompt pack statuses
- feature maturity overclaiming
- commands without examples
- docs listing nonexistent commands
- changelog mismatch
- completion report mismatch
- PROJECT_STATE stale

Create/update:
- docs/bugfix/TRACKER_DOCS_REVIEW.md
- docs/PROMPT_AUDIT.md if present
- docs/TRACKER_CONSISTENCY_REPORT.md if present

Run docs/command/prompt validations if available.

Final report:
- tracker inconsistencies found/fixed
- docs updated
- prompts needing attention
