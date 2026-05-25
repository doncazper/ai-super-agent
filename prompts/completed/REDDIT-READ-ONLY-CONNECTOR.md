# Prompt Record: REDDIT-READ-ONLY-CONNECTOR

prompt_id: REDDIT-READ-ONLY-CONNECTOR
title: Reddit read-only connector v1
category: forums
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on: [REDDIT-OAUTH-CONFIG-DOCTOR]
status: completed
source: user
created_at: 2026-05-25T02:52:23+00:00
pasted_to_codex: yes
started_at: 2026-05-25T02:52:23+00:00
completed_at: 2026-05-25
branch: checkpoint/large-working-tree-20260523
commit_hash:
related_feature_ids: REDDIT-READ-ONLY-CONNECTOR, REDDIT-PROVIDER-POLICY-COMPLIANCE, REDDIT-OAUTH-CONFIG-DOCTOR
related_files: agent/forums/reddit/, agent/tools/forums/reddit.py, agent/ui/cli_commands.py, agent/ui/command_registry.py, config/capabilities.yaml, tests/test_reddit_read_only_connector.py
files_expected: Reddit client/models/provider/normalizer/errors/retention modules, tests, docs, command registry, tracking docs
files_changed: Reddit connector modules, brokered Reddit tools, CLI dispatch, ToolBroker redaction/trust handling, capability manifest, README, Reddit docs, command registry/test matrix, feature/risk/threat/test/release tracking, prompt tracking
expected_outputs: Official Reddit Data API read-only connector with search/subreddit/post/comments/cache/retention commands and no write or scraping surface
commands_expected: reddit search, reddit subreddit, reddit post, reddit comments, reddit cache clear, reddit retention sweep
commands_run: command docs generation; startup policy validation; capability manifest validation; command registry validation; focused pytest; CLI setup-required/cache smokes
tests_expected: mocked connector tests, rate-limit/error tests, retention/cache tests, command registry validation, startup/capability validation
tests_run: focused Reddit policy/doctor/read-only connector tests 32 passed; focused command/prompt/maturity/Reddit tests 55 passed; full suite 951 passed, 2 skipped
test_result: passed
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links: docs/COMPLETION_REPORT.md, tests/test_reddit_read_only_connector.py, docs/forums/REDDIT_COMPLIANCE.md
blockers: Live Reddit API validation not run; remains opt-in and credential/config dependent.
next_prompt_id: REDDIT-SEARCH-WORKFLOWS
supersedes:
superseded_by:
notes: Completed local mocked read-only v1. No Reddit web scraping fallback, unauthenticated traffic, posting/commenting/voting/DM/moderation, content training, permanent user-content storage, or query-history persistence was added.
