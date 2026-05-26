---
prompt_id: NLCMD-01
pack_id: natural-language-command-understanding-v1
title: Natural-language command understanding architecture
category: core
risk_level: LOW
approval_gate: false
depends_on: []
status: completed
order: 1
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:52:16+00:00
completed_at: 2026-05-25T22:00:04+00:00
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
Create Natural-Language Command Understanding architecture and roadmap.

Goal:
Design a safe layer that lets the user type loose natural-language requests in terminal and have the agent infer intent, map to commands/capabilities, ask clarifying questions, or run safe preflight/dry-run flows.

Before making changes, read:
- SPEC.md
- docs/SDLC.md
- AGENTS.md
- README.md
- CHANGELOG.md
- docs/PROJECT_STATE.md
- docs/FEATURE_REGISTRY.md
- docs/FEATURE_MATURITY.md
- docs/FEATURE_ROADMAP.md
- docs/COMMAND_REGISTRY.md, if present
- docs/COMMAND_TEST_MATRIX.md, if present
- docs/COMPLETION_REPORT.md
- docs/RISK_REGISTER.md
- docs/THREAT_MODEL.md
- docs/RELEASE_CHECKLIST.md
- agent/core/router.py
- smart_agent.py

Scope:
- Architecture docs.
- Intent taxonomy.
- Safety policy.
- Roadmap.
- No runtime behavior change unless trivial docs/help wiring.

Non-goals:
- Do not use LLM routing as sole safety mechanism.
- Do not execute risky actions.
- Do not add personal-data access.
- Do not bypass ToolBroker/Policy/Audit.
- Do not replace existing exact commands.

Create:
- docs/natural_language/NL_COMMAND_UNDERSTANDING_TRACK.md
- docs/natural_language/NL_INTENT_TAXONOMY.md
- docs/natural_language/NL_COMMAND_SAFETY_POLICY.md
- docs/decisions/natural_language_command_understanding.md

Define intent categories:
- chat.no_tools
- chat.general
- doctor.status
- command.help
- command.search
- weather.current
- weather.forecast
- web.research
- news.brief
- reddit.search
- file.read
- file.summarize
- memory.search
- memory.add
- prompt.queue
- git.status
- test.run
- docs.lookup
- bug.report
- session.review
- action.preflight
- personal_data.request
- send_or_write.request
- unknown
- ambiguous

Define safety outcomes:
- answer_directly
- route_to_command
- show_command_suggestion
- run_safe_command
- dry_run_only
- ask_clarifying_question
- require_approval
- deny
- unsupported
- handoff_to_help

Update roadmap/tracking docs.

Run docs validation/tests if available.

Final report:
- files created
- intent taxonomy summary
- safety policy summary
- tests/validations run
- next recommended prompt
