# Changelog

All notable project changes are tracked here. This file follows a Keep-a-Changelog style structure and must not contain secrets or private user data.

## Unreleased

### Added

- Personal connector readiness checklist at `docs/checklists/personal_connector_readiness.md`, with evidence for ToolBroker, policy, approval, audit, memory, untrusted-content, and disabled-by-default personal connector gates.
- Selected-scope calendar read-only connector validation with brokered `calendar read` and `calendar availability` commands, optional Calendar.app AppleScript adapter, and event-text-as-data safety labeling.
- Selected-scope contacts read-only connector validation with brokered `contacts search` and `contacts read` commands, optional Contacts.app AppleScript adapter, sensitive-field gates, and contact-text-as-data safety labeling.
- Email metadata + selected-thread + draft-only assistant validation with brokered `email metadata/read/summarize/draft-reply` commands, optional IMAP adapter, untrusted email labeling, and no-send draft output.
- Messages/text draft-only assistant validation with brokered `messages read/summarize/draft-reply/draft-from-text` commands, explicit `messages.draft_from_text` capability, and workspace-only manual fallback.
- Daily Briefing v1 with optional brokered weather, calendar selected-range, email metadata, web topic search, reminders stub, dry-run, and JSON output.
- Meeting prep workflow with brokered selected calendar event read, optional approved contact lookup, optional web topic search, dry-run, and JSON output.
- Email Triage v1 with brokered metadata-only priority classification, optional selected-thread summary, draft-only reply generation, dry-run, and JSON output.
- Self-improvement backlog/propose commands that inspect approved project files through brokered, audited `filesystem.read` calls and produce ranked read-only improvement proposals.
- Agent Dashboard v1 with `dashboard` and `status` commands for read-only runtime, LM Studio, tools, connectors, permissions, pending approvals, audit metadata, memory counts, risk settings, last test run, and setup hints.
- Live eval harness commands `eval list`, `eval run`, and `eval report` for controlled feature validation without personal-data access by default.
- Unified Action Center v1 with `actions list/show/approve/deny/edit/clear-denied/export`, persisted action records, redacted exact previews, approval queue integration, one-time approval consumption, and action lifecycle audits.
- Calendar approved writes v1 with `calendar draft-create/create --from-action`, `calendar draft-update/update --from-action`, and `calendar draft-delete/delete --from-action`; drafts create Action Center records and approved executions still go through `ToolBroker`.
- Reminders / Tasks connector v1 with adapter interface, mock provider, brokered `tasks.list/create/update/complete/delete`, and Action Center `tasks draft-create` plus `tasks create --from-action`.
- Contacts approved edits v1 with `contacts draft-update/update --from-action` and `contacts draft-create/create --from-action`; drafts create Action Center records with field-level diffs and approved executions still go through `ToolBroker`.
- Email approved send v1 with `email draft-new`, Action Center backed `email draft-reply`, and `email send --from-action`; send execution requires an approved Action Center item and supports only a mock provider until a real send provider is separately approved.
- Messages safe handoff v1 with `messages.save_draft` and `messages.copy_draft` Action Center handoff actions plus a decision record at `docs/decisions/messages_send_path.md`.
- Browser selected URL and clipping v1 with `browser read-url`, `browser summarize-url`, `browser clip-url --to workspace`, and a selected-tab stub plus a decision record at `docs/decisions/browser_selected_tab_clipping.md`.
- Knowledge Capture v1 with `capture note`, `capture from-file`, `capture from-url`, `capture list`, `capture summarize`, and `capture promote-to-memory` for a workspace-only local knowledge inbox.
- Daily Briefing v2 with configurable `weather`, `calendar`, `tasks`, `email`, `web`, `memory`, and `suggested_actions` sections, `briefing config show/set`, brokered dry-run previews, independent section failure handling, and Action Center queued suggestions.
- Meeting Follow-Up workflow with `meeting follow-up --event-id`, `meeting follow-up --notes-file`, dry-run/JSON output, workspace-bounded notes reads, deterministic decisions/action-items extraction, and Action Center queued task/email/calendar suggestions.
- Personal Task Extraction workflow with `tasks extract --from-notes`, `--from-email-thread`, `--from-meeting`, `--from-url`, `--from-capture`, dry-run/JSON output, untrusted source filtering, and Action Center queued task drafts.
- Controlled self-improvement implementation loop with `improve implement`, `improve run-tests`, `improve show-diff`, and approval-gated `improve commit --from-action`.
- Prompt Ledger and Prompt Queue tracking with `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_AUDIT.md`, prompt record directories, a prompt record template, and `prompts list/next/show/add/mark-active/mark-complete/mark-skipped/mark-failed/audit/missing` CLI commands.
- Prompt Pack import/splitting support with strict `<<<PROMPT_PACK_START>>>` format validation, pack storage under `prompts/packs/`, split prompt files under `prompts/queued/`, ledger/queue/audit integration, and `prompts validate-pack/import/split/mark-superseded` commands.
- PromptOps Workbench v1 with `work import`, `work import-clipboard`, `work next`, `work copy-next`, `work show-next`, `work resume`, `work status`, `work review`, `work run-next`, `work autopilot`, and `work audit` commands for one-command prompt ingestion and resume-safe queue handling.
- Command Registry and Manual QA System with generated `docs/COMMAND_REGISTRY.md`, `docs/COMMAND_TEST_MATRIX.md`, `docs/COMMAND_LEGACY.md`, `docs/COMMAND_QA_RUNBOOK.md`, command record templates, and read-only `commands list/show/search/legacy/deprecated/validate/qa-plan/qa-run` CLI commands.
- Scheduler / Automation v1 with explicit local `schedule list/create/run/pause/delete` commands for manual-run daily briefing, connector doctor, safe eval, memory cleanup, and audit summary workflows.
- Eval report template at `docs/EVAL_REPORT.md`.
- Durable project tracking files: `docs/PROJECT_STATE.md`, `docs/FEATURE_REGISTRY.md`, `docs/FEATURE_ROADMAP.md`, and tracking templates.
- Feature maturity tracking with `docs/FEATURE_MATURITY.md` and `docs/templates/feature_maturity_template.md`.
- Documentation validation for project tracking and feature maturity files.
- Weather-only daily briefing command that uses only brokered weather tools and avoids personal-data sources.
- NOAA/National Weather Service as a U.S.-only no-key weather provider with forecast and alerts support.
- Safe weather preferences with explicit default-location config, units, cache controls, and CLI show/set/clear commands.
- Weather-aware web research routing/workflow for delays, closures, and storm updates while keeping simple weather weather-only.
- WeatherKit connector decision record and provider stub without implementing JWT signing or Apple API calls.
- Reusable connector metadata/status framework under `agent/connectors/` and CLI connector dashboard routing through it.
- Prompt-free `smart_agent.py preflight "<request>"` command for brokered dry-run previews of routed or exact tool/capability requests.
- Workspace file assistant CLI commands for brokered list/read/summarize/search/write/patch/diff operations inside approved roots.
- Memory v2 CLI commands for brokered add/search/list/export/delete/clear/context operations.

