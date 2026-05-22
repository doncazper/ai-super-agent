# Release Checklist

- [x] All tests pass or failures are documented.
- [x] No forbidden capabilities introduced.
- [x] No accidental personal-data access.
- [x] Audit logs verified.
- [x] Policy behavior verified.
- [x] Approval behavior verified for high/critical actions in scope.
- [x] Approval lifecycle audit events verified for approval-required actions in scope.
- [x] Critical approval reuse is blocked.
- [x] Secrets redacted from debug and audit outputs.
- [x] Capability manifest includes trust levels, audit fields, storage flags, and web rate limits.
- [x] Sensitive path denylist includes SSH, GPG, Keychain, Messages, Mail, Application Support, AWS, config, and `.env`.
- [x] Prompt-injection regressions cover web, email, messages, and workspace-file content.
- [x] Weather hardening verified: ToolBroker-only current/forecast path, manifest entries, audit metadata, rate limits, opt-in default location, no system location inference, structured outputs/errors, no live-network unit tests, and no personal-data tools enabled by weather.
- [x] Weather cache avoids precise-looking street addresses and direct coordinates.
- [x] NWS provider verified with mocked geocoding, points/grid, forecast, hourly, alerts, unsupported-location, timeout, and audit-domain tests.
- [x] Safe weather preferences verified: no default location by default, explicit default only, default-use audit source, units/cache preferences, config CLI, and no memory write by default.
- [x] Weather-aware web research verified: simple weather remains weather-only, delay/closure/storm update prompts add web only when needed, web-disabled/provider failures become limitations, untrusted snippets are filtered, and weather/web results stay separated.
- [x] WeatherKit remains stub-only: decision record exists, credentials are checked by presence only, no JWT signing/API calls are implemented, and secrets are not logged.
- [x] Docs updated.
- [x] `docs/COMPLETION_REPORT.md` updated.
- [x] Next milestone identified.
- [x] Approval gates checked.

## Release Gate Result

M0-M11 implementation tests pass locally. The post-connector release gate passed locally on 2026-05-22 after the Weather connector pattern, feature maturity tracking, weather-only daily briefing, NWS path, safe Weather preferences, weather-aware web research, and WeatherKit stub work.

Real-world release/use still requires human review of disabled-by-default personal and write/send capabilities before enabling connectors. Live LM Studio, weather provider, and web-provider smoke tests should be run with the user's configured local services and keys before broader use.
