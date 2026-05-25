# Prompt Record: News Capability Manifest Provider Policy

prompt_id: news-capability-manifest-provider-policy
title: News capability manifest entries and provider policy
category: news-intelligence
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on: [news-intelligence-roadmap]
status: completed
source: user
created_at: 2026-05-25T09:14:27+00:00
pasted_to_codex: unknown
started_at: 2026-05-25T09:25:21+00:00
completed_at: 2026-05-25T09:35:43+00:00
branch:
commit_hash:
related_feature_ids: NEWS-INTELLIGENCE-ROADMAP
related_files: config/capabilities.yaml, .env.example, docs/news/NEWS_PROVIDER_STRATEGY.md, docs/news/NEWS_RETENTION_POLICY.md, docs/COMMAND_REGISTRY.md
files_expected: capability manifest/news provider policy/config defaults/tests/docs/tracker updates
files_changed:
expected_outputs: disabled/planned news capability entries, free-first provider policy defaults, no history/article body defaults, no paid API defaults
commands_expected: capability manifest validation, startup policy validation, command registry validation, tests
commands_run:
tests_expected: capability manifest validates, unknown news capability denied, paid providers disabled by default, CRITICAL actions absent from news v1, provider policy free-first, search history disabled by default
tests_run:
test_result: News provider-policy tests 10 passed; focused News/docs/maturity tests 28 passed; full suite 1119 passed, 1 skipped; startup policy ok; capability manifest ok; command registry ok.
docs_updated: Updated capabilities manifest, News docs, README, .env.example, changelog, project state, feature registry, feature maturity, roadmap, risk register, threat model, test plan, release checklist, completion report, tracker dashboard.
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
notes: Completed disabled/planned News capability manifest entries and provider policy only; no provider calls, article fetch, paid API default, search-history storage, or full article-body persistence.
