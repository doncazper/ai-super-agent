# Project State

This is the durable resume file for Codex runs in this repository. Read it before making changes and update it before ending a run.

## Purpose

Build a local Mac AI agent with safety-first governance, ToolBroker-only tool execution, explicit policy/permission/approval/audit controls, and resumable SDLC documentation.

## Current Overall Phase

Post-baseline hardening and roadmap reset after M0-M11 and the first real connector pattern.

## Current Batch

Controlled actions and workflow feature-batch release gate.

## Current Task

Full feature maturity review and release gate.

## Current Status

complete

## Current Branch

`main`

## Last Known Good Commit

`fcfd68c Prepare post-connector feature batch` before this large working-tree release commit.

## Last Test Result

Full suite: 529 passed in 10.23s. Startup policy ok. Capability manifest ok (59 capabilities). Command registry validation ok (154 commands). Safe eval suite passed with 9 pass, 0 fail, 8 skipped by design. Personal-data tools enabled by default: none. CRITICAL approval reuse violations: none.

## Startup Policy Status

startup policy ok.

## Prompt Tracking

- active_prompt_id: none
- next_prompt_id: NATIVE-SKILLS-FOUNDATION
- active_prompt_pack: none
- prompt_queue_status: Full feature maturity review is complete; next queued prompt is `NATIVE-SKILLS-FOUNDATION`.
- last_prompt_audit_result: 90 prompt records known; 53 definitely complete, 34 queued, 3 blocked, 0 active, next prompt `NATIVE-SKILLS-FOUNDATION`.

## Last Updated Timestamp

2026-05-23 00:20 PDT

## Last Completed Work

- Full feature maturity review and release gate completed.
- Full test suite passed: 529 passed in 10.23s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Command registry validation passed: 154 commands, no missing registry/matrix ids, no invalid records.
- Safe eval suite passed: 9 passed, 0 failed, 8 skipped by design. LM Studio live evals skipped because `LMSTUDIO_MODEL` was not set; personal-data evals skipped by default.
- Release gate found and fixed Open-Meteo live geocoding for comma-separated U.S. city/state inputs such as `Phoenix, AZ`; added a mocked regression test.
- ToolBroker-bypass scan found provider calls contained inside registered tool providers/workflow broker paths, with user-facing workflows still using `ToolBroker`.
- Personal-data tools remain disabled by default.
- HIGH actions remain approval-required.
- CRITICAL actions remain per-action approval only with no approval reuse.
- Command registry validation found no undocumented command drift.
- `docs/FEATURE_MATURITY.md` now has a `Next Work-Up Candidates` section.
- `FULL-FEATURE-MATURITY-REVIEW` is marked complete; next queued prompt is `NATIVE-SKILLS-FOUNDATION`.
- Scheduler / Automation v1 implemented in the working tree.
- Added `agent/workflows/scheduler.py`.
- Added `python smart_agent.py schedule list`.
- Added `python smart_agent.py schedule create`.
- Added `python smart_agent.py schedule run <schedule_id>`.
- Added `python smart_agent.py schedule pause <schedule_id>`.
- Added `python smart_agent.py schedule delete <schedule_id>`.
- Supported scheduled workflows in v1:
  - `daily_briefing`
  - `connector_doctor`
  - `eval_safe`
  - `memory_cleanup`
  - `audit_summary`
