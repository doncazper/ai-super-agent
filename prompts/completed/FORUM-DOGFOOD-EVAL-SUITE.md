# Prompt Record: FORUM-DOGFOOD-EVAL-SUITE

prompt_id: FORUM-DOGFOOD-EVAL-SUITE
title: Forum Intelligence dogfood/eval suite
category: forums
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on: [CHINESE-FORUM-DISCOVERY]
status: completed
source: user
created_at: 2026-05-25T05:39:16+00:00
pasted_to_codex: unknown
started_at: 2026-05-25T05:39:16+00:00
completed_at: 2026-05-25T05:52:12+00:00
branch:
commit_hash:
related_feature_ids: FORUM-DOGFOOD-EVAL-SUITE
related_files: dogfood_suites/reddit_core.yaml, dogfood_suites/reddit_research.yaml, dogfood_suites/forum_multilingual.yaml, dogfood_suites/v2ex.yaml, dogfood_suites/chinese_forum_discovery.yaml, eval_cases/forums/forum_intelligence.json, docs/forums/FORUM_DOGFOOD_RUNBOOK.md
files_expected: dogfood_suites/reddit_core.yaml, dogfood_suites/reddit_research.yaml, dogfood_suites/forum_multilingual.yaml, dogfood_suites/v2ex.yaml, dogfood_suites/chinese_forum_discovery.yaml, eval_cases/forums/, docs/forums/FORUM_DOGFOOD_RUNBOOK.md
files_changed: agent/ui/evals.py, agent/ui/cli_commands.py, agent/ui/command_registry.py, dogfood_suites/reddit_core.yaml, dogfood_suites/reddit_research.yaml, dogfood_suites/forum_multilingual.yaml, dogfood_suites/v2ex.yaml, dogfood_suites/chinese_forum_discovery.yaml, eval_cases/forums/forum_intelligence.json, tests/test_forum_dogfood_eval.py, docs/forums/FORUM_DOGFOOD_RUNBOOK.md
expected_outputs: dogfood suites, forum eval cases, eval CLI flags, command registry updates, docs and tracker updates
commands_expected: python smart_agent.py dogfood run reddit_core --session; python smart_agent.py dogfood run reddit_research --session; python smart_agent.py dogfood run forum_multilingual --session; python smart_agent.py eval run --forums; python smart_agent.py eval report --forums
commands_run:
tests_expected: suite YAML validates; all_safe excludes live Reddit requiring credentials; fixtures do not contain real personal data; evals pass with mocks; command registry updated
tests_run: ./.venv/bin/python -m pytest tests/test_forum_dogfood_eval.py -q; ./.venv/bin/python -m pytest tests/test_forum_dogfood_eval.py tests/test_dogfood_suites.py tests/test_eval_harness.py tests/test_command_registry.py tests/test_feature_maturity_docs.py tests/test_prompt_tracking.py -q; ./.venv/bin/python -m pytest -q; ./.venv/bin/python smart_agent.py eval run --forums --json; forum dogfood dry-runs; startup policy validation; capability manifest validation; commands validate
test_result: focused forum dogfood/eval tests 7 passed; focused docs/command/maturity tests 56 passed; eval run --forums passed 5 and skipped 5 personal-data evals; forum dogfood dry-runs ok; startup policy ok; capability manifest ok with 185 capabilities; command registry ok with 382 commands; full suite 1034 passed, 2 skipped
docs_updated: docs/forums/FORUM_DOGFOOD_RUNBOOK.md, dogfood suite docs, README, command registry/test matrix, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, project state, changelog, completion report
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links:
blockers:
next_prompt_id: FORUM-INTELLIGENCE-RELEASE-GATE
supersedes:
superseded_by:
notes: Completed mock-first Forum Intelligence dogfood/eval suite. Next recommended prompt: FORUM-INTELLIGENCE-RELEASE-GATE.
