# Project State

Last updated: 2026-05-22.

## Baseline

- M0-M11 baseline is complete.
- Safety control plane is the most mature reusable pattern.
- Weather is the most developed post-baseline connector, now with Open-Meteo, U.S.-only NWS provider paths, a WeatherKit planning stub, explicit safe preferences, and web research only for weather-impact/current-context questions.
- Daily briefing now has a weather-only first workflow that avoids personal data.
- Personal-data connectors remain disabled by default.
- Write/send actions remain disabled by default and approval-gated.

## Maturity Summary

Most mature features:

- ToolBroker / PolicyEngine / AuditLogger: `8 Mature Pattern`
- Weather connector: `7 User-Ready`
- LM Studio no-tool chat: `5 Hardened`
- Web search/fetch/research: `5 Hardened`
- Workspace file assistant: `5 Hardened`
- Memory: `5 Hardened`

Least mature features:

- Meeting prep: `0 Idea`
- Email triage: `1 Specified`
- Messages draft-only: `2 Scaffolded`
- Agent dashboard: `3 Implemented`

Features needing hardening:

- Calendar read-only
- Contacts read-only
- Email draft-only
- Messages draft-only
- Agent dashboard

Features needing live validation:

- LM Studio no-tool chat with the currently configured local model.
- Weather-only daily briefing with Open-Meteo.
- NWS current/forecast/alerts CLI smoke with a U.S. location.
- Weather-impact web research with a configured web provider.
- WeatherKit decision review before any JWT/signing implementation.
- Web search/fetch/research with a configured Brave Search key.
- Calendar read-only against a selected range with explicit user approval.
- Contacts read-only against a selected contact with explicit user approval.
- Email draft-only against a deliberately configured non-production account.

Features needing docs:

- Meeting prep
- Email triage
- Agent dashboard consolidation

Features needing tests:

- Meeting prep
- Email triage
- Full dashboard workflow tests

## Current Recommended Work Up Next

Post-connector release gate passed locally on 2026-05-22 with full tests, startup policy validation, focused safety tests, feature maturity docs validation, direct-execution search, and secret scan.

Next build batch should proceed in this order: finish connector foundation, polish UX/approvals, build web research, build memory, build selected-scope calendar/contacts, build email drafts, build text drafts, build useful workflows, and only then approved writes/sends. Each step must update maturity tracking and stop at the relevant approval gates.

Run live LM Studio no-tool smoke with the configured `LMSTUDIO_MODEL`, then document whether it passed. After that, live-smoke Open-Meteo and NWS weather commands if network access is desired. Choose the next low-risk external connector only through a decision record. Use Weather as the reference pattern for provider abstraction, ToolBroker-only execution, audit metadata, cache/privacy behavior, CLI diagnostics, and maturity tracking.

## Gates

- Do not add connector framework work until `docs/FEATURE_MATURITY.md`, `docs/FEATURE_REGISTRY.md`, `docs/PROJECT_STATE.md`, `AGENTS.md`, and docs validation are updated and tests pass.
- Do not enable personal-data tools by default.
- Do not add send/write actions without approval UI and per-action gates.
- Do not mark a feature mature because it merely exists.