### Changed

- Project tracking now records the next feature set as Controlled Actions and Proactive Workflows, starting with a live validation and eval harness before any approved write/send implementation.
- Codex working rules now require prompt ledger/queue reads, active/completed prompt status updates, prompt audit updates after major batches, and final reports with `prompt_id` plus `next_prompt_id`.
- Codex working rules now direct pasted mega prompts through `work import` and restrict `work autopilot` to safe categories with approval-gate stops.
- Codex working rules now require command registry and command test matrix updates whenever CLI commands are added, renamed, deprecated, removed, or behaviorally changed.
- Feature roadmap release-gate status now marks the accumulated post-baseline workflow batch as synced after the full test suite, startup policy validation, capability manifest validation, and docs validation passed.
- Full feature maturity release gate now marks the controlled actions and workflow batch complete after full tests, startup policy validation, capability manifest validation, command registry validation, safe eval, ToolBroker/default personal-data/CRITICAL approval scans, and docs sync.
- Source-grounded research reports fetch failures in a first-class `fetch_failures` field and includes an explicit no-fabricated-citations source policy.
- `filesystem.read` results and audit trust now label file content as `UNTRUSTED_DOCUMENT`.
- Memory search now supports category filters, and memory context injection returns a bounded non-personal context block with injected memory IDs.
- Runtime `doctor` now reports normalized capability manifest validation, `ToolBroker` initialization, connector registry loading, personal connector defaults, and CRITICAL action defaults without sending model prompts or executing tools.
- Connector dashboard status now includes normalized capability summaries and `setup_hint` in addition to the existing docs setup hint.
- Capability manifest entries now use a normalized schema with capability/tool/connector names, approval reuse, rate limit, memory behavior, setup hint, and docs reference fields.
- Connector dashboard status is now backed by reusable connector metadata/status primitives instead of UI-local status logic.
- Project roadmap now prioritizes batch order, approval gates, and resume-safe handoff state.
- AGENTS working rules now require PROJECT_STATE, changelog, feature registry, roadmap, and completion report updates after meaningful runs.

