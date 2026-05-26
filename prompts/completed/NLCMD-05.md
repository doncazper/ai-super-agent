---
prompt_id: NLCMD-05
pack_id: natural-language-command-understanding-v1
title: Safe execution planner and natural-language preflight
category: safety
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-04"]
status: completed
order: 5
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:12:25+00:00
completed_at: 2026-05-25T22:00:06+00:00
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
Build safe execution planner and natural-language preflight.

Goal:
Convert natural-language intent into a safe execution plan that can be previewed, dry-run, approved, or denied before any tool or command execution.

Scope:
- Execution plan.
- Preflight display.
- Dry-run integration.
- Tests.

Non-goals:
- Do not execute HIGH/CRITICAL actions.
- Do not auto-run personal-data commands.
- Do not bypass ToolBroker.
- Do not bypass ApprovalManager.

Create/update:
- agent/natural_language/execution_plan.py
- agent/natural_language/preflight.py
- tests/natural_language/test_nl_execution_plan_preflight.py
- docs/natural_language/NL_PREFLIGHT.md

Execution plan fields:
- plan_id
- original_request
- intent
- command
- args
- risk_level
- trust_level
- approval_required
- dry_run_required
- toolbroker_required
- expected_side_effects
- provider_requirements
- missing_requirements
- audit_preview
- memory_behavior
- safe_to_execute

Commands:
- python smart_agent.py nl preflight "request"
- python smart_agent.py nl explain "request"
- python smart_agent.py nl suggest "request"

Requirements:
1. Preflight executes no tools.
2. Safe/LOW read-only commands may be suggested for execution.
3. HIGH/CRITICAL actions require Action Center/approval.
4. Unknown commands denied/suggest help.
5. Missing provider/setup reported.
6. Plan includes exact command to run.
7. Audit summary included.
8. Command registry updated.

Tests:
- safe weather request creates safe plan.
- web research plan shows provider requirement.
- email send plan requires approval and not safe_to_execute.
- file write plan requires approval/preview.
- unknown command denied.
- preflight executes no tools.
- command registry updated.

Update docs/tracking.

Final report:
- preflight added
- commands added
- tests run/results
- next recommended prompt