- Scheduler v1 is manual-run only and creates no LaunchAgent, cron job, daemon, login item, or hidden background persistence.
- Schedule records are stored locally in JSON at `data/schedules.json` by default; tests and advanced usage can set `SCHEDULE_PATH`.
- Schedule lifecycle events and scheduled run start/finish events are audited.
- Scheduled tool workflows still use `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Personal Daily Briefing sections remain approval-gated and are not read when approval is unavailable.
- Unsupported workflows, including direct send/write/CRITICAL action workflows, are rejected.
- `memory_cleanup` is intentionally conservative in v1 and does not delete memory automatically.
- Added `docs/SCHEDULER.md`.
- Scheduler focused tests passed: 7 passed in 0.47s.
- Scheduler/prompt/registry/maturity focused tests passed: 25 passed in 0.45s.
- Full suite passed: 528 passed in 10.76s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Command registry validation passed: 154 commands, no missing records.
- Diff whitespace check passed.
- Command Registry + Manual QA System implemented in the working tree.
- Added a durable command catalog with 150 command records across core runtime, diagnostics, connectors, approvals, Action Center, weather, web/research, workspace files, memory, personal modules, workflows, PromptOps, quality/evals, planned groups, legacy commands, and blocked commands.
- Added `docs/COMMAND_REGISTRY.md`.
- Added `docs/COMMAND_TEST_MATRIX.md`.
- Added `docs/COMMAND_LEGACY.md`.
- Added `docs/COMMAND_QA_RUNBOOK.md`.
- Added `docs/templates/command_record_template.md`.
- Added `docs/templates/command_test_record_template.md`.
- Added `python smart_agent.py commands list`.
- Added `python smart_agent.py commands show <command_id>`.
- Added `python smart_agent.py commands search "<query>"`.
- Added `python smart_agent.py commands legacy`.
- Added `python smart_agent.py commands deprecated`.
- Added `python smart_agent.py commands validate`.
- Added `python smart_agent.py commands qa-plan`.
- Added `python smart_agent.py commands qa-run <group>`.
- Command registry validation passes locally and checks command docs, matrix coverage, metadata completeness, README links, and AGENTS command-registry rules.
- `commands qa-run` is intentionally non-executing in v1; it prints SAFE/LOW manual QA examples for the requested group.
- Manual QA results remain pending for most commands and should be logged in `docs/COMMAND_TEST_MATRIX.md` as suites are run.
- Command status counts: 129 active, 10 planned, 4 experimental, 4 stubbed, 2 legacy, 1 blocked, 0 deprecated, 0 removed.
- Command registry focused tests passed: 13 passed in 0.11s.
- Full suite passed: 521 passed in 10.74s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Diff whitespace check passed.
- PromptOps Workbench v1 implemented in the working tree.
- Added `agent/promptops/` modules for import, clipboard, workbench, runner, state, safety, reports, and models.
- Added `python smart_agent.py work import <file>`.
- Added `python smart_agent.py work import --stdin`.
- Added `python smart_agent.py work import-clipboard`.
- Added `python smart_agent.py work next`, `show-next`, `copy-next`, `resume`, `status`, `review`, and `audit`.
- Added `python smart_agent.py work mark-active`, `mark-complete`, and `mark-failed`.
- Added disabled-by-default `python smart_agent.py work run-next`.
- Added safe-only `python smart_agent.py work autopilot --safe-only --max-prompts N`.
- Added `docs/PROMPTOPS_WORKBENCH.md` and `docs/templates/promptops_run_report_template.md`.
- PromptOps imports prompt packs or raw single prompts, updates prompt ledger/queue/audit/project state, and does not execute imported prompts automatically.
- Imported prompt text is labeled `UNTRUSTED_DOCUMENT`.
- Runner execution requires `CODEX_RUNNER_ENABLED=true`; default behavior writes a safe report instead of running Codex.
- Autopilot refuses HIGH/CRITICAL/FORBIDDEN risk prompts, approval-gated prompts, and forbidden categories.
- PromptOps focused prompt/docs tests passed: 41 passed in 0.32s.
- Full suite passed: 516 passed in 10.91s.
- Startup policy validation passed: startup policy ok.
- Capability manifest validation passed: capability manifest ok (59 capabilities).
- Diff whitespace check passed.
- Prompt Pack import/splitting support is complete.
- Added `agent/prompts/pack_models.py`, `pack_parser.py`, `pack_validator.py`, `prompt_store.py`, `prompt_queue.py`, and `prompt_audit.py`.
- Added `docs/PROMPT_PACK_FORMAT.md` and `docs/templates/prompt_pack_template.md`.
- Added `python smart_agent.py prompts validate-pack <pack_file>`.
- Added `python smart_agent.py prompts import <pack_file>`.
- Added `python smart_agent.py prompts split <pack_file>`.
- Added `python smart_agent.py prompts mark-superseded <prompt_id> --by <replacement_id>`.
- Prompt packs are validation-first, import-only, split into `prompts/queued/`, and never executed automatically.
- Prompt Ledger and Prompt Queue tracking is in progress.
- Added `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and `docs/PROMPT_AUDIT.md`.
- Added prompt record directories under `prompts/queued`, `prompts/active`, `prompts/completed`, `prompts/skipped`, `prompts/failed`, and `prompts/superseded`.
- Added `docs/templates/prompt_record_template.md`.
- Added `python smart_agent.py prompts list/next/show/add/mark-active/mark-complete/mark-skipped/mark-failed/audit/missing`.
- Reconstructed prompt evidence for baseline, weather, connector, workflow, controlled-action, and self-improvement batches.
- Queued the next important prompt groups beginning with `NATIVE-SKILLS-FOUNDATION`.
- Controlled Self-Improvement Implementation Loop v1 implemented in the working tree.
- Added `python smart_agent.py improve implement <proposal_id>`.
- Added `python smart_agent.py improve run-tests`.
- Added `python smart_agent.py improve show-diff`.
- Added `python smart_agent.py improve commit --from-action <action_id>`.
- Implementation requires an approved proposal record in `data/self_improvement/approved_proposals.json`.
- Implementation creates/switches to a `codex/` branch.
- Approved file writes go through brokered `filesystem.write`.
- Tests and diff go through brokered `code.run_tests` and `git.diff`.
- Commit is queued as an Action Center `self_improvement.commit` record and does not execute until approved.
- Protected safety file edits, policy weakening, audit disabling, personal-data grants, persistence paths, and package installs without approval are blocked.
- Controlled self-improvement focused tests passed: 21 passed in 2.34s.
- Personal Task Extraction v1 implemented in the working tree.
- Added `python smart_agent.py tasks extract --from-notes ./workspace/notes.md`.
- Added `python smart_agent.py tasks extract --from-email-thread <thread_id>`.
- Added `python smart_agent.py tasks extract --from-meeting <event_id>`.
- Added `python smart_agent.py tasks extract --from-url <url>`.
- Added `python smart_agent.py tasks extract --from-capture ./workspace/captures/<file>.json`.
- Added `python smart_agent.py tasks extract --dry-run`.
- Each source is read through existing brokered tools/connectors.
- Email/calendar personal sources remain approval-gated.
- Extracted task candidates become pending Action Center `tasks.create` records only.
- No task creation, writes/sends, contact edits, or memory writes execute in the extraction workflow.
- Untrusted source instruction lines are filtered before task extraction.
- Personal Task Extraction focused workflow tests passed: 70 passed in 1.45s.
- Meeting Follow-Up v1 implemented in the working tree.
- Added `python smart_agent.py meeting follow-up --event-id <event_id>`.
- Added `python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md`.
- Added `python smart_agent.py meeting follow-up --dry-run`.
- Added optional `--contact` and `--json` support.
- Selected calendar event reads remain approval-gated through `calendar.read_selected_event`.
- Meeting notes are read only through brokered `filesystem.read` and workspace path policy.
- Notes content is treated as `UNTRUSTED_DOCUMENT`; instruction-injection lines are filtered before synthesis.
- Suggested tasks, email sends, and calendar updates create pending Action Center records only.
- No email send, calendar write, task creation, contact edit, or memory write executes in the workflow.
- Meeting Follow-Up focused workflow tests passed: 61 passed in 1.01s.
- Full suite passed: 465 passed in 8.59s.
- Startup policy, capability manifest validation, docs validation, and diff whitespace check passed.
- Daily Briefing v2 implemented in the working tree.
- Added configurable opt-in sections for weather, calendar selected date range, tasks/reminders, email metadata only, web topics, memory preferences, and suggested Action Center actions.
- Added `python smart_agent.py briefing daily --sections weather,calendar,tasks,email,web,memory,suggested_actions`.
- Added `python smart_agent.py briefing config show`.
- Added `python smart_agent.py briefing config set sections=... weather_location=... web_topics=...`.
- Personal-data sections remain HIGH risk and require approval; denied or unavailable sections are skipped independently and reported in the final briefing.
- Email bodies and messages are not read.
- No writes/sends execute from the briefing; suggested actions create pending Action Center items only.
- No memory writes occur by default; the memory section reads non-personal preference records only.
- Dry-run shows planned tool calls and approvals without executing tools.
- Daily Briefing v2 focused workflow tests passed: 51 passed in 0.53s.
- Notes / Knowledge Capture v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py capture note "text"`.
- Added `python smart_agent.py capture from-file <path>`.
- Added `python smart_agent.py capture from-url <url>`.
- Added `python smart_agent.py capture list`.
- Added `python smart_agent.py capture summarize`.
- Added `python smart_agent.py capture promote-to-memory <capture_id>`.
- Captures are stored as JSON files under `./workspace/captures` through brokered `filesystem.write`.
- Source files are read through brokered `filesystem.read`.
- URLs are fetched through brokered `web.fetch_url`.
- Web captures remain `UNTRUSTED_WEB`; file captures remain `UNTRUSTED_DOCUMENT`; note captures are `TRUSTED_USER`.
- Secrets are rejected before capture writes.
- Apple Notes integration, private app database scraping, and personal-data connector access were not added.
- Memory promotion calls brokered `memory.store`; personal-looking content is blocked by default before memory storage.
- Browser selected URL and clipping v1 completed and locally release-gated in the working tree.
- Added `docs/decisions/browser_selected_tab_clipping.md`.
- Added `python smart_agent.py browser read-url "<url>"`.
- Added `python smart_agent.py browser summarize-url "<url>"`.
- Added `python smart_agent.py browser clip-url "<url>" --to workspace`.
- Added `python smart_agent.py browser selected-tab` as a clear unavailable/stubbed selected-tab path.
- URL read and summarize workflows fetch only explicit public URLs through brokered `web.fetch_url`.
- URL clips fetch through brokered `web.fetch_url` and write only under `./workspace` through brokered `filesystem.write`.
- Fetched page content remains `UNTRUSTED_WEB`; saved clips are labeled `UNTRUSTED_DOCUMENT`.
- The connector does not read browser history, cookies, sessions, forms, passwords, bookmarks, or private browser profile databases.
- No browser automation, form submission, cookie/session scraping, password manager access, or native selected-tab integration was added.
- Added browser connector status metadata for the explicit URL workflow while keeping native selected-tab disabled/stubbed.
- Messages safe handoff v1 completed and locally release-gated in the working tree.
- Added `docs/decisions/messages_send_path.md`.
- Added `messages.save_draft` and `messages.copy_draft` capabilities, both HIGH risk, disabled by default, approval-required, and no-send.
- Added Action Center handoff records from `python smart_agent.py messages draft-from-text --to "Name" --context-file ./workspace/thread.txt`.
- Added `python smart_agent.py messages save-draft --from-action <action_id>`.
- Added `python smart_agent.py messages copy-draft --from-action <action_id>`.
- Saved message drafts remain inside `./workspace`.
- Clipboard copy uses approval-gated handoff and supports mock mode in tests.
- Automatic text/message sending remains deferred.
- No Messages database scraping, Full Disk Access dependency, AppleScript send automation, Accessibility send automation, or memory storage was added.
- Email approved send v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py email draft-new --to ... --subject ... --body ...`.
- Added Action Center backed `python smart_agent.py email draft-reply <thread_id> --to ... --subject ... --body ...`.
- Added `python smart_agent.py email send --from-action <action_id>`.
- Email send drafts create Action Center records only and do not send.
- Approved email send actions execute once through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Direct `email.send_approved` calls without an Action Center action id are blocked even if an approval manager auto-approves the capability.
- `email.send_approved` remains disabled by default and CRITICAL per-action approval only.
- Preflight previews include from account/provider, to, cc, bcc, subject, full body, attachments, thread/reply context, and rollback impossibility.
- Editing an email send action invalidates prior approval.
- Bulk sends and attachments are blocked in v1.
- The current email send provider is mock-only for tests; real provider integration is deferred.
- Email thread context remains `UNTRUSTED_EMAIL` and cannot approve or instruct sending.
- Email send contents are not written to memory by default.
- Contacts approved edits v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py contacts draft-update <contact_id> --set field=value --old field=value`.
- Added `python smart_agent.py contacts update --from-action <action_id>`.
- Added `python smart_agent.py contacts draft-create --display-name "Name" --field field=value`.
- Added `python smart_agent.py contacts create --from-action <action_id>`.
- Contact update/create drafts create Action Center records only and do not mutate Contacts.app.
- Approved contact update/create actions execute once through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- `contacts.update_selected` and `contacts.create` remain disabled by default and CRITICAL per-action approval only.
- Contact updates require explicit field-level diffs.
- Phone, email, address, and note-like contact values are redacted in persisted previews and audit logs.
- Bulk contact edits are denied.
- Contact deletion remains deferred and unregistered.
- The current contact write connector remains a no-external-change stub; live native Contacts writes are deferred.
- Contact details are not written to memory by default.
- Reminders / Tasks connector v1 completed and locally release-gated in the working tree.
- Added adapter-first personal tasks connector with `NotConfiguredTasksConnector` and `MockTasksConnector`.
- Added brokered `tasks.list`, `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` tools.
- Added `python smart_agent.py tasks list`.
- Added `python smart_agent.py tasks draft-create "task"`.
- Added `python smart_agent.py tasks create --from-action <action_id>`.
- Added `python smart_agent.py tasks complete <task_id>`.
- Added `python smart_agent.py tasks update <task_id>`.
- Added `python smart_agent.py tasks delete <task_id>`.
- Task create drafts create Action Center records only and execute once from approved actions.
- Task listing is HIGH risk and approval-required.
- Task create/update/complete/delete are CRITICAL per-action approval tools.
- Tasks connector is disabled by default, selected-scope, no full export, no memory storage by default, and no native Reminders provider enabled.
- Added Reminders / Tasks connector decision notes.
- Calendar approved writes v1 completed and locally release-gated in the working tree.
- Added `python smart_agent.py calendar draft-create`.
- Added `python smart_agent.py calendar create --from-action <action_id>`.
- Added `python smart_agent.py calendar draft-update <event_id>`.
- Added `python smart_agent.py calendar update --from-action <action_id>`.
- Added `python smart_agent.py calendar draft-delete <event_id>`.
- Added `python smart_agent.py calendar delete --from-action <action_id>`.
- Calendar draft commands create Action Center records only; they do not create, update, delete, invite, export, or store calendar data in memory.
- Calendar `--from-action` commands require an approved Action Center record and execute through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`.
- Calendar approved write actions are consumed once after brokered execution.
- Calendar create/update/delete capabilities remain disabled by default and CRITICAL per-action approval only.
- The current approved write connector remains a no-external-change stub; live native Calendar writes are deferred.
- Notes/body text is omitted from drafts unless `--allow-notes` is explicit.
- Automatic invites and recurring events are not supported in v1.
- Unified Action Center v1 completed in the working tree.
- Added `python smart_agent.py actions list`.
- Added `python smart_agent.py actions show <action_id>`.
- Added `python smart_agent.py actions approve <action_id>`.
- Added `python smart_agent.py actions deny <action_id>`.
- Added `python smart_agent.py actions edit <action_id> key=value`.
- Added `python smart_agent.py actions clear-denied`.
- Added `python smart_agent.py actions export`.
- Added persisted action records in `data/actions.json` with action id, timestamps, status, tool/capability, risk/trust, preview, sanitized args, rollback availability, source workflow, approval state, and audit ids.
- Action Center integrates with `ApprovalStore`/`ApprovalRequest`, redacts previews, records audit lifecycle events, invalidates prior approvals after edits, and enforces one-time approval consumption.
- Action Center does not execute tools directly; any future execution must still go through `ToolBroker`, `PolicyEngine`, approval rules, and `AuditLogger`.
- CRITICAL action records remain per-action only with no approval reuse.
- Non-interactive action execution gates block approval-required pending actions.
- Live validation and eval harness v1 completed in the working tree.
- Added `python smart_agent.py eval list`.
- Added `python smart_agent.py eval run --safe`.
- Added `python smart_agent.py eval run --lmstudio`.
- Added `python smart_agent.py eval run --web`.
- Added `python smart_agent.py eval run --weather`.
- Added `python smart_agent.py eval run --workspace`.
- Added `python smart_agent.py eval run --memory`.
- Added `python smart_agent.py eval report`.
- Eval safe runs cover no-tool LM Studio chat when configured, time tool roundtrip, weather current/forecast when configured, web search/fetch when configured, controlled workspace read/write, non-sensitive memory add/search/delete, dry-run/preflight, and connector doctor checks.
- Personal-data evals for calendar, contacts, email, and messages are skipped by default.
- Eval reports write structured results to `logs/eval_results.json` and Markdown summaries to `docs/EVAL_REPORT.md`.
- Eval tool checks execute through `ToolBroker` and are audited.
- Eval harness performs no sends, no calendar/contact writes, no personal-data reads by default, and no personal memory storage.
- Project tracking and release gate sync completed.
- Confirmed current reported built features are reflected in `CHANGELOG.md`, `docs/FEATURE_REGISTRY.md`, `docs/FEATURE_MATURITY.md`, `docs/FEATURE_ROADMAP.md`, and this project state file.
- Full suite still reports 359 passing tests.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed.
- Confirmed no personal-data tools are enabled by default.
- Confirmed enabled HIGH-risk actions evaluate to approval-required.
- Confirmed CRITICAL capabilities require per-action approval and disallow approval reuse.
- Confirmed unknown capabilities are denied.
- Confirmed the next feature set is queued as controlled actions and proactive workflows, with no runtime feature implementation in this sync.
- Agent Dashboard v1 completed and validated.
- Added `python smart_agent.py dashboard`.
- Added `python smart_agent.py status`.
- Dashboard reports current model/config, LM Studio status, enabled tools, connector status, permissions, pending approvals, recent audit metadata, memory counts, risk settings, last test run, and setup hints.
- Dashboard is metadata/status-only: it does not attach tools, execute connector actions, read personal data, grant permissions, consume approvals, start background actions, write memory, or display memory content.
- Secrets are redacted and personal connectors are displayed from configuration/status metadata only.
- Self-improvement backlog generator completed and validated.
- Added `python smart_agent.py improve backlog`.
- Added `python smart_agent.py improve propose`.
- Backlog/propose mode reads only an approved set of project docs, tests, capability config, self-improvement workflow files, and audit-log paths through brokered `filesystem.read` calls.
- Backlog/propose mode is read-only: no file edits, permission grants, package installs, personal-data access, memory writes, or commits.
- Dry-run mode audits planned file reads without reading file contents.
- Safety-weakening suggestions such as disabling audit logs, relaxing ToolBroker/PolicyEngine gates, or enabling personal-data connectors by default are flagged as blocked.
- Email Triage v1 completed and validated.
- Added `python smart_agent.py email triage` and `python smart_agent.py email triage --selected-thread "<thread_id>"`.
- Email Triage v1 uses metadata only by default, classifies priority from metadata, reads at most one selected thread body after approval, summarizes it, and drafts a reply without sending.
- Selected thread body content remains `UNTRUSTED_EMAIL`, is redacted from triage reports, and is not stored in memory by default.
- Meeting Prep v1 completed and validated.
- Added `python smart_agent.py meeting prep` with selected `--event-id` or `--date` plus `--title`, optional `--contact`, optional `--web-topic`, `--dry-run`, and `--json`.
- Added brokered `calendar.read_selected_event` capability as HIGH risk, disabled by default, approval-required, selected-event only, and no-memory by default.
- Meeting Prep v1 uses only brokered selected calendar event reads, optional approved contact searches, and optional web search; it performs no sends, writes, bulk exports, or memory writes by default.
- Daily Briefing v1 completed and validated.
- Added `python smart_agent.py briefing daily` with optional `--weather`, `--calendar`, `--email-metadata`, `--web-topic`, `--dry-run`, and `--json`.
- Daily Briefing v1 uses only explicitly selected sources through `ToolBroker`; calendar and email metadata are skipped when disabled or unapproved.
- Daily Briefing v1 performs no sends, writes, message reads, email body reads, browser history reads, contact reads, or memory writes by default.
- Messages/text draft-only assistant completed and validated.
- Added explicit `messages.draft_from_text` capability for the workspace-only manual fallback.
- Email metadata + selected-thread + draft-only assistant completed and validated.
- Email metadata and body outputs are labeled `UNTRUSTED_EMAIL`; draft output remains no-send/no-delete/no-move/no-archive.
- Contacts read-only selected-scope connector completed and validated.
- Added contacts contact-text-as-data safety notice and sensitive-field requested/config regression coverage.
- Calendar read-only selected-range connector completed and validated.
- Added calendar event-text-as-data safety notice and regression coverage.
- Personal connector readiness gate completed and validated.
- Added `docs/checklists/personal_connector_readiness.md`.
- Verified ToolBroker, PolicyEngine, approval UI, dry-run/preflight, AuditLogger, secret redaction, connector registry, personal disabled-by-default manifest entries, HIGH/CRITICAL approval rules, untrusted-content wrappers, memory defaults, denial tests, non-interactive approval blocking, and no direct connector calls outside ToolBroker.
- Memory v2 safe context completed and validated.
- Workspace file assistant workflow completed and validated.
- Source-grounded web research hardening completed and validated.
- Approval UI foundation and universal dry-run/preflight mode completed.
- Added prompt-free `preflight` command backed by deterministic routing and `ToolBroker.dry_run()`.
- Runtime doctor + connector dashboard polish completed.
- Durable project tracking files and validation updated.
- Capability manifest normalized and startup validation hardened.
- M0-M11 baseline complete.
- Post-connector release gate passed locally.
- Weather connector pattern completed with Open-Meteo, NWS, WeatherKit stub, safe preferences, caching/rate limiting, alerts, and daily weather briefing.
- Connector framework extraction completed in the working tree and validated with targeted/full tests before this tracking pass.

