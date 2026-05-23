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
- [x] Open-Meteo live safe eval verified for `Phoenix, AZ` after city/state geocode fallback hardening.
- [x] Weather cache avoids precise-looking street addresses and direct coordinates.
- [x] NWS provider verified with mocked geocoding, points/grid, forecast, hourly, alerts, unsupported-location, timeout, and audit-domain tests.
- [x] Safe weather preferences verified: no default location by default, explicit default only, default-use audit source, units/cache preferences, config CLI, and no memory write by default.
- [x] Weather-aware web research verified: simple weather remains weather-only, delay/closure/storm update prompts add web only when needed, web-disabled/provider failures become limitations, untrusted snippets are filtered, and weather/web results stay separated.
- [x] WeatherKit remains stub-only: decision record exists, credentials are checked by presence only, no JWT signing/API calls are implemented, and secrets are not logged.
- [x] Personal connector readiness gate passed: ToolBroker, PolicyEngine, approval UI, dry-run/preflight, AuditLogger, secret redaction, connector registry, personal default-disabled manifest entries, HIGH/CRITICAL approval rules, untrusted-content wrappers, memory defaults, denial tests, non-interactive blocking, and direct-call scans were verified.
- [x] No live personal-data reads were performed during the readiness gate.
- [x] Calendar read-only selected-range connector verified: disabled by default, HIGH risk, approval-required, selected-range only, no notes/body, location redaction by default, availability without event details, event text labeled as data, no memory storage by default, and audited access.
- [x] Contacts read-only selected-scope connector verified: disabled by default, HIGH risk, approval-required, no bulk export, compact search first, selected-token reads only, no notes, phone/email/address redacted by default, contact text labeled as data, no memory storage by default, and audited access.
- [x] Contacts approved edits v1 verified: disabled by default, CRITICAL per-action approval only, Action Center draft/update/create stubs, exact field-level diff previews, bulk edit denied, delete deferred, sensitive contact values redacted in previews/audits, no memory storage by default, and brokered audited execution.
- [x] Email metadata + selected-thread + draft-only verified: disabled by default, HIGH risk, approval-required, no send/delete/move/archive, no bulk ingestion, metadata/body labeled `UNTRUSTED_EMAIL`, body wrapped as untrusted data, prompt-injection filtering, no body memory storage by default, body audit redaction, and audited access.
- [x] Email approved send v1 verified: disabled by default, CRITICAL per-action approval only, Action Center reviewed drafts required, direct unreviewed sends blocked, no approval reuse, no bulk/background sends, attachments blocked in v1, editing invalidates approval, mock provider only, no credentials stored, no private Mail database scraping, no memory storage by default, and brokered audited execution.
- [x] Messages/text draft-only verified: disabled by default, HIGH risk, approval-required, no send/delete/move/archive/contact harvesting, no bulk history, no Messages database scraping, no Full Disk Access dependency, `messages.draft_from_text` workspace-only fallback, `UNTRUSTED_MESSAGE` labeling, no body memory storage by default, body audit redaction, and audited access.
- [x] Messages safe handoff v1 verified: no automatic send, no Messages database scraping, no Full Disk Access, workspace-only context reads, save/copy handoff through Action Center approval, workspace-bounded saved drafts, clipboard copy explicit/audited, no memory storage by default, and automatic send deferred by decision record.
- [x] Browser selected URL and clipping v1 verified: explicit URL workflows only, URL fetches through `web.fetch_url`, clips write through `filesystem.write` under `./workspace`, content labels are `UNTRUSTED_WEB`/`UNTRUSTED_DOCUMENT`, selected-tab native integration is stubbed/disabled, no browser history/cookies/sessions/passwords/profile databases are accessed, and audit logs cover fetch/write/stub paths.
- [x] Knowledge Capture v1 verified: captures store only under `./workspace/captures`, notes/files/URLs route through brokered tools, URL/file content remains untrusted data, secrets are rejected before writes, Apple Notes/private app databases are not accessed, memory promotion goes through Memory v2 policy, and personal-looking content is not stored in memory by default.
- [x] Prompt Ledger and Prompt Queue tracking verified: ledger/queue/audit docs exist, prompt record directories and template exist, prompt CLI commands are tested, queued prompts have prompt IDs, project state records `active_prompt_id` and `next_prompt_id`, AGENTS requires prompt updates, and blocked send/overnight prompts remain gated.
- [x] Prompt Pack import/splitting verified: pack format docs/template exist, importer rejects `execute_all`, validate-pack writes no files, import stores packs under `prompts/packs`, split prompts go under `prompts/queued`, prompt bodies are preserved, dependencies/approval gates affect `prompts next`, and no imported prompt executes automatically.
- [x] PromptOps Workbench verified: one-command import from stdin/file/clipboard works, raw single prompts can be queued, runner is disabled by default, autopilot is safe-only and refuses HIGH/approval-gated prompts, reports redact secret-like values, and no imported prompt executes automatically.
- [x] Command Registry + Manual QA verified: command registry/test matrix/legacy/runbook docs and templates exist, 150 commands are cataloged, command metadata validation passes, README and AGENTS reference the registry, and `commands qa-run` prints SAFE/LOW examples without executing commands.
- [x] Scheduler / Automation v1 verified: schedule create/list/run/pause/delete work locally, v1 is manual-run only with no hidden persistence, scheduled tool workflows retain ToolBroker/policy/approval/audit gates, personal scheduled sections require approval, and CRITICAL actions do not execute automatically.
- [x] Controlled actions and workflow batch release gate passed: full tests, startup policy, capability manifest, command registry validation, safe eval, ToolBroker/default personal-data/CRITICAL approval scans, feature maturity sync, and prompt queue sync completed.
- [x] Docs updated.
- [x] `docs/COMPLETION_REPORT.md` updated.
- [x] Next milestone identified.
- [x] Approval gates checked.

## Release Gate Result

M0-M11 implementation tests pass locally. The post-connector release gate passed locally on 2026-05-22 after the Weather connector pattern, feature maturity tracking, weather-only daily briefing, NWS path, safe Weather preferences, weather-aware web research, WeatherKit stub work, and the personal connector readiness gate.

The controlled actions and workflow batch release gate passed locally on 2026-05-23 after Action Center, approved-write stubs, tasks, messages handoff, browser clipping, knowledge capture, Daily Briefing v2, Meeting Follow-Up, Task Extraction, controlled self-improvement loop, PromptOps, Command Registry, and Scheduler v1 work. Full tests, startup policy, manifest validation, command registry validation, safe eval, default personal-data, CRITICAL approval, and ToolBroker path scans passed.

Real-world release/use still requires human review of disabled-by-default personal and write/send capabilities before enabling connectors. Live LM Studio, weather provider, and web-provider smoke tests should be run with the user's configured local services and keys before broader use.
