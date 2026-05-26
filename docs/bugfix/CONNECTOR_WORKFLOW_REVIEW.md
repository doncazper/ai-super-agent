# Connector And Workflow Bug Review

Prompt ID: `CODEBUG-05`
Date: 2026-05-25

## Scope

Review connector and workflow status paths, setup hints, disabled-by-default behavior, paid-provider gates, and mock-first workflow tests.

## Non-Goals

- No live provider calls.
- No new connector implementation.
- No paid API usage.
- No personal-data enablement.
- No send/write enablement.
- No CAPTCHA, login-wall, paywall, or anti-bot bypass.

## Evidence Reviewed

- Connector status commands:
  - `connectors list`
  - `connectors status reddit`
  - `reddit status`
  - `v2ex doctor`
  - `web providers`
  - `weather doctor`
- Focused connector/workflow tests listed below.
- Existing connector and workflow test files under `tests/`.

## Findings

| Finding | Severity | Status | Evidence |
|---|---:|---|---|
| Paid web providers remain skipped by default | n/a | verified | `web providers` reports `allow_paid_apis: false`; Brave and SerpAPI are not allowed by policy. |
| Weather default path remains free-first | n/a | verified | `weather doctor` selects Open-Meteo/NWS and leaves WeatherAPI not default-allowed. |
| Reddit remains disabled without OAuth/config | n/a | verified | `reddit status` reports `enabled: false`, OAuth required, no API calls, no user content stored, write actions disabled. |
| V2EX remains disabled/read-only without config | n/a | verified | `v2ex doctor` reports disabled, read-only, no network call, no personal data access, no write capabilities. |
| Connector/workflow focused tests pass | n/a | verified | 440 focused tests passed. |

## Bugs Fixed

No CODEBUG-05 code fixes were needed. Provider setup/status behavior is conservative and tests are passing.

## Bugs Deferred

| Bug ID | Severity | Status | Notes |
|---|---:|---|---|
| CODEBUG-P2-003 | P2 | needs_review | Provider/setup UX remains broad. No failing behavior was confirmed, but `connectors list` is very verbose and includes historical `last_error` values that may confuse users. Treat as future UX polish, not a scoped bug fix. |

## Tests And Validation

- `./.venv/bin/python -m pytest -q tests/test_connectors.py tests/test_connector_framework.py tests/test_weather.py tests/test_web.py tests/test_web_acquisition.py tests/test_web_acquisition_robots_feeds_sitemaps.py tests/test_web_cache_index.py tests/test_official_api_connectors.py tests/test_news_capability_provider_policy.py tests/test_reddit_provider_policy.py tests/test_reddit_oauth_doctor.py tests/test_reddit_read_only_connector.py tests/test_reddit_search_workflows.py tests/test_reddit_thread_workflows.py tests/test_reddit_summarization.py tests/test_reddit_retention_cache.py tests/test_v2ex_connector.py tests/test_forum_provider_registry.py tests/test_chinese_forum_discovery.py tests/test_cross_language_forum_research.py tests/test_workflows.py tests/test_knowledge_capture.py tests/test_calendar_approved_writes.py tests/test_contacts_approved_edits.py tests/test_email_approved_send.py tests/test_messages_safe_handoff.py tests/test_tasks_connector.py`: 440 passed.
- `./.venv/bin/python smart_agent.py web providers`: passed; paid providers skipped by policy.
- `./.venv/bin/python smart_agent.py weather doctor`: passed; free-first providers selected.
- `./.venv/bin/python smart_agent.py reddit status`: passed; disabled without OAuth/config and no content fetched.
- `./.venv/bin/python smart_agent.py v2ex doctor`: passed; disabled/read-only and no network call.
- `./.venv/bin/python smart_agent.py connectors status reddit`: passed; clear setup hint and no personal reads.

## Safety Notes

No connector path reviewed here enabled personal-data tools by default, bypassed policy gates, used paid APIs by default, performed live content fetches unexpectedly, or enabled send/write behavior.
