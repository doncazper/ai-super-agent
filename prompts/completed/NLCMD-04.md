---
prompt_id: NLCMD-04
pack_id: natural-language-command-understanding-v1
title: Clarification and confirmation flow
category: ux
risk_level: MEDIUM
approval_gate: false
depends_on: ["NLCMD-03"]
status: completed
order: 4
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:06:35+00:00
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
Build clarification and confirmation flow for natural-language commands.

Goal:
When a natural-language request is ambiguous, risky, or missing parameters, the agent should ask a useful clarifying question or show a safe command suggestion instead of failing or guessing.

Scope:
- Clarification model.
- CLI display.
- Tests.
- No risky execution.

Create/update:
- agent/natural_language/clarification.py
- agent/natural_language/preview.py
- tests/natural_language/test_clarification_flow.py
- docs/natural_language/CLARIFICATION_FLOW.md

Clarification types:
- missing_required_argument
- multiple_matching_commands
- risky_action
- personal_data_request
- provider_missing
- ambiguous_intent
- unsupported_capability
- command_is_stubbed
- command_is_deprecated

Requirements:
1. Ask one clear question when possible.
2. Offer exact command examples.
3. Show why approval/dry-run is required.
4. Do not expose secrets.
5. Do not access personal data.
6. Do not execute tools during clarification.
7. If a command is deprecated, suggest replacement.
8. If a provider is missing, suggest doctor/setup command.
9. If intent is unknown, offer help search.

Tests:
- missing location asks for location.
- multiple command matches offer choices.
- provider missing suggests doctor.
- deprecated command suggests replacement.
- personal-data request says approval/setup required.
- risky send/write request does not execute.
- command registry updated if CLI changed.

Update docs/tracking.

Final report:
- clarification flow added
- tests run/results
- next recommended prompt
