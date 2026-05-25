---
prompt_id: WEB-ROBOTS-SITEMAP-FEED-SUPPORT
title: Build robots.txt, sitemap, and RSS/Atom feed support
category: web-acquisition
status: completed
source: user
created_at: 2026-05-24
pasted_to_codex: true
started_at: 2026-05-24
completed_at: 2026-05-24
branch: checkpoint/large-working-tree-20260523
commit_hash: pending
related_feature_ids:
  - CONN-WEB
files_expected:
  - agent/web_acquisition/robots.py
  - agent/web_acquisition/sitemaps.py
  - agent/web_acquisition/feeds.py
  - docs/web/ROBOTS_AND_RATE_LIMITS.md
  - docs/web/FEEDS_AND_SITEMAPS.md
commands_expected:
  - python smart_agent.py web robots "<domain_or_url>"
  - python smart_agent.py web sitemap "<domain_or_url>"
  - python smart_agent.py web feed "<feed_url>"
test_result: focused tests passed; full-suite status recorded in completion report/final response
docs_updated: true
changelog_updated: true
feature_registry_updated: true
feature_maturity_updated: true
command_registry_updated: true
completion_report_updated: true
next_prompt_id: WEB-SEARCH-PROVIDER-REGISTRY
blockers: none
---

Completed by adding core parser modules, ToolBroker alias capabilities, default limit reconciliation, docs, and focused safety tests. No paid provider, browser automation, login/paywall/CAPTCHA bypass, article-body fetch from feeds, or memory storage path was added.
