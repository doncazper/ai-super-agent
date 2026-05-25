# Prompt Record: REDDIT-SEARCH-WORKFLOWS

prompt_id: REDDIT-SEARCH-WORKFLOWS
title: Reddit search workflows
category: forums
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on: [REDDIT-READ-ONLY-CONNECTOR]
status: completed
source: roadmap
created_at: 2026-05-25
pasted_to_codex: no
started_at: 2026-05-25T03:20:26+00:00
completed_at: 2026-05-25T03:26:40+00:00
branch: checkpoint/large-working-tree-20260523
commit_hash:
related_feature_ids: REDDIT-FORUM-INTELLIGENCE-TRACK, REDDIT-READ-ONLY-CONNECTOR, REDDIT-SEARCH-WORKFLOWS
related_files: agent/forums/reddit/client.py, agent/forums/reddit/models.py, agent/forums/reddit/provider.py, agent/forums/reddit/retention.py, agent/forums/reddit/policy.py, agent/tools/forums/reddit.py, agent/ui/cli_commands.py, agent/ui/command_registry.py, config/capabilities.yaml, tests/test_reddit_search_workflows.py, tests/test_reddit_read_only_connector.py, docs/forums/REDDIT_SEARCH.md
files_expected:
files_changed:
expected_outputs: Search ergonomics for global/subreddit Reddit search with sort, time, limit, advisory language, source labels, setup hints, docs, and tests.
commands_expected: reddit search, reddit explain-result
commands_run: python smart_agent.py reddit search "private sensitive query" --language zh --limit 10; python smart_agent.py reddit explain-result reddit_post_missing; command registry validation; startup policy validation; capability manifest validation; targeted and full pytest
tests_expected: mocked search workflow tests, sensitive-query redaction tests, setup hint tests, command registry validation, startup/capability validation
tests_run: tests/test_reddit_read_only_connector.py; tests/test_reddit_search_workflows.py; tests/test_reddit_provider_policy.py; tests/test_command_registry.py; tests/test_prompt_tracking.py; tests/test_feature_maturity_docs.py; full pytest
test_result: focused Reddit search/read-only/provider tests passed; command registry, startup policy, and capability manifest validation passed; final full suite recorded in completion report
docs_updated: CHANGELOG, PROJECT_STATE, FEATURE_REGISTRY, FEATURE_MATURITY, FEATURE_ROADMAP, COMMAND_REGISTRY, COMMAND_TEST_MATRIX, REDDIT_SEARCH docs, README, risk/threat/test/release docs, completion report
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links: docs/forums/REDDIT_SEARCH.md, tests/test_reddit_search_workflows.py, docs/COMMAND_REGISTRY.md, docs/COMPLETION_REPORT.md
blockers: Live Reddit API validation not run; remains explicit opt-in after OAuth configuration.
next_prompt_id: REDDIT-THREAD-FETCH-NORMALIZATION
supersedes:
superseded_by:
notes: Read-only official Reddit API search workflow polish; no scraping, no writes, no paid provider default, no search-history persistence.
