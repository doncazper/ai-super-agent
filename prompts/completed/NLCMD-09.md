---
prompt_id: NLCMD-09
pack_id: natural-language-command-understanding-v1
title: Natural-language bug feedback loop
category: bugs
risk_level: LOW
approval_gate: false
depends_on: ["NLCMD-08"]
status: completed
order: 9
created_at: 2026-05-25T19:52:09+00:00
imported_at: 2026-05-25T19:52:09+00:00
source_pack: prompts/packs/natural-language-command-understanding-v1.md
trust_level: UNTRUSTED_DOCUMENT
started_at: 2026-05-25T20:38:17+00:00
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
Build natural-language bug feedback loop.

Goal:
When the agent misunderstands a natural-language request, the user should be able to flag it and the system should create a structured bug/regression fixture.

Scope:
- Feedback tags.
- Bug report templates.
- Regression fixture generation.
- Tests.

Non-goals:
- Do not fix all NL bugs in this prompt.
- Do not store personal data.
- Do not weaken policy.

Add feedback tags:
- misunderstood_intent
- wrong_command_suggested
- should_have_clarified
- should_have_denied
- should_have_required_approval
- executed_when_should_not
- failed_to_find_command
- poor_natural_language_answer

Create/update:
- docs/natural_language/NL_BUG_TRIAGE.md
- docs/templates/nl_regression_case_template.yaml
- tests/natural_language/test_nl_bug_feedback_loop.py

Commands if practical:
- python smart_agent.py feedback nl-bug --last --expected-intent <intent>
- python smart_agent.py bugs create-nl-regression <bug_id>
- python smart_agent.py nl regressions list

Requirements:
1. NL feedback attaches to last command/session entry.
2. Regression fixture contains sanitized input.
3. Personal data redacted.
4. Expected safe behavior captured.
5. Regression case can be added to eval_cases/natural_language.
6. Command registry updated.

Tests:
- feedback tag accepted.
- regression case generated.
- personal data redacted.
- fixture loads in eval suite.
- command registry updated.

Update docs/tracking.

Final report:
- feedback loop added
- tests run/results
- next recommended prompt
