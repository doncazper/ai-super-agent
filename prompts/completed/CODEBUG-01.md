---
prompt_id: CODEBUG-01
pack_id: codebase-bug-review-and-hardening-v1
title: Codebase bug review baseline
category: release_gate
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:31:06+00:00
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
Run Codebase Bug Review Baseline.

Goal:
Establish current codebase health: git state, tests, validations, import errors, command errors, safety checks, and likely bug hotspots.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/TEST_PLAN.md
- docs/RELEASE_CHECKLIST.md

Run:
- git status --short
- git diff --stat
- .venv/bin/python --version if .venv exists
- python version guard check if practical
- targeted import checks
- full test suite if practical
- startup policy validation if available
- capability manifest validation if available
- command registry validation if available
- docs validation if available

Create/update:
- docs/bugfix/CODEBASE_BUG_REVIEW_BASELINE.md
- docs/bugfix/CODEBASE_BUG_HOTSPOTS.md
- docs/bugfix/CODEBASE_BUG_FIX_QUEUE.md

Report:
- failing tests
- import errors
- CLI startup errors
- command registry drift
- docs validation issues
- safety validation issues
- uncommitted files that may affect review
- highest-risk bug hotspots
- recommended fix order

Do not fix bugs in this prompt unless a tiny test/doc issue is blocking the baseline report.

Update tracking docs.

Final report:
- baseline summary
- tests/validations run
- bug hotspot list
- next recommended prompt
