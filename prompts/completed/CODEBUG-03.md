---
prompt_id: CODEBUG-03
pack_id: codebase-bug-review-and-hardening-v1
title: CLI and command bug review
category: command_registry
risk_level: MEDIUM
approval_gate: false
depends_on: ["CODEBUG-02"]
status: completed
order: 3
created_at: 2026-05-25T19:29:34+00:00
imported_at: 2026-05-25T19:29:34+00:00
source_pack: prompts/packs/codebase-bug-review-and-hardening-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:35:00+00:00
completed_at: 2026-05-25T22:00:13+00:00
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
Review CLI and command system for bugs.

Goal:
Find and fix bugs where commands fail, help text is wrong, exact commands break, natural-language routing conflicts with exact commands, commands are undocumented, or docs list commands that do not exist.

Scope:
- smart_agent.py
- CLI modules
- COMMAND_REGISTRY
- help/docs
- tests

Non-goals:
- Do not add major new command groups.
- Do not change command semantics broadly.
- Do not execute risky commands.
- Do not access personal data.

Check:
- empty invocation UX
- doctor
- --no-tools
- --debug
- --interactive
- commands list/show/search/validate if present
- runtime/brain/platform/promptops/native skill command groups if present
- deprecated/stubbed commands labeled correctly
- command examples accurate
- Python wrapper scripts if present

Create/update:
- docs/bugfix/CLI_COMMAND_REVIEW.md
- docs/COMMAND_REGISTRY.md
- docs/COMMAND_TEST_MATRIX.md if present

Add tests for fixed command bugs.

Run command validation and targeted CLI tests.

Final report:
- command bugs found/fixed
- command registry changes
- tests run/results
