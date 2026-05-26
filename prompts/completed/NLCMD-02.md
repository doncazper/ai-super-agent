---
prompt_id: NLCMD-02
pack_id: natural-language-command-understanding-v1
title: Command registry intent index
category: command_registry
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-01"]
status: completed
order: 2
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T19:57:08+00:00
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
Build command registry intent index.

Goal:
Make docs/COMMAND_REGISTRY.md usable by the natural-language router by indexing command groups, examples, aliases, intents, risk levels, approval requirements, and prerequisites.

Scope:
- Command registry parsing/indexing.
- Alias metadata.
- Tests.
- No command execution.

Create/update:
- agent/commands/intent_index.py
- agent/commands/models.py if needed
- tests/commands/test_command_intent_index.py
- docs/natural_language/COMMAND_INTENT_INDEX.md

Index fields:
- command_id
- command
- group
- description
- examples
- aliases
- natural_language_triggers
- intent_ids
- risk_level
- approval_required
- provider_required
- connector_required
- safe_to_run_directly
- dry_run_available
- docs_link
- status

Requirements:
1. Exact command registry remains source of truth.
2. Missing command registry handled gracefully.
3. Planned/stubbed/deprecated commands are not suggested as active.
4. HIGH/CRITICAL commands are never run directly from NL intent.
5. Commands requiring providers show setup hints.
6. Alias mapping must be explicit and testable.
7. Search supports fuzzy/natural terms without LLM dependency.
8. No command execution.

Commands if practical:
- python smart_agent.py commands intents
- python smart_agent.py commands suggest "natural language request"

Tests:
- index builds from fixture registry.
- active command suggested.
- deprecated command not primary.
- stubbed command labeled.
- high-risk command dry-run/approval-only.
- provider-required command shows setup hint.
- command registry updated.

Update docs/tracking.

Final report:
- intent index added
- commands added
- tests run/results
- next recommended prompt