### Fixed

- Open-Meteo and NWS geocoding now retry comma-separated city/region inputs such as `Phoenix, AZ` by searching the city and preferring matching administrative regions when the upstream geocoder does not resolve the original query.

### Security

- Personal connector readiness gate passed locally before any new personal-data connector work; no personal-data tools were enabled and no live personal-data reads were performed.
- Calendar read-only remains HIGH risk, disabled by default, approval-required, selected-range only, audited, non-writing, and non-persistent by default.
- Contacts read-only remains HIGH risk, disabled by default, approval-required, selected-scope only, audited, non-writing, no-bulk, and non-persistent by default.
- Email assistant remains HIGH risk, disabled by default, approval-required, selected-thread only, audited, no-send/no-delete/no-move/no-archive, no-bulk, and non-persistent by default.
- Messages/text assistant remains HIGH risk, disabled by default, approval-required, selected-thread or workspace-file only, audited, no-send/no-delete/no-move/no-archive/no-contact-harvesting, no-bulk, no private database scraping, and non-persistent by default.
- Daily Briefing v1 executes only explicitly selected sources through `ToolBroker`, skips unapproved or disabled calendar/email metadata sections, performs no writes/sends, reads no email bodies or messages, and writes no memory by default.
- Daily Briefing v2 keeps all sections opt-in/configurable, skips approval-gated personal sections when approval is denied, reads email metadata only, avoids message reads, performs no writes/sends, and queues suggested actions instead of executing them.
- Meeting prep executes selected calendar event, contact lookup, and web search only through `ToolBroker`; it sends no emails/texts, edits no calendar/contact data, performs no bulk contact export, and writes no memory by default.
- Meeting Follow-Up reads selected events and workspace notes only through `ToolBroker`, treats notes as `UNTRUSTED_DOCUMENT`, filters instruction-injection lines, creates Action Center records for suggested tasks/email/calendar updates, performs no writes/sends, and writes no memory by default.
- Personal Task Extraction reads exactly one selected source through existing brokered tools/connectors, requires approval for personal sources, ignores untrusted source instructions, queues `tasks.create` Action Center drafts only, performs no task writes, and writes no memory by default.
- Controlled self-improvement implementation is branch-based, requires approved proposal records, writes through brokered `filesystem.write`, runs brokered tests/diff, creates Action Center commit records only, and blocks policy weakening, audit disabling, personal-data grants, persistence paths, package installs without approval, and send/write side effects.
- Prompt tracking is SDLC metadata only: it does not add connectors, personal-data access, send/write tools, background automations, or policy exemptions.
- Prompt pack import is import-only: it rejects `execute_all`, preserves prompt bodies as data, and does not run imported prompts automatically.
- PromptOps Workbench treats imported prompt text as `UNTRUSTED_DOCUMENT`, keeps `work run-next` disabled by default, refuses HIGH/CRITICAL/FORBIDDEN or approval-gated prompts in autopilot, and redacts secret-looking values in PromptOps reports.
- Command Registry commands are metadata-only and do not execute agent tools, access connectors, read personal data, grant approvals, or write memory. `commands qa-run` prints SAFE/LOW manual QA examples and does not execute them in v1.
- Scheduler v1 does not install background persistence. Scheduled runs are manual, audited, reuse ToolBroker for tool workflows, require normal approvals for personal sections, and never execute CRITICAL actions automatically.
- Email Triage v1 reads metadata only by default, reads at most one selected thread body after approval, redacts body content from the triage report/audit args, sends nothing, mutates nothing, and writes no memory by default.
- Self-improvement backlog/propose mode is read-only, uses only approved project file reads through `ToolBroker`, audits reads/dry-runs, and blocks safety-weakening suggestions such as disabling audit logs or relaxing policy gates.
- Agent Dashboard v1 is metadata/status-only: it does not attach tools, execute connector actions, read personal data, grant permissions, consume approvals, or start background work; secrets are redacted and memory content is not displayed.
- Eval harness safe runs execute tool checks only through `ToolBroker`, skip personal-data evals by default, perform no sends, perform no calendar/contact writes, and delete the non-sensitive memory test fact before completion.
- Unified Action Center does not execute actions directly; it is a review and approval queue only. Future execution must still pass through `ToolBroker`, `PolicyEngine`, approval rules, and `AuditLogger`; CRITICAL actions remain per-action only and edits invalidate prior approvals.
- Calendar write capabilities remain disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, audited for draft/approval/execution/failure, no automatic invites, no recurring events in v1, no full calendar export, and no notes/body in drafts unless explicitly allowed.
- Tasks connector capabilities remain disabled by default; task listing is HIGH risk and approval-required, task writes are CRITICAL per-action approval only, task creation is Action Center gated, no full task export is performed, no task contents are written to memory by default, and no native Reminders database scraping or Full Disk Access dependency is introduced.
- Contact write capabilities remain disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, audited for draft/approval/execution/failure, no bulk edits, no delete implementation, sensitive field values redacted from previews/audits, and no contact details written to memory by default.
- Email send remains disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, no direct unreviewed model-output send, no bulk sends, no background sends, attachments blocked in v1, body/thread context previewed before approval, and no credentials or private Mail databases are used.
- Messages safe handoff remains no-send: no Messages database scraping, no Full Disk Access dependency, no automatic text sending, save/copy requires Action Center approval, drafts stay in `./workspace` or clipboard only, message content remains `UNTRUSTED_MESSAGE`, and message bodies are not written to memory by default.
- Browser clipping v1 is explicit-URL only: it reads no browser history, cookies, sessions, forms, passwords, bookmarks, or private browser profile databases; URL fetches go through `web.fetch_url`, clips write only through `filesystem.write` under `./workspace`, selected-tab native reading remains disabled/stubbed, and clipped content is labeled `UNTRUSTED_DOCUMENT`.
- Knowledge Capture v1 stores captures only under `./workspace/captures`, rejects secret-looking content before writing, uses brokered `filesystem.read/write` and `web.fetch_url`, treats URL/file captures as untrusted data, performs no Apple Notes integration or private app database scraping, and promotes to memory only through `memory.store` policy.
- Web research excerpting is stricter: instruction-injection-only page text is not reused as fallback evidence.
- File assistant workflows treat document content as untrusted data, filter instruction-like text in summaries/search excerpts, and continue to rely on workspace root checks, backups, and audit logging.
- Memory v2 refuses secrets, keeps personal memory approval-gated, excludes personal memory from default context injection, and audits injected memory IDs.
- Runtime and connector diagnostics remain read-only: they do not send model prompts, attach tools, read personal data, grant permissions, or change config.
- Startup capability validation now rejects missing normalized fields, missing trust/approval/risk rules, personal-data capabilities enabled by default, CRITICAL actions without per-action approval, and manifest bypass flags.
- Connector status and health checks remain metadata-only and do not execute personal-data reads.
- Connector status output redacts secret-like fields.
- Preflight evaluations run through `ToolBroker.dry_run()`, execute no tools, show approval requirements, and redact sensitive arguments.
- Tracking rules explicitly preserve ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger gates.

### Deprecated

- Ad hoc connector status logic in UI modules is superseded by `agent.connectors`.

### Removed

- No runtime features removed.

### Known Limitations

- Live LM Studio, web provider, weather provider, and personal connector smoke tests still require the user's local configuration and explicit approvals where applicable.
- Personal-data tools remain disabled by default and are not release-ready for broad unattended use.
- Prompt reconstruction is best-effort; queued or blocked prompt groups should be checked against `docs/PROMPT_AUDIT.md` before being treated as missed work.
- Command status and manual QA results are conservative. Most commands are cataloged, but manual verification should be recorded in `docs/COMMAND_TEST_MATRIX.md` as QA suites are run.
