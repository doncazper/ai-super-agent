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
- Browser clipping capability-name compatibility for canonical `browser.read_url`, `browser.summarize_url`, and disabled `browser.selected_tab` names while retaining legacy selected-URL aliases.
- Knowledge Capture v1 with `capture note`, `capture from-file`, `capture from-url`, `capture list`, `capture summarize`, and `capture promote-to-memory` for a workspace-only local knowledge inbox.
- Knowledge Capture `capture from-file` now supports an explicit `--trusted-user` marker for user-authored workspace files while keeping file captures untrusted by default.
- Daily Briefing v2 with configurable `weather`, `calendar`, `tasks`, `email`, `web`, `memory`, and `suggested_actions` sections, `briefing config show/set`, brokered dry-run previews, independent section failure handling, and Action Center queued suggestions.
- Meeting Follow-Up workflow with `meeting follow-up --event-id`, `meeting follow-up --notes-file`, dry-run/JSON output, workspace-bounded notes reads, deterministic decisions/action-items extraction, and Action Center queued task/email/calendar suggestions.
- Personal Task Extraction workflow with `tasks extract --from-notes`, `--from-email-thread`, `--from-meeting`, `--from-url`, `--from-capture`, dry-run/JSON output, untrusted source filtering, and Action Center queued task drafts.
- Controlled self-improvement implementation loop with `improve implement`, `improve run-tests`, `improve show-diff`, `improve create-action-for-commit`, and approval-gated `improve commit --from-action`.
- Overnight self-improvement safe-mode runbook, report template, report directory, and `improve overnight-plan` planner command for docs/tests/hardening candidate selection without execution.
- Prompt Ledger and Prompt Queue tracking with `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_AUDIT.md`, prompt record directories, a prompt record template, and `prompts list/next/show/add/mark-active/mark-complete/mark-skipped/mark-failed/audit/missing` CLI commands.
- Prompt Pack import/splitting support with strict `<<<PROMPT_PACK_START>>>` format validation, pack storage under `prompts/packs/`, split prompt files under `prompts/queued/`, ledger/queue/audit integration, and `prompts validate-pack/import/split/mark-superseded` commands.
- PromptOps Workbench v1 with `work import`, `work import-clipboard`, `work next`, `work copy-next`, `work show-next`, `work resume`, `work status`, `work review`, `work run-next`, `work autopilot`, and `work audit` commands for one-command prompt ingestion and resume-safe queue handling.
- Command Registry and Manual QA System with generated `docs/COMMAND_REGISTRY.md`, `docs/COMMAND_TEST_MATRIX.md`, `docs/COMMAND_LEGACY.md`, `docs/COMMAND_QA_RUNBOOK.md`, command record templates, and read-only `commands list/show/search/legacy/deprecated/validate/qa-plan/qa-run` CLI commands.
- Scheduler / Automation v1 with explicit local `schedule list/create/run/pause/delete` commands for manual-run daily briefing, connector doctor, safe eval, memory cleanup, and audit summary workflows.
- Scheduler / Automation v1 now also supports optional manual-run `backup_create` schedules, implemented as redacted-only brokered `backup.create` calls.
- Native Skills Program foundation with intake process, native skill criteria, candidate registry, risk model, and reusable native skill record template under `docs/native_skills/`.
- Skill marketplace survey and native-candidate shortlist with category scoring, high-risk deferrals, and a recommended first native skill candidate.
- Native skill vetter v1 with brokered `skills vet`, `skills vet-folder`, and `skills score` commands for workspace-only static analysis of candidate `SKILL.md` files and skill folders.
- Native skill manifest discovery with metadata-only `skills list`, `skills show`, `skills validate`, and `skills doctor` commands plus the first built-in `native_skill_vetter` manifest.
- Native skill finder v1 with brokered `skills find "<query>"`, `native_skills.find_skill`, and a built-in `native_skill_finder` manifest for local-only discovery across manifests, candidate docs, feature registry, and maturity tracker.
- PDF workspace native skill v1 with brokered `pdf info`, `pdf extract-text`, `pdf summarize`, and `pdf extract-tables` commands over approved workspace PDFs.
- Golden Eval Suite and quality scorecards with data-backed cases in `eval_cases/`, `eval run --routing/--policy/--tools/--workflows/--prompt-injection/--lmstudio-live`, per-category scores, and per-run JSON reports under `reports/evals/`.
- Privacy Center / Data Inventory v1 with `privacy status`, `privacy inventory`, `privacy export`, `privacy delete-memory`, `privacy audit-summary`, and `privacy permissions` for metadata-only local data visibility.
- Backup / Restore / Migration v1 with brokered `backup create/list/inspect/verify/export --redacted/restore`, redacted local archives, manifest integrity hashes, restore previews, and approval-gated restore.
- Model-router benchmark and prompt quality evals with `models list`, `models benchmark --safe`, `router eval`, `prompts eval`, and `prompts report` over reviewed fixture prompts and report output.
- Local launcher script at `scripts/agent` that prefers `AI_AGENT_PYTHON`, `./.venv/bin/python`, and the bundled Codex Python runtime before falling back to a Python 3.11+ system interpreter.
- Live Session Logging and Replay with `session start/status/run/end/list/show/replay/export/last`, redacted output capture under `reports/sessions/`, audit-id linking where visible, and `docs/SESSION_LOGGING.md`.
- Manual Dogfood Command Suites with `dogfood list/show/run`, curated suite YAML under `dogfood_suites/`, safe synthetic fixtures under `workspace/dogfood` and `workspace/skills`, and docs under `docs/dogfood/`.
- User feedback capture for live sessions with `feedback good/bad/bug/confusing/slow/unsafe/rate/add/list/export`, redacted session feedback records, replay/show integration, severity escalation for unsafe feedback, and audit events for feedback operations.
- Session Review and Bug Generator with `session review <session_id>`, `session review --last --create-bugs`, `bugs list/show/export`, redacted review reports under `reports/session_reviews/`, local bug records under `bugs/`, and `docs/BUG_TRIAGE.md`.
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