## Current Work In Progress

None. Prompt Pack import/splitting support is implemented and locally release-gated. The working tree still contains completed but uncommitted connector-framework, tracking-doc, manifest-normalization, diagnostics, approval/preflight, web research, workspace file assistant, Memory v2, personal connector readiness, calendar read-only, contacts read-only, email draft-only, messages draft-only, Daily Briefing v1/v2, Meeting Prep v1, Meeting Follow-Up v1, Personal Task Extraction v1, Email Triage v1, Self-improvement backlog/implementation, Agent Dashboard v1, tracking sync, eval harness, Action Center, calendar approved writes, tasks connector, contacts approved edits, email approved send, messages safe handoff, browser clipping, knowledge capture, prompt tracking, and prompt pack import changes.

## Files Being Changed

- `agent/ui/prompts.py`
- `agent/prompts/__init__.py`
- `agent/prompts/pack_models.py`
- `agent/prompts/pack_parser.py`
- `agent/prompts/pack_validator.py`
- `agent/prompts/prompt_store.py`
- `agent/prompts/prompt_queue.py`
- `agent/prompts/prompt_audit.py`
- `agent/ui/cli_commands.py`
- `tests/test_prompt_pack.py`
- `tests/test_prompt_tracking.py`
- `tests/test_feature_maturity_docs.py`
- `docs/PROMPT_PACK_FORMAT.md`
- `docs/PROMPT_LEDGER.md`
- `docs/PROMPT_QUEUE.md`
- `docs/PROMPT_AUDIT.md`
- `docs/templates/prompt_record_template.md`
- `docs/templates/prompt_pack_template.md`
- `prompts/completed/PROMPT-PACK-IMPORT.md`
- `prompts/completed/PROMPT-LEDGER-QUEUE.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/COMPLETION_REPORT.md`
- `docs/PROJECT_STATE.md`
- `agent/tools/personal/tasks.py`
- `agent/workflows/tasks.py`
- `tests/test_tasks_connector.py`
- `agent/workflows/contact_edits.py`
- `agent/safety/contact_redaction.py`
- `tests/test_contacts_approved_edits.py`
- `agent/workflows/email_sends.py`
- `tests/test_email_approved_send.py`
- `agent/workflows/daily_briefing.py`
- `smart_agent.py`
- `tests/test_workflows.py`
- `README.md`
- `CHANGELOG.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/FEATURE_MATURITY.md`
- `docs/COMPLETION_REPORT.md`
- `docs/PROJECT_STATE.md`
- `agent/workflows/message_handoff.py`
- `agent/workflows/browser_clipping.py`
- `agent/workflows/knowledge_capture.py`
- `agent/workflows/meeting_followup.py`
- `agent/workflows/task_extraction.py`
- `agent/workflows/self_improvement_loop.py`
- `docs/decisions/browser_selected_tab_clipping.md`
- `tests/test_browser_clipping.py`
- `tests/test_knowledge_capture.py`
- `tests/test_messages_safe_handoff.py`
- `docs/decisions/messages_send_path.md`
- `docs/decisions/2026-05-22_reminders_tasks_connector.md`
- `agent/tools/personal/read_only.py`
- `agent/tools/registry.py`
- `agent/config/schema.py`
- `agent/safety/actions.py`
- `agent/core/tool_broker.py`
- `agent/connectors/registry.py`
- `tests/test_connector_framework.py`
- `tests/test_connectors.py`
- `config/capabilities.yaml`
- `agent/workflows/calendar_writes.py`
- `agent/tools/personal/write_actions.py`
- `smart_agent.py`
- `tests/test_calendar_approved_writes.py`
- `agent/safety/actions.py`
- `agent/safety/action_preview.py`
- `agent/ui/cli_commands.py`
- `tests/test_action_center.py`
- `README.md`
- `CHANGELOG.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/FEATURE_MATURITY.md`
- `docs/PROJECT_STATE.md`
- `docs/COMPLETION_REPORT.md`
- `agent/ui/evals.py`
- `agent/ui/cli_commands.py`
- `tests/test_eval_harness.py`
- `docs/EVAL_REPORT.md`
- `README.md`
- `CHANGELOG.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/FEATURE_MATURITY.md`
- `docs/PROJECT_STATE.md`
- `docs/COMPLETION_REPORT.md`
- `docs/PROJECT_STATE.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_MATURITY.md`
- `docs/COMPLETION_REPORT.md`
- `CHANGELOG.md`
- `AGENTS.md`
- `CHANGELOG.md`
- `docs/FEATURE_REGISTRY.md`
- `docs/FEATURE_ROADMAP.md`
- `docs/PROJECT_STATE.md`
- `docs/templates/feature_record_template.md`
- `docs/templates/changelog_entry_template.md`
- `docs/templates/project_state_update_template.md`
- `docs/COMPLETION_REPORT.md`
- `docs/checklists/personal_connector_readiness.md`
- `docs/RELEASE_CHECKLIST.md`
- `tests/test_feature_maturity_docs.py`
- `config/capabilities.yaml`
- `agent/config/schema.py`
- `tests/test_policy.py`
- `docs/SDLC.md`
- `docs/TEST_PLAN.md`
- `agent/ui/doctor.py`
- `agent/ui/dashboard.py`
- `agent/connectors/base.py`
- `agent/connectors/status.py`
- `tests/test_ux_packaging.py`
- `tests/test_connectors.py`
- `agent/tools/registry.py`
- `agent/ui/cli_commands.py`
- `agent/ui/preflight.py`
- `tests/test_preflight.py`
- `docs/THREAT_MODEL.md`
- `agent/workflows/research.py`
- `agent/workflows/daily_briefing.py`
- `agent/workflows/meeting_prep.py`
- `agent/workflows/email_triage.py`
- `agent/workflows/self_improvement_backlog.py`
- `tests/test_workflows.py`
- `tests/test_self_improvement.py`
- `docs/RISK_REGISTER.md`
- `agent/tools/low_risk/workspace_files.py`
- `agent/workflows/files.py`
- `smart_agent.py`
- `tests/test_files_workflow.py`
- `agent/memory/persistent_memory.py`
- `agent/memory/search.py`
- `agent/memory/context.py`
- `agent/memory/tools.py`
- `tests/test_memory.py`
- `agent/tools/personal/calendar.py`
- `agent/tools/personal/contacts.py`
- `agent/tools/personal/email.py`
- `agent/tools/personal/messages.py`
- `agent/tools/personal/read_only.py`
- `tests/test_personal_modules.py`

