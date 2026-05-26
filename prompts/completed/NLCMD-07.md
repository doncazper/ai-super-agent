---
prompt_id: NLCMD-07
pack_id: natural-language-command-understanding-v1
title: Natural-language eval fixtures
category: tests
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-06"]
status: completed
order: 7
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:25:15+00:00
completed_at: 2026-05-25T22:00:07+00:00
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
Build natural-language command understanding eval fixtures.

Goal:
Create a repeatable eval set that checks whether the agent correctly understands common natural-language terminal requests, maps them to safe commands, asks clarifying questions, or blocks risky actions.

Create:
- eval_cases/natural_language/
- tests/natural_language/test_nl_eval_fixtures.py
- docs/natural_language/NL_EVALS.md

Eval categories:
1. weather
2. web/research
3. news
4. reddit/forums
5. help/commands
6. doctor/status
7. memory safe requests
8. workspace read/summarize
9. prompt tracker
10. bug/session review
11. ambiguous requests
12. risky personal-data requests
13. send/write requests
14. unsupported requests
15. deprecated/legacy commands

Each eval case:
- input_text
- expected_intent
- expected_safety_outcome
- expected_command_group
- should_execute
- should_clarify
- should_require_approval
- should_deny
- notes

Commands:
- python smart_agent.py eval run --natural-language
- python smart_agent.py eval report --natural-language

Tests:
- eval fixtures load.
- safe cases pass.
- risky cases do not execute.
- ambiguous cases clarify.
- unsupported cases report help.
- command registry updated.

Update docs/tracking.

Final report:
- eval fixtures added
- tests run/results
- next recommended prompt
