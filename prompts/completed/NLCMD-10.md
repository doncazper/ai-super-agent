---
prompt_id: NLCMD-10
pack_id: natural-language-command-understanding-v1
title: Natural-language command understanding release gate
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-09"]
status: completed
order: 10
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:44:17+00:00
completed_at: 2026-05-25T22:00:08+00:00
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
Run Natural-Language Command Understanding release gate and maturity review.

Goal:
Validate that the natural-language command understanding layer improves usability while preserving safety, command registry truth, approval gates, and existing exact command behavior.

Run:
1. full test suite
2. startup policy validation
3. capability manifest validation
4. docs validation
5. command registry validation
6. natural-language eval suite
7. natural-language dogfood suite with safe fixtures
8. exact command regression tests

Verify:
- exact commands still work.
- no-tools mode preserved.
- natural-language requests map to safe commands.
- ambiguous requests clarify.
- risky requests require preflight/approval.
- personal-data requests do not execute by default.
- HIGH/CRITICAL actions not executed.
- command registry is source of truth.
- evals/dogfood exist.
- feedback loop exists.
- docs/user guide updated.
- feature maturity conservative.

Create/update:
- docs/natural_language/NL_COMMAND_RELEASE_GATE.md
- docs/natural_language/NL_COMMAND_MATURITY_REVIEW.md

Maturity assessment:
- NL architecture/taxonomy
- command intent index
- parser/router
- clarification flow
- preflight/execution plan
- CLI UX
- eval fixtures
- dogfood suite
- bug feedback loop
- release gate

Classify each:
- Idea
- Specified
- Scaffolded
- Implemented
- Tested
- Hardened
- Live-Validated
- User-Ready
- Mature Pattern

Update:
- CHANGELOG.md
- README.md
- docs/USER_GUIDE.md if present
- docs/HELP.md if present
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md

Final report:
- tests run/results
- validation results
- eval/dogfood results
- maturity score
- remaining blockers
- whether NL command understanding is safe to rely on
- next recommended feature track