Existing uncommitted connector-framework files are also present from the previous completed task:

- `agent/connectors/*`
- `agent/ui/connectors.py`
- `tests/test_connector_framework.py`
- related docs touched by that task

## Commands Run

- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' smart_agent.py`
- `rg -n "subparsers|add_parser|def _run|prompts|dashboard|memory|improve" smart_agent.py agent/ui tests docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `sed -n '1,360p' agent/ui/cli_commands.py`
- `sed -n '1,220p' CHANGELOG.md`
- `sed -n '1,160p' docs/FEATURE_REGISTRY.md`
- `sed -n '1,170p' docs/FEATURE_MATURITY.md`
- `sed -n '1,220p' tests/test_feature_maturity_docs.py`
- `sed -n '1,180p' docs/TEST_PLAN.md`
- `sed -n '1,140p' docs/RISK_REGISTER.md`
- `sed -n '1,160p' docs/THREAT_MODEL.md`
- `sed -n '1,160p' docs/RELEASE_CHECKLIST.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts next`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- Startup policy and capability manifest validation.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts audit`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_prompt_pack.py tests/test_prompt_tracking.py tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- Startup policy and capability manifest validation after prompt pack support.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py prompts audit`
- `git diff --check`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' agent/tools/personal/read_only.py && sed -n '1,220p' agent/tools/personal/write_actions.py`
- `sed -n '1,260p' agent/tools/registry.py && rg -n "tasks\\.|reminders|Reminder|Task" agent tests config docs README.md -g '*.py' -g '*.yaml' -g '*.md'`
- `sed -n '820,1040p' smart_agent.py`
- `sed -n '1,180p' agent/config/schema.py && sed -n '1180,1385p' config/capabilities.yaml`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_tasks_connector.py -q; else python3 -m pytest tests/test_tasks_connector.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py tasks draft-create "Follow up with Alex" --source-workflow meeting_prep | head -80; else python3 smart_agent.py tasks draft-create "Follow up with Alex" --source-workflow meeting_prep | head -80; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_tasks_connector.py tests/test_connector_framework.py::test_connector_registry_loads tests/test_connectors.py::test_connectors_cli_list -q; else python3 -m pytest tests/test_tasks_connector.py tests/test_connector_framework.py::test_connector_registry_loads tests/test_connectors.py::test_connectors_cli_list -q; fi`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `sed -n '1,420p' agent/tools/personal/calendar.py`
- `sed -n '1,180p' agent/tools/personal/write_actions.py`
- `sed -n '1,620p' agent/core/tool_broker.py`
- `rg -n "def _run_calendar|calendar draft|calendar create|calendar update|calendar delete|calendar\\.create_event|write_actions" smart_agent.py agent tests -g '*.py'`
- `sed -n '700,840p' smart_agent.py`
- `sed -n '1,160p' tests/test_approved_write_actions.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_calendar_approved_writes.py -q; else python3 -m pytest tests/test_calendar_approved_writes.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py calendar draft-create --title "Test" --start 2026-05-23T10:00 --end 2026-05-23T10:30 | head -80; else python3 smart_agent.py calendar draft-create --title "Test" --start 2026-05-23T10:00 --end 2026-05-23T10:30 | head -80; fi`
- `git status --short data logs | cat`
- `pwd && git status --short && git branch --show-current`
- `rg -n "calendar\\.create_event|contacts\\.update_selected|email\\.send_approved|messages\\.send_approved|filesystem\\.delete|git\\.commit|memory\\.(store_personal|write_personal)|self_improvement\\.commit" config/capabilities.yaml agent tests docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md README.md`
- `sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/safety/action_preview.py`
- `sed -n '1,320p' agent/ui/cli_commands.py`
- `sed -n '1,220p' agent/safety/audit.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_action_center.py -q; else python3 -m pytest tests/test_action_center.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest -q; else python3 -m pytest -q; fi`
- Startup policy validation via `validate_startup_policy('config/capabilities.yaml')`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_feature_maturity_docs.py -q; else python3 -m pytest tests/test_feature_maturity_docs.py -q; fi`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" smart_agent.py actions list | head -80; else python3 smart_agent.py actions list | head -80; fi`
- `rg -n "direct|ToolBroker|execute\\(|ActionCenter|action\\." agent/safety/actions.py agent/ui/cli_commands.py tests/test_action_center.py`
- `date '+%Y-%m-%d %H:%M %Z'`
- `git status --short --branch`
- `git log --oneline -5`
- `date '+%Y-%m-%d %H:%M %Z'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest -q; else python3 -m pytest -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... validate_startup_policy('config/capabilities.yaml') ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')) ... PY`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ -x "$PY" ]; then "$PY" -m pytest tests/test_feature_maturity_docs.py -q; else python3 -m pytest tests/test_feature_maturity_docs.py -q; fi`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY=python3; fi; "$PY" - <<'PY' ... PolicyEngine invariant checks ... PY`
- `rg -n "LM Studio|Qwopus|no-tool|deterministic router|ToolBroker|PolicyEngine|PermissionManager|ApprovalManager|AuditLogger|preflight|doctor|connector framework|Agent Dashboard|Open-Meteo|NWS|WeatherKit|web search|Workspace file|Memory v2|Calendar read-only|Contacts read-only|Email Triage|Meeting Prep|Daily Briefing|self-improvement backlog" CHANGELOG.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/PROJECT_STATE.md docs/FEATURE_ROADMAP.md`
- `sed -n '1,260p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' CHANGELOG.md`
- `git diff --check`
- `rg -n "subprocess|os\\.system|Popen|requests\\.|urllib|open\\(|sqlite3|~/Library|Library/Messages|Library/Mail|Keychains|execute\\(" agent smart_agent.py -g '*.py'`
- `sed -n '1,220p' docs/FEATURE_REGISTRY.md && sed -n '70,160p' docs/FEATURE_MATURITY.md && sed -n '1,180p' docs/FEATURE_ROADMAP.md`
- `sed -n '1,220p' SPEC.md && sed -n '1,220p' AGENTS.md && sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' docs/FEATURE_ROADMAP.md && sed -n '1,120p' docs/FEATURE_REGISTRY.md && tail -n 120 docs/COMPLETION_REPORT.md`
- `git status --short && rg -n "dashboard|status|audit tail|permissions show|tools list|def dispatch_cli|audit" smart_agent.py agent tests README.md -g '*.py' -g '*.md'`
- `sed -n '1,240p' agent/ui/cli_commands.py && sed -n '1,260p' agent/ui/doctor.py && sed -n '1,180p' agent/ui/audit_viewer.py`
- `sed -n '1,220p' agent/ui/permissions_dashboard.py && sed -n '1,220p' agent/safety/approvals.py && sed -n '1,160p' agent/ui/connectors.py`
- `sed -n '1,260p' agent/config/runtime.py && sed -n '1,160p' agent/ui/config_viewer.py && sed -n '1,220p' tests/test_ux_packaging.py`
- `sed -n '220,520p' tests/test_ux_packaging.py`
- `sed -n '1,220p' agent/memory/tools.py && sed -n '1,220p' agent/memory/persistent_memory.py`
- `sed -n '1,180p' agent/connectors/base.py && sed -n '1,180p' agent/connectors/status.py && sed -n '1,180p' agent/connectors/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_ux_packaging.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py dashboard --audit-limit 3 | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py status --json --audit-limit 2 | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py audit tail 2`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check && PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')" && $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `pwd && git status --short && rg -n "self_improve|self-improve|improve|backlog|proposal|propose" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '1,260p' agent/tools/low_risk/workspace_files.py`
- `sed -n '1,260p' agent/core/tool_broker.py`
- `sed -n '260,620p' smart_agent.py`
- `sed -n '1,260p' agent/workflows/self_improvement.py`
- `sed -n '1,220p' tests/test_self_improvement.py`
- `sed -n '1,220p' agent/tools/registry.py`
- `rg -n "filesystem\\.read|filesystem\\.write|filesystem\\.delete|self_improvement|ToolSpec|capability" config/capabilities.yaml tests/test_policy.py tests/test_tool_broker.py agent -g '*.py' -g '*.yaml'`
- `sed -n '620,1100p' smart_agent.py`
- `sed -n '430,530p' agent/core/tool_broker.py`
- `sed -n '1,180p' tests/test_workflows.py`
- `sed -n '1,180p' agent/workflows/files.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_self_improvement.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py improve backlog --dry-run --json | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py improve propose --json`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '818,880p' smart_agent.py`
- `sed -n '1,360p' agent/tools/personal/email.py`
- `sed -n '1,260p' agent/workflows/email_assistant.py && sed -n '1,240p' tests/test_personal_modules.py`
- `rg -n "email triage|triage|draft-reply|email\\.metadata|email\\.list_metadata|Email" tests agent README.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md docs/PROJECT_STATE.md CHANGELOG.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py email triage --dry-run --json | head -100`
- `git diff --check`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '1,360p' agent/workflows/daily_briefing.py`
- `sed -n '1,360p' agent/tools/personal/calendar.py`
- `sed -n '1,360p' agent/tools/personal/contacts.py`
- `rg -n "meeting|calendar read|contacts search|def _run_.*command|briefing" smart_agent.py agent tests README.md docs/FEATURE_REGISTRY.md docs/FEATURE_ROADMAP.md docs/FEATURE_MATURITY.md docs/PROJECT_STATE.md CHANGELOG.md`
- `sed -n '700,830p' smart_agent.py`
- `sed -n '1,180p' tests/test_workflows.py`
- `sed -n '1,280p' agent/tools/registry.py`
- `sed -n '1,260p' agent/safety/policy.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_workflows.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py meeting prep --date 2026-05-22 --title "Roadmap Sync" --dry-run --json | head -100`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `date '+%Y-%m-%d %H:%M %Z'`
- `sed -n '1,260p' agent/workflows/daily_briefing.py`
- `rg -n "briefing|daily_briefing|daily" smart_agent.py agent tests README.md docs/FEATURE_REGISTRY.md docs/PROJECT_STATE.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md CHANGELOG.md`
- `sed -n '1,320p' smart_agent.py`
- `sed -n '1,260p' tests/test_workflows.py`
- `sed -n '400,470p' smart_agent.py`
- `sed -n '240,620p' tests/test_workflows.py`
- `sed -n '1,260p' agent/workflows/base.py`
- `sed -n '1,260p' agent/core/tool_broker.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_workflows.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py briefing daily --weather "Phoenix, AZ" --calendar --email-metadata --web-topic "AI safety" --dry-run --json | head -120`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `git status --short --branch && git log --oneline -5`
- Read `AGENTS.md`, `CHANGELOG.md`, `docs/PROJECT_STATE.md`, `docs/FEATURE_REGISTRY.md`, `docs/FEATURE_ROADMAP.md`, and `tests/test_feature_maturity_docs.py`.
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `git diff --check`
- `sed -n '1,260p' config/capabilities.yaml`
- `sed -n '1,260p' agent/safety/policy.py && sed -n '1,260p' agent/safety/validation.py && sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/config/schema.py && sed -n '1,220p' agent/config/loader.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_policy.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_ux_packaging.py::test_doctor_with_mocked_lmstudio_reachable tests/test_ux_packaging.py::test_doctor_with_lmstudio_unavailable tests/test_ux_packaging.py::test_doctor_reports_missing_model tests/test_ux_packaging.py::test_doctor_reports_invalid_config tests/test_connectors.py tests/test_connector_framework.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py connectors status weather | head -80`
- `rg -n "dry-run|dry_run|preflight|ApprovalRequest|approvals|ActionPreview|request_approval|decision_provider|auto_approve" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '1,340p' agent/ui/cli_commands.py`
- `sed -n '1,260p' agent/core/router.py`
- `sed -n '1,340p' agent/core/tool_broker.py`
- `sed -n '1,260p' agent/safety/approvals.py`
- `sed -n '1,260p' agent/safety/action_preview.py`
- `sed -n '1,260p' agent/tools/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_preflight.py tests/test_tool_broker.py tests/test_safety_control_plane.py tests/test_ux_packaging.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py preflight "email.read_selected_thread"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py preflight "What's the weather in Phoenix?"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `git status --short --branch`
- `rg -n "read_date_range\\(|find_availability\\(|contacts\\.search\\(|read_selected\\(|list_metadata\\(|read_selected_thread\\(|summarize_thread\\(|draft_reply\\(|send_approved\\(|create_event\\(|update_event\\(|delete_event\\(" agent smart_agent.py -g '*.py'`
- `rg -n "\\.handler\\(|handler\\(\\*\\*|broker\\.registry|get\\(tool_name\\)|ToolSpec\\(|default_registry\\(|execute\\(" agent smart_agent.py -g '*.py'`
- `rg -n "~/Library|Library/Messages|Library/Mail|Keychains|Full Disk|sqlite3|Contacts\\.app|Calendar\\.app|osascript|imap|IMAP|Messages" agent smart_agent.py -g '*.py'`
- `rg -n "CalendarConnector|ContactsConnector|EmailConnector|MessagesConnector|connector\\." agent smart_agent.py -g '*.py'`
- `sed -n '720,1310p' config/capabilities.yaml`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,420p' agent/tools/personal/calendar.py`
- `sed -n '1,180p' agent/tools/personal/read_only.py`
- `rg -n "calendar read|calendar availability|calendar\\.read_date_range|calendar\\.find_availability|def _calendar|subparsers.*calendar" smart_agent.py agent tests README.md docs -g '*.py' -g '*.md'`
- `sed -n '640,740p' smart_agent.py`
- `sed -n '1120,1365p' tests/test_personal_modules.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,280p' agent/tools/personal/messages.py`
- `sed -n '880,940p' smart_agent.py`
- `rg -n "messages\\.read_selected_thread|messages\\.summarize_thread|messages\\.draft_reply|messages\\.draft_from_text|draft-from-text|UNTRUSTED_MESSAGE|messages.send|Library/Messages|bulk message" tests/test_personal_modules.py config/capabilities.yaml README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md agent -g '*.py' -g '*.md' -g '*.yaml'`
- `sed -n '975,1065p' config/capabilities.yaml && sed -n '1,230p' agent/tools/registry.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,430p' agent/tools/personal/email.py`
- `sed -n '800,900p' smart_agent.py`
- `rg -n "email\\.list_metadata|email\\.read_selected_thread|email\\.summarize_thread|email\\.draft_reply|email.send|draft reply|UNTRUSTED_EMAIL|bulk inbox|archive|move|delete" tests/test_personal_modules.py config/capabilities.yaml README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `sed -n '1,220p' docs/checklists/personal_connector_readiness.md`
- `sed -n '1,360p' agent/tools/personal/contacts.py`
- `sed -n '740,830p' smart_agent.py`
- `rg -n "contacts\\.search|contacts\\.read_selected|contacts search|contacts read|bulk|phone|email.*redact|Contact" tests/test_personal_modules.py README.md docs/RISK_REGISTER.md docs/THREAT_MODEL.md docs/COMPLETION_REPORT.md docs/FEATURE_REGISTRY.md docs/FEATURE_MATURITY.md docs/FEATURE_ROADMAP.md`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_personal_modules.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.config.loader import load_capabilities_config; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(load_capabilities_config('config/capabilities.yaml')); print('capability manifest ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `git diff --check`
- `sed -n '1,260p' agent/memory/tools.py`
- `sed -n '1,260p' agent/memory/persistent_memory.py`
- `sed -n '1,260p' tests/test_memory.py`
- `rg -n "memory\\.|Memory|context injection|memory add|memory search|temporary_personal|personal_data_reference|session_context|workflow_lesson" agent tests README.md docs config -g '*.py' -g '*.md' -g '*.yaml'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_memory.py tests/test_ux_packaging.py::test_cli_memory_list_command_works`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `sed -n '1,240p' agent/workflows/research.py`
- `sed -n '240,420p' agent/workflows/research.py`
- `sed -n '280,430p' tests/test_workflows.py`
- `sed -n '1,210p' tests/test_web.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_workflows.py tests/test_web.py`
- `WEB_SEARCH_PROVIDER= BRAVE_SEARCH_API_KEY= PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY smart_agent.py research "local AI news"`
- `sed -n '1,260p' agent/tools/low_risk/workspace_files.py`
- `rg -n "filesystem\\.|files |workspace|patch|delete|backup|UNTRUSTED_DOCUMENT" agent tests README.md docs config -g '*.py' -g '*.md' -g '*.yaml'`
- `sed -n '1,280p' tests/test_filesystem.py`
- `sed -n '1,220p' agent/tools/low_risk/git_tools.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q tests/test_filesystem.py tests/test_files_workflow.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy('config/capabilities.yaml'); print('startup policy ok')"`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; $PY -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,220p' AGENTS.md`
- `sed -n '1,220p' docs/FEATURE_REGISTRY.md`
- `sed -n '1,220p' docs/FEATURE_MATURITY.md`
- `git status --short`
- `rg -n "web.fetch_url|fetch_url|research|browser|clip" agent smart_agent.py tests config/capabilities.yaml README.md docs -g '*.py' -g '*.yaml' -g '*.md'`
- `sed -n '1,260p' agent/tools/web/fetch.py`
- `sed -n '1,260p' agent/tools/registry.py`
- `sed -n '1,260p' smart_agent.py`
- `sed -n '190,430p' agent/tools/personal/read_only.py`
- `sed -n '1,260p' agent/workflows/research.py`
- `sed -n '1140,1225p' config/capabilities.yaml`
- `sed -n '1,180p' agent/safety/policy.py`
- `sed -n '1,560p' agent/core/tool_broker.py`
- `sed -n '1,620p' agent/tools/low_risk/workspace_files.py`
- `sed -n '1,280p' tests/test_policy.py`
- `sed -n '1,260p' tests/test_personal_modules.py`
- `sed -n '1,260p' agent/config/schema.py`
- `sed -n '1,300p' agent/connectors/registry.py`
- `sed -n '1,260p' agent/connectors/status.py`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_browser_clipping.py tests/test_connectors.py tests/test_connector_framework.py tests/test_policy.py::test_capability_manifest_has_required_hardening_metadata -q`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest -q`
- Startup policy validation via `validate_startup_policy('config/capabilities.yaml')`
- Capability manifest validation via `validate_capabilities_config(load_capabilities_config('config/capabilities.yaml'))`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_feature_maturity_docs.py -q`
- `git diff --check`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" smart_agent.py browser selected-tab | head -80`
- `sed -n '1,220p' docs/PROJECT_STATE.md`
- `sed -n '1,180p' AGENTS.md`
- `sed -n '1,180p' docs/FEATURE_MATURITY.md`
- `sed -n '1,120p' docs/FEATURE_REGISTRY.md`
- `git status --short`
- `sed -n '1,320p' agent/memory/tools.py`
- `sed -n '1,260p' agent/memory/persistent_memory.py`
- `sed -n '1,260p' agent/safety/redaction.py`
- `sed -n '520,880p' smart_agent.py`
- `rg -n "memory.store|store_personal|def _run_memory|MEMORY_SCHEMAS|secret" agent tests -g '*.py'`
- `PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"; if [ ! -x "$PY" ]; then PY="python3"; fi; "$PY" -m pytest tests/test_knowledge_capture.py -q`

