# Prompt Record: Prompt Pack import and splitting support

prompt_id: PROMPT-PACK-IMPORT
title: Prompt Pack import and splitting support
category: tracking
status: completed
source: user
created_at: 2026-05-23T00:00:00-07:00
pasted_to_codex: yes
started_at: 2026-05-23T00:00:00-07:00
completed_at: 2026-05-23T00:00:00-07:00
branch: main
commit_hash: pending
related_feature_ids: PROMPT-LEDGER
related_files: agent/prompts, agent/ui/prompts.py, agent/ui/cli_commands.py, docs/PROMPT_PACK_FORMAT.md, docs/templates/prompt_pack_template.md, tests/test_prompt_pack.py
expected_outputs: Prompt pack parser, validator, splitter, queue/ledger/audit integration, CLI commands, docs, tests
commands_expected: prompts validate-pack, prompts import, prompts split, prompts next, pytest
commands_run: pytest tests/test_prompt_pack.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q; pytest -q; startup policy validation; capability manifest validation; smart_agent.py prompts audit; git diff --check
tests_expected: prompt pack tests, full test suite, docs validation, startup policy validation, capability manifest validation
tests_run: focused prompt pack/docs validation, full suite, startup policy validation, capability manifest validation, prompt audit CLI, diff whitespace check
test_result: focused 28 passed; full suite 503 passed; startup policy ok; capability manifest ok; diff whitespace check passed
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
completion_report_updated: yes
blockers: none
next_prompt_id: NATIVE-SKILLS-FOUNDATION
supersedes: PROMPT-LEDGER-QUEUE
superseded_by:
notes: Import-only prompt pack support. Imported prompts are queued and never executed automatically.
