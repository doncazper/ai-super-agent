---
prompt_id: NLCMD-03
pack_id: natural-language-command-understanding-v1
title: Natural-language request parser and deterministic router
category: core
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-02"]
status: completed
order: 3
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:03:36+00:00
completed_at: 2026-05-25T22:00:05+00:00
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
Build natural-language request parser and deterministic command router.

Goal:
Given a user request, classify intent and propose the safest next action without relying on LLM-only safety decisions.

Scope:
- Parser/router.
- Deterministic rules.
- Optional LLM interpretation as non-authoritative suggestion if existing architecture supports it.
- Tests.

Non-goals:
- Do not execute high-risk commands.
- Do not route personal-data requests automatically.
- Do not add new tools.
- Do not bypass existing router or ToolBroker.

Create:
- agent/natural_language/
  - __init__.py
  - models.py
  - parser.py
  - router.py
  - safety.py
  - errors.py
- tests/natural_language/test_nl_parser_router.py

Models:
- NaturalLanguageRequest
- IntentCandidate
- CommandSuggestion
- NLRouteDecision
- ClarificationQuestion
- NLExecutionPlan

Router decision fields:
- original_text
- normalized_text
- intent
- confidence
- command_suggestions
- safety_outcome
- risk_level
- approval_required
- dry_run_required
- clarification_required
- reason
- evidence
- audit_summary

Requirements:
1. Deterministic rules first.
2. LLM suggestions, if used, cannot override safety outcome.
3. Exact commands still work normally.
4. No-tools mode preserved.
5. Ambiguous requests ask clarification.
6. Risky personal/send/write requests produce preflight/approval/dry-run only.
7. Unknown requests fall back to chat/help.
8. Natural language parser does not call tools.
9. Parser does not access personal data.
10. Router decisions are testable.

Tests:
- "what's the weather in Phoenix" maps to weather current.
- "look this up" maps to web/research with clarification if missing query.
- "what commands do I have for memory" maps to help/commands search.
- "fix the last session bugs" maps to session review/bugfix suggestion.
- "send this email" requires approval/preflight/unsupported depending capability.
- ambiguous short request asks clarification.
- no-tools mode does not route tools.
- exact command unaffected.
- high-risk request not executed.

Update docs/tracking.

Final report:
- parser/router added
- tests run/results
- next recommended prompt