- Overnight self-improvement tracking now records the explicitly approved bounded safe-mode run on `agent/overnight-2026-05-23`, with a live report under `reports/overnight/` and stricter report-template validation.
- Session logs are ignored by git by default except for `reports/sessions/.gitkeep`; committed session fixtures must be sanitized.
- Messages safe handoff tools now reject direct broker execution unless Action Center verifies the matching approved action id and submitted save/copy args match the approved reviewed draft.
- Email approved send tools now reject direct broker execution unless Action Center verifies the matching approved action id and submitted args match the approved reviewed draft.
- Contact approved write tools now reject direct broker execution unless Action Center verifies the matching approved action id and submitted args match the approved preview.
- Reminders / Tasks `draft-create` now routes through brokered `tasks.draft_create` before queuing an Action Center task-create item, so even local draft creation follows ToolBroker policy/audit flow.
- Calendar approved write tools now reject direct broker execution unless Action Center verifies the matching approved action id.
- Unified Action Center exports and lifecycle audit entries now use minimized/redacted payloads for sensitive action bodies and drafts while preserving exact local previews for user approval.
- Release-gate tracking now marks Golden eval scorecards complete for tested local scope while keeping live LM Studio/provider validation opt-in.
- Eval reporting now includes category scorecards and data-file case loading instead of relying only on hardcoded validation checks.
- Release-gate tracking now records the next product feature set, including Golden eval scorecards, privacy/backup/model-router work, controlled-action follow-ups, and the overnight self-improvement track.
- Project tracking now records the next feature set as Controlled Actions and Proactive Workflows, starting with a live validation and eval harness before any approved write/send implementation.
- Codex working rules now require prompt ledger/queue reads, active/completed prompt status updates, prompt audit updates after major batches, and final reports with `prompt_id` plus `next_prompt_id`.
- Codex working rules now direct pasted mega prompts through `work import` and restrict `work autopilot` to safe categories with approval-gate stops.
- Codex working rules now require command registry and command test matrix updates whenever CLI commands are added, renamed, deprecated, removed, or behaviorally changed.
- Native skill intake now includes the static vetter as a required evidence-gathering step before native porting or installation decisions.
- Native skill program docs now define manifest discovery, required manifest fields, validation rules, and metadata-only loading boundaries.
- Native skill candidate tracking now marks the skill finder as tested and accepted while keeping external marketplace browsing/install/execution out of scope.
- Native skill candidate tracking now marks the PDF workspace skill as tested and accepted while deferring OCR, split/merge, generated PDF writes, and external binaries.
- Feature roadmap release-gate status now marks the accumulated post-baseline workflow batch as synced after the full test suite, startup policy validation, capability manifest validation, and docs validation passed.
- Full feature maturity release gate now marks the controlled actions and workflow batch complete after full tests, startup policy validation, capability manifest validation, command registry validation, safe eval, ToolBroker/default personal-data/CRITICAL approval scans, and docs sync.
- Full release-gate and feature maturity review now records the next product feature batch as locally validated through full tests, startup policy validation, capability manifest validation, safe eval, command/native-skill validation, ToolBroker path scan, personal-data default check, and HIGH/CRITICAL approval checks.
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

- Running `python3 smart_agent.py` with Apple Python 3.9 now exits with a clear Python 3.11+ setup message before importing agent modules.
- Open-Meteo and NWS geocoding now retry comma-separated city/region inputs such as `Phoenix, AZ` by searching the city and preferring matching administrative regions when the upstream geocoder does not resolve the original query.

