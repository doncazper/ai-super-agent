# Changelog

## Unreleased

- Added feature maturity tracking with `docs/FEATURE_MATURITY.md`, `docs/FEATURE_REGISTRY.md`, `docs/PROJECT_STATE.md`, and `docs/FEATURE_ROADMAP.md`.
- Added a reusable feature maturity template under `docs/templates/`.
- Added documentation validation for feature maturity tracking.
- Added a weather-only daily briefing command that uses only brokered weather tools and avoids personal-data sources.
- Added NOAA/National Weather Service as a U.S.-only no-key weather provider with forecast and alerts support.
- Added safe weather preferences with explicit default-location config, units, cache controls, and CLI show/set/clear commands.
- Added weather-aware web research routing/workflow for delays, closures, and storm updates while keeping simple weather weather-only.
- Added a WeatherKit connector decision record and provider stub without implementing JWT signing or Apple API calls.