## Test Status

- Prompt Pack import/splitting focused/docs tests: 28 passed in 0.18s.
- Full suite after Prompt Pack import/splitting support: 503 passed in 10.59s.
- Startup policy validation after Prompt Pack import/splitting support: startup policy ok.
- Capability manifest validation after Prompt Pack import/splitting support: capability manifest ok.
- Prompt audit CLI after Prompt Pack import/splitting support: 86 prompt records known; 49 complete, 34 queued, 3 blocked, next prompt `NATIVE-SKILLS-FOUNDATION`.
- Diff whitespace check after Prompt Pack import/splitting support: passed.
- Prompt Ledger and Prompt Queue focused/docs validation tests: 13 passed in 0.15s.
- Full suite after Prompt Ledger and Prompt Queue tracking: 488 passed in 10.65s.
- Startup policy validation after Prompt Ledger and Prompt Queue tracking: startup policy ok.
- Capability manifest validation after Prompt Ledger and Prompt Queue tracking: capability manifest ok.
- Prompt audit CLI: 85 prompt records known; 48 complete, 34 queued, 3 blocked, next prompt `NATIVE-SKILLS-FOUNDATION`.
- Diff whitespace check after Prompt Ledger and Prompt Queue tracking: passed.
- Knowledge Capture targeted tests: 9 passed in 0.63s.
- Full suite after Knowledge Capture v1: 445 passed in 7.91s.
- Startup policy validation after Knowledge Capture v1: startup policy ok.
- Capability manifest validation after Knowledge Capture v1: capability manifest ok.
- Docs validation after Knowledge Capture v1: 7 passed in 0.01s.
- Diff whitespace check after Knowledge Capture v1: passed.
- Browser clipping focused tests: 24 passed in 1.23s.
- Full suite after Browser selected URL and clipping v1: 436 passed in 7.33s.
- Startup policy validation after Browser selected URL and clipping v1: startup policy ok.
- Capability manifest validation after Browser selected URL and clipping v1: capability manifest ok.
- Docs validation after Browser selected URL and clipping v1: 7 passed in 0.01s.
- Diff whitespace check after Browser selected URL and clipping v1: passed.
- Browser selected-tab CLI stub smoke returned a clear unavailable message and audited the disabled selected-tab capability.
- Reminders / Tasks targeted tests: 10 passed in 0.34s.
- Connector registry/list regression tests after adding tasks: 12 passed in 0.39s.
- Capability manifest validation after adding tasks: capability manifest ok.
- Tasks draft-create CLI smoke: produced a pending Action Center record and did not create a task.
- Full suite after Reminders / Tasks connector: 397 passed in 5.81s.
- Startup policy validation after Reminders / Tasks connector: startup policy ok.
- Capability manifest validation after Reminders / Tasks connector: capability manifest ok.
- Docs validation after Reminders / Tasks connector: 7 passed in 0.01s.
- Diff whitespace check after Reminders / Tasks connector: passed.
- Calendar approved writes targeted tests: 10 passed in 0.67s.
- Calendar draft-create CLI smoke: produced a pending Action Center record and did not create an event.
- Full suite after calendar approved writes: 387 passed in 5.13s.
- Startup policy validation after calendar approved writes: startup policy ok.
- Capability manifest validation after calendar approved writes: capability manifest ok.
- Docs validation after calendar approved writes: 7 passed in 0.01s.
- Diff whitespace check after calendar approved writes: passed.
- Action Center targeted tests: 10 passed in 0.48s.
- Full suite after Action Center: 377 passed in 4.37s.
- Startup policy validation after Action Center: startup policy ok.
- Capability manifest validation after Action Center: capability manifest ok.
- Docs validation after Action Center: 7 passed in 0.01s.
- Diff whitespace check after Action Center: passed.
- Action Center CLI smoke: `actions list` returned an empty actions list successfully.
- Eval harness targeted tests: 8 passed in 0.46s.
- Full suite after eval harness: 367 passed in 4.01s.
- Startup policy validation after eval harness: startup policy ok.
- Capability manifest validation after eval harness: capability manifest ok.
- Docs validation after eval harness: 7 passed in 0.01s.
- Diff whitespace check after eval harness: passed.
- Policy invariant check after eval harness: no personal-data tools enabled by default, no CRITICAL approval misconfiguration, unknown capability denied.
- Docs validation: 7 passed in 0.01s.
- Current task targeted policy tests: 17 passed in 0.22s.
- Current task startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Full suite: 297 passed in 3.09s.
- Current diagnostics targeted tests: 19 passed in 0.81s.
- Full suite: 298 passed in 3.23s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Approval/preflight targeted tests: 30 passed in 0.33s.
- Full suite: 303 passed in 2.81s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Web/research targeted tests: 38 passed in 0.20s.
- Disabled-provider CLI smoke returned a structured `web search provider is not configured` report with no fabricated sources.
- Full suite: 307 passed in 2.87s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Personal connector readiness gate full suite: 320 passed in 2.90s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Final full suite: 320 passed in 2.94s.
- Direct personal-data access and ToolBroker-bypass scans: no readiness blockers found.
- Calendar targeted personal connector tests: 52 passed in 0.69s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Full suite: 321 passed in 2.92s.
- Diff whitespace check: passed.
- Capability manifest validation: capability manifest ok.
- Contacts targeted personal connector tests: 54 passed in 0.70s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.95s.
- Diff whitespace check: passed.
- Email targeted personal connector tests: 54 passed in 0.72s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.99s.
- Diff whitespace check: passed.
- Messages targeted personal connector tests: 54 passed in 0.65s.
- Docs validation: 7 passed in 0.01s.
- Startup policy validation: startup policy ok.
- Capability manifest validation: capability manifest ok.
- Full suite: 323 passed in 2.93s.
- Diff whitespace check: passed.
- Memory targeted tests: 13 passed in 0.13s.
- Full suite: 320 passed in 2.89s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.
- Filesystem/workflow targeted tests: 14 passed in 0.18s.
- Full suite: 315 passed in 2.82s.
- Startup policy validation: startup policy ok.
- Docs validation: 7 passed in 0.01s.
- Diff whitespace check: passed.

