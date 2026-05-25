# Prompt Record: WEB-FETCH-EXTRACTION-HARDENING

prompt_id: WEB-FETCH-EXTRACTION-HARDENING
title: Safe web fetch and extraction hardening
category: web-acquisition
pack_id:
risk_level: MEDIUM
approval_gate: false
depends_on:
- BRAVE-PROVIDER
status: completed
source: user
created_at: 2026-05-24
pasted_to_codex: 2026-05-24
started_at: 2026-05-24
completed_at: 2026-05-24
branch: checkpoint/large-working-tree-20260523
commit_hash:
related_feature_ids:
- CONN-WEB
- PROVIDER-COST-POLICY
related_files:
- agent/web_acquisition/fetch.py
- agent/web_acquisition/extraction.py
- agent/web_acquisition/sanitization.py
- agent/web_acquisition/url_normalization.py
- agent/tools/web/fetch.py
- agent/tools/web/extraction.py
- smart_agent.py
- config/capabilities.yaml
files_expected:
- agent/web_acquisition/fetch.py
- agent/web_acquisition/extraction.py
- agent/web_acquisition/sanitization.py
- agent/web_acquisition/url_normalization.py
files_changed:
- agent/web_acquisition/fetch.py
- agent/web_acquisition/extraction.py
- agent/web_acquisition/sanitization.py
- agent/web_acquisition/url_normalization.py
- agent/tools/web/fetch.py
- agent/tools/web/extraction.py
- agent/tools/registry.py
- smart_agent.py
- config/capabilities.yaml
- tests/test_web.py
- docs/web/SAFE_FETCH_AND_EXTRACTION.md
expected_outputs:
- Brokered safe selected-URL fetch/extract/metadata commands
- Structured FetchResult fields
- Prompt-injection and blocked-page safeguards
commands_expected:
- python smart_agent.py web fetch "<url>"
- python smart_agent.py web extract "<url>"
- python smart_agent.py web metadata "<url>"
commands_run:
- ./.venv/bin/python -m pytest tests/test_web.py tests/test_web_acquisition.py tests/test_web_acquisition_robots_feeds_sitemaps.py tests/test_command_registry.py -q
tests_expected:
- mocked fetch/extraction tests
- command registry validation
- startup policy validation
- capability manifest validation
- full suite if feasible
tests_run: focused web/acquisition/command/maturity/prompt tests 91 passed; full suite 876 passed, 2 skipped; startup policy ok; capability manifest ok; command registry ok with 320 commands; prompt audit ok
test_result: pass
docs_updated: yes
changelog_updated: yes
feature_registry_updated: yes
feature_maturity_updated: yes
command_registry_updated: yes
completion_report_updated: yes
evidence_links:
- docs/web/SAFE_FETCH_AND_EXTRACTION.md
- docs/COMPLETION_REPORT.md
blockers: none
next_prompt_id: SOURCE-GROUNDED-RESEARCH-V1
supersedes:
superseded_by:
notes: No live web call, paid API use, browser automation, binary download, cookies/session/form submission, CAPTCHA/login/paywall/anti-bot bypass, or web-content memory storage was added.
