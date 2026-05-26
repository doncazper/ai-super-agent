---
prompt_id: NLCMD-06
pack_id: natural-language-command-understanding-v1
title: Conversational CLI UX for natural-language commands
category: ux
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-05"]
status: completed
order: 6
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:17:34+00:00
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
Add conversational CLI UX for natural-language command handling.

Goal:
Make terminal usage friendlier when the user types natural language. The CLI should explain what it understood, what it plans to do, what command matches, and when clarification/approval is required.

Scope:
- CLI integration.
- Help text.
- UX output.
- Tests.

Non-goals:
- Do not break existing exact commands.
- Do not require natural-language mode for all commands.
- Do not call LM Studio for simple command suggestions unless configured.
- Do not execute risky actions.

Modes:
- exact command mode
- natural-language suggestion mode
- natural-language preflight mode
- interactive clarification mode

Possible commands:
- python smart_agent.py ask "natural language request"
- python smart_agent.py nl "natural language request"
- python smart_agent.py nl suggest "request"
- python smart_agent.py nl preflight "request"
- python smart_agent.py nl explain "request"

Behavior:
1. Exact commands remain exact.
2. If user invokes `ask` or `nl`, use NL parser.
3. For safe command, show mapped command and optionally execute only if policy says safe and user requested execution mode.
4. For risky command, show preflight/approval path.
5. For ambiguity, ask clarification.
6. For unknown, offer help/command search.

Tests:
- exact command still works.
- nl weather request maps correctly.
- ask help request maps to command search.
- risky send request not executed.
- ambiguous request asks clarification.
- no-tools mode preserved.
- help text updated.
- command registry updated.

Update:
- README.md.
- docs/USER_GUIDE.md if present.
- docs/HELP.md if present.
- docs/COMMAND_REGISTRY.md.
- docs/FEATURE_MATURITY.md.
- docs/COMPLETION_REPORT.md.
- CHANGELOG.md.

Run tests/validations.

Final report:
- CLI UX changes
- tests run/results
- next recommended prompt