## Blockers

None currently. `.DS_Store` files are untracked local noise and should not be committed.

## Decisions Made During Current Task

- Implement prompt pack support as SDLC metadata import/splitting only; do not execute imported prompts.
- Reject any pack mode other than `import_only` and any default execution other than `one_prompt_at_a_time`.
- Store original prompt packs under `prompts/packs/` and split individual prompt files under `prompts/queued/`.
- Preserve prompt bodies exactly after the `PROMPT:` marker.
- Append imported prompt rows to `docs/PROMPT_LEDGER.md` and `docs/PROMPT_QUEUE.md`, and append an import summary to `docs/PROMPT_AUDIT.md`.
- Keep `prompts next` dependency-aware and skip approval-gated prompts that are not ready.
- Implement prompt tracking as SDLC metadata and CLI inspection/update commands only; do not add external connectors, personal-data access, sends, writes, or policy changes.
- Use `docs/PROMPT_LEDGER.md` as the master reconstructed evidence table.
- Use `docs/PROMPT_QUEUE.md` as the ordered next-prompt source of truth.
- Use `docs/PROMPT_AUDIT.md` for best-effort completed/queued/blocked/superseded/missing-evidence review.
- Use file-based prompt records under `prompts/<status>/` for future active/completed/failed/skipped/superseded prompt details.
- Require `prompts mark-complete` to include test/docs status or `--unknown` so prompts are not silently marked complete without evidence.
- Keep the next prompt as `NATIVE-SKILLS-FOUNDATION`; block explicit send/overnight prompts until approval gates are satisfied.
- Implement Knowledge Capture v1 as a workspace JSON inbox under `./workspace/captures`, not as an Apple Notes integration.
- Use only existing brokered tools for capture operations: `filesystem.write` for capture persistence, `filesystem.read` for workspace source files, `web.fetch_url` for URL sources, and `memory.store` for explicit promotion.
- Reject secret-looking capture content before writing any capture file.
- Treat manual note captures as `TRUSTED_USER`, URL captures as `UNTRUSTED_WEB`, and file captures as `UNTRUSTED_DOCUMENT`.
- Keep captured content out of long-term memory by default; `promote-to-memory` is explicit and still goes through Memory v2 policy.
- Block personal-looking content from default memory promotion before calling `memory.store`.
- Avoid Apple Notes, private app folders, browser history, email, messages, contacts, calendar, and any personal-data connector access.
- Implement Browser v1 as an explicit URL workflow over existing brokered `web.fetch_url` and `filesystem.write` tools, not as browser automation.
- Keep native selected-tab reading as a clear stub because no safe selected-scope browser integration is implemented yet.
- Add browser connector status metadata for the URL workflow while documenting that selected-tab native access remains unavailable.
- Treat fetched URL content as `UNTRUSTED_WEB` and stored clips as `UNTRUSTED_DOCUMENT`.
- Store clips only under `./workspace` and rely on the existing workspace guard for path traversal and denied-path protection.
- Do not read browser history, cookies, sessions, form contents, bookmarks, password managers, or private browser profile databases.
- Do not submit forms, download binaries by default, or automate browser UI.
- Implement Reminders / Tasks v1 as adapter/mock first; no native Reminders provider, private database scraping, or Full Disk Access.
- Register tasks as a personal connector namespace so startup validation enforces disabled-by-default.
- Make `tasks.list` HIGH risk and approval-required because task titles can expose private data.
- Make `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` CRITICAL per-action approval tools.
- Use Action Center for task creation drafts and one-shot approved create execution.
- Keep update/complete/delete direct CLI commands brokered and approval-gated rather than adding write/send shortcuts.
- Omit task notes unless explicitly allowed and never write task contents to memory by default.
- Implement calendar approved writes v1 as Action Center drafts plus brokered execution from approved actions.
- Keep the live calendar write provider deferred; the current `calendar.create_event`, `calendar.update_event`, and `calendar.delete_event` handlers are no-external-change approved-write connector stubs.
- Require `--allow-notes` before notes/body text is included in calendar write drafts.
- Keep automatic invites disabled via `send_invites=false` in v1.
- Keep recurring events unsupported in v1.
- Decode selected calendar event tokens to capture rollback data for update/delete drafts where possible.
- Consume Action Center approval once only after `ToolBroker` reports an allowed execution.
- Implement Action Center as a safety-layer persisted review queue in `agent/safety/actions.py`, not as an executor.
- Link Action Center records to `ApprovalStore`/`ApprovalRequest` so approval state is visible in existing approval infrastructure.
- Keep one-time approval consumption as state tracking only; actual tool execution remains a future `ToolBroker` path.
- Treat `memory.write_personal`, `file.delete`, and `self_improvement.commit` as Action Center action types that map to existing brokered capabilities `memory.store_personal`, `filesystem.delete`, and `git.commit`.
- Require exact preview args for all supported Action Center action types before queuing.
- Mark irreversible actions such as sends/deletes with rollback unavailable in the preview.
- Invalidate prior approvals after an action draft is edited.
- Build the eval harness as a CLI validation layer under `agent/ui/evals.py` rather than as a new connector or workflow with new permissions.
- Keep eval results structured and write both `logs/eval_results.json` and `docs/EVAL_REPORT.md`.
- Keep personal-data evals skipped by default; no calendar/contact/email/message live reads are attempted.
- Use `ToolBroker.execute()` and `ToolBroker.dry_run()` for tool evals so policy, rate limits, approval behavior, and audit remain in path.
- Use a controlled `./workspace/eval` file for workspace read/write validation.
- Use only a non-sensitive project fact for memory eval and delete it before completion.
- Keep `docs/PROJECT_STATE.md` as the primary resume file.
- Keep `docs/FEATURE_REGISTRY.md` as the source-of-truth feature safety/status table.
- Keep `docs/FEATURE_ROADMAP.md` as the ordered batch queue.
- Keep `CHANGELOG.md` in Keep-a-Changelog style.
- Preserve uncommitted connector-framework work rather than reverting user/Codex changes.
- Validate tracking docs through pytest instead of adding a runtime docs command in this pass.
- Normalize the manifest in place rather than adding a second manifest file.
- Keep `stores_data` as a required field in addition to the new normalized schema, because existing policy/docs already use it.
- Keep runtime and connector diagnostics read-only and metadata-only; do not execute tools or probe personal data.
- Implement preflight as a brokered dry-run preview instead of a separate execution path.
- Allow exact tool/capability names in preflight so high-risk disabled capabilities can be inspected before enabling personal connectors.
- Keep preflight prompt-free and deterministic; it does not ask the LLM for tool calls.
- Keep source-grounded research deterministic and brokered; no LLM synthesis pass was added in this task.
- Expose `fetch_failures` as a first-class report field so failed or denied fetches are obvious to the caller.
- Treat pure webpage instruction-injection text as unusable evidence instead of falling back to it as an excerpt.
- Build file assistant commands as a workflow wrapper around existing `filesystem.*` and `git.diff` tools instead of direct file access.
- Label `filesystem.read` output and file workflow summaries/searches as `UNTRUSTED_DOCUMENT`.
- Do not add a `files delete` shortcut; deletion remains available only through the existing approval-gated `filesystem.delete` tool.
- Route memory CLI list/add/search/delete/export/clear/context through ToolBroker instead of the old direct memory viewer path.
- Add `memory.context` as a bounded non-personal context injection tool that audits injected memory IDs.
- Keep personal-memory context injection disabled by default; personal data still requires approval to store and is not injected without a future approved design.
- Add a personal connector readiness checklist as a prerequisite gate; it verifies safety controls only and does not approve live personal-data reads.
- Keep the calendar connector selected-range, disabled by default, and approval-required; add event-text-as-data labeling instead of altering policy or allowing event text to drive tools.
- Keep the contacts connector selected-scope, disabled by default, and approval-required; add contact-text-as-data labeling and require requested fields plus config gates before sensitive email/phone/address values are returned.
- Treat email metadata as `UNTRUSTED_EMAIL`, because sender and subject fields can contain adversarial instructions even without body text.
- Keep email draft-only output explicit: no send, delete, move, archive, approval, or memory storage side effects.
- Add `messages.draft_from_text` as a distinct brokered capability/tool for the safe manual workspace-file fallback instead of overloading `messages.draft_reply` at the CLI boundary.
- Keep live macOS Messages integration unavailable until a safe permissioned implementation path exists; do not scrape `~/Library/Messages` or request Full Disk Access.
- Build Agent Dashboard v1 as a CLI/status interface rather than a local web dashboard for now, matching the current architecture and avoiding background services.
- Keep dashboard memory visibility to counts by category/scope only; do not display stored memory content.
- Keep dashboard audit visibility to safe metadata fields; do not display raw sanitized args by default.