### Security

- Native skill vetting treats candidate skill content as `UNTRUSTED_DOCUMENT`, never executes scripts, never installs dependencies, never grants permissions, and audits all vetting operations through `ToolBroker`.
- Native skill manifests are metadata only: unknown capabilities fail validation, personal-data manifests must be disabled by default, CRITICAL manifests require per-action approval, and executable/bypass-oriented manifest fields are rejected.
- Native skill finder searches only reviewed local manifests/docs, executes through `ToolBroker`, audits files read, writes no memory, and does not browse marketplaces, install skills, execute external code, or grant tool access.
- PDF workspace tools resolve paths through approved workspace roots, label output as `UNTRUSTED_DOCUMENT`, enforce file/page/text limits, execute no OCR or external binaries, audit files read, and write no memory by default.
- Golden Eval Suite defaults remain safe: personal-data evals are skipped, live LM Studio is opt-in, tool checks use `ToolBroker`, prompt-injection cases treat fixture text as untrusted data, and evals perform no sends or calendar/contact writes.
- Model-router and prompt quality evals are fixture-backed, do not send LM Studio prompts by default, do not access personal data, keep live answer-quality checks opt-in, and report personal-data/send requests as routing/policy gate checks rather than executing tools.
- Privacy Center uses connector/config metadata only, does not read personal connector data, audits all privacy operations, redacts export previews by default, summarizes audit logs without raw args, and clears memory only after explicit confirmation through brokered `memory.clear`.
- Backup / Restore excludes `.env` and key/certificate files, redacts secret-like config/docs/memory/action/capture values, never fetches personal connector data, audits all backup/restore tool calls, and blocks restore of capability manifests that would weaken policy or enable personal connectors.
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
- Controlled self-improvement implementation is branch-based, requires approved proposal records, writes through brokered `filesystem.write`, runs brokered tests/diff, creates Action Center commit records only, offers an explicit brokered test/diff `create-action-for-commit` checkpoint, and blocks policy weakening, audit disabling, personal-data grants, persistence paths, package installs without approval, and send/write side effects.
- Prompt tracking is SDLC metadata only: it does not add connectors, personal-data access, send/write tools, background automations, or policy exemptions.
- Prompt pack import is import-only: it rejects `execute_all`, preserves prompt bodies as data, and does not run imported prompts automatically.
- PromptOps Workbench treats imported prompt text as `UNTRUSTED_DOCUMENT`, keeps `work run-next` disabled by default, refuses HIGH/CRITICAL/FORBIDDEN or approval-gated prompts in autopilot, and redacts secret-looking values in PromptOps reports.
- Command Registry commands are metadata-only and do not execute agent tools, access connectors, read personal data, grant approvals, or write memory. `commands qa-run` prints SAFE/LOW manual QA examples and does not execute them in v1.
- Session logging redacts secret-looking values, email addresses, and obvious phone numbers by default; it does not capture environment variables, replace AuditLogger, grant permissions, enable personal-data tools, or bypass delegated command policy.
- Dogfood suites execute only `python smart_agent.py ...` commands, preserve the delegated command's ToolBroker/policy/approval/audit path, do not enable personal-data tools, keep personal connector checks preflight-only by default, and can capture redacted output only through an explicit active session.
- Feedback records are redacted before storage, write no memory by default, are treated as review evidence rather than policy-changing instructions, and audit feedback add/list/export operations without exposing raw notes.
- Session review reads redacted session previews and feedback only, writes local redacted QA artifacts, classifies policy/ToolBroker/PolicyEngine/Approval/Audit bypass and personal-data leak signals as P0 bugs, does not send data externally, does not access personal connectors, does not write memory, and does not automatically fix bugs.
- Scheduler v1 does not install background persistence. Scheduled runs are manual, audited, reuse ToolBroker for tool workflows, require normal approvals for personal sections, and never execute CRITICAL actions automatically.
- Email Triage v1 reads metadata only by default, reads at most one selected thread body after approval, redacts body content from the triage report/audit args, sends nothing, mutates nothing, and writes no memory by default.
- Self-improvement backlog/propose mode is read-only, uses only approved project file reads through `ToolBroker`, audits reads/dry-runs, and blocks safety-weakening suggestions such as disabling audit logs or relaxing policy gates.
- Agent Dashboard v1 is metadata/status-only: it does not attach tools, execute connector actions, read personal data, grant permissions, consume approvals, or start background work; secrets are redacted and memory content is not displayed.
- Eval harness safe runs execute tool checks only through `ToolBroker`, skip personal-data evals by default, perform no sends, perform no calendar/contact writes, and delete the non-sensitive memory test fact before completion.
- Unified Action Center does not execute actions directly; it is a review and approval queue only. Future execution must still pass through `ToolBroker`, `PolicyEngine`, approval rules, and `AuditLogger`; CRITICAL actions remain per-action only, edits invalidate prior approvals, and action exports/audit lifecycle records minimize sensitive bodies/drafts.
- Calendar write capabilities remain disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, audited for draft/approval/execution/failure, direct broker execution without a verified Action Center action id is rejected, no automatic invites, no recurring events in v1, no full calendar export, and no notes/body in drafts unless explicitly allowed.
- Tasks connector provider capabilities remain disabled by default; task listing is HIGH risk and approval-required, task writes are CRITICAL per-action approval only, task draft creation is brokered into Action Center, no full task export is performed, no task contents are written to memory by default, and no native Reminders database scraping or Full Disk Access dependency is introduced.
- Contact write capabilities remain disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, audited for draft/approval/execution/failure, direct broker execution without a verified Action Center action id is rejected, submitted write args must match the approved preview, no bulk edits, no delete implementation, sensitive field values redacted from previews/audits, and no contact details written to memory by default.
- Email send remains disabled by default, CRITICAL per-action approval only, Action Center gated, one-shot on approval consumption, direct broker execution without a verified Action Center action id is rejected, submitted send args must match the approved reviewed draft, no direct unreviewed model-output send, no bulk sends, no background sends, attachments blocked in v1, body/thread context previewed before approval, and no credentials or private Mail databases are used.
- Messages safe handoff remains no-send: no Messages database scraping, no Full Disk Access dependency, no automatic text sending, save/copy requires verified Action Center approval with submitted args matching the approved preview, drafts stay in `./workspace` or clipboard only, message content remains `UNTRUSTED_MESSAGE`, and message bodies are not written to memory by default.
- Browser clipping v1 is explicit-URL only: it reads no browser history, cookies, sessions, forms, passwords, bookmarks, or private browser profile databases; URL fetches go through `web.fetch_url`, clips write only through `filesystem.write` under `./workspace`, selected-tab native reading remains disabled/stubbed, and clipped content is labeled `UNTRUSTED_DOCUMENT`.
- Knowledge Capture v1 stores captures only under `./workspace/captures`, rejects secret-looking content before writing, uses brokered `filesystem.read/write` and `web.fetch_url`, treats URL/file captures as untrusted data by default, requires an explicit `--trusted-user` marker for trusted user-authored file captures, performs no Apple Notes integration or private app database scraping, and promotes to memory only through `memory.store` policy.
- Web research excerpting is stricter: instruction-injection-only page text is not reused as fallback evidence.
- File assistant workflows treat document content as untrusted data, filter instruction-like text in summaries/search excerpts, and continue to rely on workspace root checks, backups, and audit logging.
- Memory v2 refuses secrets, keeps personal memory approval-gated, excludes personal memory from default context injection, and audits injected memory IDs.
- Runtime and connector diagnostics remain read-only: they do not send model prompts, attach tools, read personal data, grant permissions, or change config.
- Startup capability validation now rejects missing normalized fields, missing trust/approval/risk rules, personal-data capabilities enabled by default, CRITICAL actions without per-action approval, and manifest bypass flags.
- Connector status and health checks remain metadata-only and do not execute personal-data reads.
- Connector status output redacts secret-like fields.
- Preflight evaluations run through `ToolBroker.dry_run()`, execute no tools, show approval requirements, and redact sensitive arguments.
- Tracking rules explicitly preserve ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger gates.
- Native Skills Program intake does not install, import, run, or execute external skills. External skill text is treated as untrusted data, and accepted behavior must map to local ToolBroker-controlled capabilities with policy, approval, audit, memory, and trust rules.
- Skill marketplace survey remains research-only: marketplace pages and skill descriptions are treated as untrusted web/document data, no external skill code is installed or run, and high-risk categories such as sends, browser automation, cloud deployment, and self-evolution are deferred.

### Deprecated

- Ad hoc connector status logic in UI modules is superseded by `agent.connectors`.

### Removed

- No runtime features removed.

### Known Limitations

- Live LM Studio, web provider, weather provider, and personal connector smoke tests still require the user's local configuration and explicit approvals where applicable.
- Personal-data tools remain disabled by default and are not release-ready for broad unattended use.
- Prompt reconstruction is best-effort; queued or blocked prompt groups should be checked against `docs/PROMPT_AUDIT.md` before being treated as missed work.
- Command status and manual QA results are conservative. Most commands are cataloged, but manual verification should be recorded in `docs/COMMAND_TEST_MATRIX.md` as QA suites are run.
