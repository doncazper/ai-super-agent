# Feature Roadmap

This roadmap prioritizes maturity before breadth. Each item must update `docs/FEATURE_MATURITY.md`, `docs/FEATURE_REGISTRY.md`, `docs/PROJECT_STATE.md`, `docs/COMPLETION_REPORT.md`, and `CHANGELOG.md` when user-visible tracking changes.

## Now

1. Keep feature maturity tracking validated by tests.
2. Use the next build batch order: connector foundation, UX/approvals polish, web research, memory, selected-scope calendar/contacts, email drafts, text drafts, useful workflows, then approved writes/sends.
3. Run live LM Studio no-tool smoke with the current local model.
4. Repeat live Weather smoke for Open-Meteo, NWS alerts, weather-impact web research, and weather-only daily briefing when network access is desired.
5. Review `docs/decisions/weatherkit_provider.md` before any WeatherKit JWT/signing implementation.

## Next

1. Live-validate Web search/fetch/research with a configured provider.
2. Improve the Agent dashboard so connector status, audit, permissions, memory, and maturity are easier to inspect.
3. Create a decision record before any new connector.
4. Decide whether daily briefing should remain weather-only or add optional sources behind explicit approvals.

## Later

1. Calendar read-only live selected-scope smoke, with explicit approval.
2. Contacts read-only live selected-scope smoke, with explicit approval.
3. Email draft-only live validation against a deliberate non-production account.
4. Meeting prep specification.
5. Email triage specification.

## Hold

- Messages live connector remains held until a safe permissioned implementation path exists.
- Send/write actions remain disabled until draft-only workflows and approval UX are fully validated.
- Device location and IP geolocation remain out of scope for Weather.