## Things To Verify Before Marking Complete

- Prompt pack parser rejects duplicate ids/orders, missing end markers, missing metadata, invalid risk levels, missing dependencies, cycles, completed-on-import, and `execute_all`.
- `validate-pack` writes no files.
- `import`/`split` write pack and queued prompt files, update ledger/queue/audit, preserve prompt bodies, and do not execute prompts.
- Full suite, docs validation, startup policy validation, capability manifest validation, diff whitespace check, completion report, project state, feature registry, feature maturity, changelog, and prompt audit are updated.
- Prompt tracking docs exist, queue rows have prompt IDs, project state references `active_prompt_id` and `next_prompt_id`, AGENTS requires prompt ledger updates, prompt CLI tests pass, full suite passes, startup policy validation passes, capability manifest validation passes, and completion report is updated.
- Knowledge Capture v1 full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Browser selected URL and clipping v1 focused tests, full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, CLI selected-tab stub smoke, README, decision record, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Contacts approved edits full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, completion report, and PROJECT_STATE completion update are complete.
- Email approved send targeted tests, CLI smoke, full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Messages safe handoff targeted tests, disabled CLI smoke, full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, bypass/path scans, README, decision record, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, release checklist, completion report, and PROJECT_STATE completion update are complete.
- Reminders / Tasks full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, completion report, and PROJECT_STATE completion update are complete.
- Calendar approved writes full suite, startup policy, capability manifest validation, docs validation, diff whitespace check, README, changelog, feature registry, roadmap, maturity tracker, risk register, threat model, completion report, and PROJECT_STATE completion update are complete.
- Action Center targeted tests passed: 10 passed in 0.48s.
- Full suite passed after Action Center: 377 passed in 4.37s.
- Startup policy validation passed after Action Center.
- Capability manifest validation passed after Action Center.
- Docs validation passed after Action Center: 7 passed in 0.01s.
- Diff whitespace check passed after Action Center.
- `actions list` CLI smoke succeeded.
- `README.md`, `CHANGELOG.md`, `FEATURE_REGISTRY.md`, `FEATURE_ROADMAP.md`, `FEATURE_MATURITY.md`, `COMPLETION_REPORT.md`, and `PROJECT_STATE.md` updated for Action Center.
- Eval harness targeted tests passed.
- Full test suite passed: 367 passed in 4.01s.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed: 7 passed in 0.01s.
- `git diff --check` passed.
- Policy invariant check passed: no personal-data tools enabled by default, no CRITICAL approval misconfiguration, unknown capability denied.
- `docs/COMPLETION_REPORT.md`, `CHANGELOG.md`, `FEATURE_REGISTRY.md`, `FEATURE_ROADMAP.md`, `FEATURE_MATURITY.md`, and `PROJECT_STATE.md` updated for eval harness.
- Full test suite passed: 359 passed in 3.61s after tracking updates.
- Startup policy validation passed.
- Capability manifest validation passed.
- Docs validation passed: 7 passed in 0.01s.
- Diff whitespace check passed.
- Feature inventory confirmed against changelog, registry, maturity tracker, roadmap, and project state.
- Personal-data tools remain disabled by default.
- HIGH-risk enabled actions still require approval.
- CRITICAL capabilities still require per-action approval with no approval reuse.
- Unknown capabilities are still denied.
- `docs/COMPLETION_REPORT.md` updated.
- `docs/PROJECT_STATE.md` status changed from `in_progress` to `complete`.
- `CHANGELOG.md`, `FEATURE_REGISTRY.md`, and `FEATURE_ROADMAP.md` reflect this tracking pass.
- Capability normalization: full suite, docs validation, startup policy, completion report, and PROJECT_STATE completion update are complete.
- Runtime doctor/dashboard polish full suite, docs validation, startup policy, completion report, and PROJECT_STATE completion update are complete.
- Approval/preflight full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Source-grounded web research full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Workspace file assistant full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Memory v2 full suite, docs validation, startup policy, completion report, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Personal connector readiness gate full suite, startup policy, capability manifest validation, direct-access scans, checklist, completion report, release checklist, risk register, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Calendar read-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Contacts read-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Email draft-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Messages draft-only full suite, startup policy, capability manifest validation, docs validation, completion report, release checklist, risk register, threat model, feature registry, maturity tracking, changelog, roadmap, and PROJECT_STATE completion update are complete.
- Daily Briefing v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, and PROJECT_STATE completion update are complete.
- Meeting Prep v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, risk register, threat model, and PROJECT_STATE completion update are complete.
- Email Triage v1 full suite, startup policy, capability manifest validation, docs validation, completion report, feature registry, maturity tracking, changelog, roadmap, README, risk register, threat model, and PROJECT_STATE completion update are complete.
- Self-improvement backlog generator full suite, startup policy, capability manifest validation, docs validation, README, changelog, feature registry, roadmap, maturity tracking, completion report, and PROJECT_STATE completion update are complete.
- Agent Dashboard v1 targeted UX tests, CLI smoke, full suite, startup policy, capability manifest validation, docs validation, README, changelog, feature registry, roadmap, maturity tracking, completion report, and PROJECT_STATE completion update are complete.

## Next Queue

1. NATIVE-SKILLS-FOUNDATION: Native Skills Program foundation.
2. SKILL-MARKETPLACE-SURVEY: Skill marketplace survey.
3. NATIVE-SKILL-VETTER: Native skill vetter.
4. NATIVE-SKILL-MANIFEST: Native skill manifest and loader.
5. SKILL-FINDER-NATIVE: Skill finder native skill.
6. PDF-WORKSPACE-SKILL: PDF workspace native skill.
7. SESSION-LOGGING-REPLAY: Session logging and replay system.
8. DOGFOOD-COMMAND-SUITES: Manual dogfood command suites.
9. FEEDBACK-CAPTURE-RATINGS: Feedback capture and ratings.
10. See `docs/PROMPT_QUEUE.md` for the full ordered prompt queue and blocked approval gates.

## Next Feature Set: Controlled Actions and Proactive Workflows

1. Live validation and eval harness. Complete in local mocked tests; live runs remain user opt-in.
2. Unified Action Center. Complete in local tests; no direct execution path.
3. Calendar approved writes. Complete in local targeted tests; live native writes deferred.
4. Reminders/tasks connector. Complete in local targeted tests; native Reminders provider deferred.
5. Contacts approved edits. Complete in local targeted tests; native Contacts write provider and delete deferred.
6. Email approved send. Complete in local targeted tests; mock provider only and real provider deferred.
7. Messages safe handoff / send decision. Complete in local targeted tests; automatic send remains deferred.
8. Browser selected-tab / clipping connector. Complete in local targeted tests; native selected-tab remains stubbed.
9. Notes / knowledge capture. Complete in local/full tests; Apple Notes integration deferred.
10. Daily briefing v2. Complete in local/full tests; live personal sections require explicit approval/config.
11. Meeting follow-up workflow. Complete in local/full tests; action execution remains separate and approval-gated.
12. Personal task extraction. Complete in local/full tests; task writes remain Action Center drafts only.
13. Controlled self-improvement implementation loop. Complete in focused/full tests; startup policy, capability manifest, docs validation, CLI smokes, and diff whitespace check passed.
14. Scheduler / automation v1.
15. Full feature maturity review.

## Open Decisions

- Whether to commit the current accumulated post-baseline feature batch together.
- Whether to implement a native Calendar.app/EventKit write provider after a separate decision record and explicit approval.
- Whether to implement a native Reminders/EventKit reminders provider after a separate decision record and explicit approval.
- Whether to add future approval-gated personal-data evals after the Unified Action Center exists.
- Whether to add a dedicated `docs validate` CLI command later or keep validation as pytest-only.
- Whether a future dashboard should add a local web UI after CLI dashboard release-gating.

## Known Risks

- Tracking files can drift if future runs skip documentation updates.
- Personal connector work remains high risk and must stop at approval gates.
- Live validation depends on local LM Studio/provider/user configuration.
- Uncommitted work can be lost if not committed after tests pass.

## Resume Instructions For Codex

Before doing any work:

1. Read `SPEC.md`.
2. Read `docs/SDLC.md`.
3. Read `AGENTS.md`.
4. Read `docs/PROJECT_STATE.md`.
5. Read `docs/PROMPT_QUEUE.md`.
6. Read `docs/PROMPT_LEDGER.md`.
7. Read `docs/FEATURE_ROADMAP.md`.
8. Read `docs/FEATURE_REGISTRY.md`.
9. Read `docs/COMPLETION_REPORT.md`.
10. Inspect git status.
11. Identify the current task and next safe task.
12. Do not proceed past approval gates.

Before finishing any run:

1. Run the relevant tests.
2. Update `docs/COMPLETION_REPORT.md`.
3. Update `CHANGELOG.md` for user-visible changes.
4. Update `docs/FEATURE_REGISTRY.md`.
5. Update `docs/FEATURE_ROADMAP.md` if statuses changed.
6. Update `docs/PROJECT_STATE.md`.
7. Update `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, and `docs/PROMPT_AUDIT.md` when prompt status changes.
8. Report files changed, commands run, tests run, results, blockers, prompt_id, next_prompt_id, and next task.

## Last Run Summary

Completed Prompt Pack import/splitting support. Added strict prompt pack parser, validator, splitter, queue/ledger/audit integration, pack format docs/templates, and prompt CLI commands for `validate-pack`, `import`, `split`, and `mark-superseded`. Imported packs are `import_only`, stored under `prompts/packs/`, split into `prompts/queued/`, and never executed automatically. Focused prompt pack/docs validation passed with 28 tests, full suite passed with 503 tests, startup policy and capability manifest validation passed, prompt audit reported 86 known prompt records with 49 complete, 34 queued, 3 blocked, and no active prompts, and diff whitespace check passed. Next recommended prompt is `NATIVE-SKILLS-FOUNDATION`.
