# Test Plan

## Unit Tests

- Policy decisions.
- Tool broker execution and denial.
- LM Studio request payload construction.
- Audit entry redaction and hash chaining.
- Tool argument validation.

## Integration Tests

- No-tool chat sends no tools.
- Tool-call loop appends matching tool results.
- CLI modes construct expected orchestration options.
- Golden Eval Suite tests load data-backed cases from `eval_cases/`, run router/policy/ToolBroker/workflow/prompt-injection checks, write scorecard reports, and keep personal-data cases skipped by default.
- Model-router benchmark and prompt-quality tests load reviewed fixture prompts, compare expected vs actual routes, attached tools, and policy decisions, verify no-tool prompts attach no tools, verify personal-data/send requests do not auto-execute, verify prompt-injection wrappers, and write prompt-quality reports.
- Prompt tracking CLI lists, advances, shows, adds, marks, audits, and reports missing prompt records without executing agent tools.
- Session logging tests cover start/status/end/list/show/replay/export behavior, `session run -- ...` stdout/stderr/exit-code capture, secret/email/phone and command-line redaction, visible audit-id linking, large-output truncation/storage, malformed session files, and gitignore protection for raw reports.
- Session review tests cover clean session summaries, failed command detection, user feedback flags, optional bug creation, stable incrementing bug ids, secret/personal-data redaction, P0 safety classification for policy-bypass signals, and `bugs list/show/export`.
- Smoke harness tests use mocks for LM Studio, web search/fetch, and personal connector policy checks.
- Pytest markers identify `unit`, `integration`, `live_lmstudio`, `live_web`, `live_calendar`, `live_contacts`, `requires_approval`, and `personal_data`.
- Tests marked `personal_data` are skipped by default and must be explicitly selected.

## Policy Tests

- Unknown capabilities denied.
- SAFE actions allowed.
- HIGH actions ask approval.
- CRITICAL actions require per-action approval.
- FORBIDDEN actions denied.
- Capability manifest validation requires normalized capability name, tool name, connector name, risk level, trust level, default state, approval requirement, approval reuse flag, storage flag, rate limit field, memory behavior, audit fields, setup hint, and docs reference.
- Startup validation rejects missing risk levels, missing trust levels, missing approval rules, missing audit rules, invalid memory behavior, and manifest bypass flags.
- Personal-data capabilities must be disabled by default.
- CRITICAL capabilities must require per-action approval and disallow approval reuse.
- Every registered tool must have a matching manifest capability.

## Approval Tests

- Approval required when policy returns `ASK`.
- Denial prevents execution.
- Critical actions do not reuse approvals.
- Interactive approval prompts display previews, allow details review, and execute only after explicit approval.
- Action Center tests verify list/show, HIGH and CRITICAL approval requirements, one-time approval consumption, denial, edit invalidation, non-interactive blocking, no direct execution, required tool metadata, and export/audit minimization of sensitive bodies and drafts.
- Calendar approved write tests verify draft-only Action Center records, create/update/delete approval gates, denial blocking, one-shot approved execution through `ToolBroker`, direct broker write denial without a verified Action Center action id, rollback token capture, notes/body omission unless explicitly allowed, audit lifecycle, and disabled-by-default manifest entries.
- Contacts approved edit tests verify draft-only Action Center records, update/create approval gates, denial blocking, one-shot approved execution through `ToolBroker`, direct broker write denial without a verified Action Center action id, submitted-args matching against the approved preview, exact field diffs, sensitive-field redaction, bulk-edit denial, delete deferral, audit lifecycle, and disabled-by-default manifest entries.
- Email approved send tests verify Action Center reviewed drafts, CRITICAL per-action approval, denial blocking, edit invalidation, one-shot mock send execution through `ToolBroker`, direct broker send denial without a verified Action Center action id, submitted-args matching against the approved reviewed draft, full body preview, missing recipient blocking, attachment blocking, untrusted reply context, audit lifecycle, and disabled-by-default manifest entries.
- Messages safe handoff tests verify Action Center reviewed save/copy drafts, approval blocking, workspace-only saves, mock clipboard copy, direct broker save/copy denial without a verified Action Center action id, submitted-args matching against the approved reviewed draft, no automatic send capability, no memory writes, and audit lifecycle.

## Audit-Log Tests

- Executions are logged.
- Denials are logged.
- Approval results are logged.
- Hash chain links entries.
- Secrets are redacted.
- Action lifecycle audit entries minimize sensitive Action Center previews while preserving lifecycle status, risk, trust, capability, and approval metadata.

## Prompt-Injection Tests

- Webpage instructions are ignored.
- Email/message instructions are ignored.
- Document instructions are ignored.
- Golden eval prompt-injection fixtures verify hostile page text is wrapped as untrusted data and does not become a system/tool instruction.
- Regression phrases include attempts to ignore instructions, reveal secrets, change policy, call tools, send email/text, disable audit logs, and store private data.

## Web Research Tests

- Web search provider missing returns a structured error.
- Brave/provider results normalize to compact untrusted records.
- `WEB_ACCESS_ENABLED=false` denies search/fetch through the broker.
- Fetch validates blocked domains, redirects, content types, and size limits.
- Scripts and event-handler content are stripped from extracted text.
- Fetched content is labeled and wrapped as `UNTRUSTED_WEB`.
- Research workflow does not fabricate sources.
- Research workflow reports fetch failures.
- Foreign-language titles/snippets/excerpts pass through without cloud translation.
- Audit logs include search and fetch actions.

## Memory Tests

- Preference, project fact, and workflow lesson memories can be stored through `ToolBroker`.
- Secrets are rejected and redacted from audit logs.
- Email/message/contact/calendar content is not stored by default.
- Personal-data memory requires approval.
- Search respects scope and category filters.
- Export/delete/clear lifecycle operations are audited and document best-effort deletion limits.
- Context injection obeys record and character limits, excludes personal memory by default, and audits injected memory IDs.
- Knowledge Capture tests cover workspace-only note captures, URL captures through `web.fetch_url`, file captures through `filesystem.read`, explicit `--trusted-user` file labeling, secret rejection before capture writes, prompt-injection filtering, personal-data default memory-promotion blocks, and `promote-to-memory` routing through `memory.store`.
- Privacy Center tests cover status, metadata-only inventory, disabled connector visibility, memory counts without contents, redacted export previews, delete-memory confirmation denial, brokered `memory.clear` execution, audit summary, permissions summary, CLI dispatch, and no personal connector reads.

## Weather Tests

- Weather provider missing returns a structured error.
- `WEB_ACCESS_ENABLED=false` denies weather calls through the broker.
- Weather capabilities are LOW risk, rate-limited, audited, and labeled `UNTRUSTED_WEB`.
- Configured mock providers return normalized current weather and forecast data.
- Open-Meteo provider tests mock geocoding and forecast endpoints; live internet is not required for unit tests.
- Open-Meteo tests cover current normalization, forecast normalization, malformed responses, timeouts, geocoding failures, and audit domains.
- NWS provider tests mock geocoding, points/grid, forecast, hourly, and alerts endpoints; live internet is not required for unit tests.
- NWS tests cover U.S.-only location enforcement, forecast normalization, alert normalization, retryable timeouts, missing grid data, CLI alerts, and audit domains.
- WeatherKit stub tests cover not-configured errors, env presence checks, no secret values in output/audit logs, and provider selection only when explicitly configured.
- Forecast days are capped by `WEATHER_MAX_FORECAST_DAYS`.
- Location arguments are redacted from audit logs and are not persisted as history by default.
- Weather preferences tests cover no default location by default, explicit default-location use, default-location audit source, units preference, cache disabling, config show/set/clear, and no automatic memory writes.
- Weather-aware web research tests cover simple weather staying weather-only, delay/closure/latest-storm queries attaching web when needed, provider errors becoming limitations, web-disabled limitations, untrusted web instruction filtering, separated weather/web sections, and audit logs for both weather and web calls.
- Provider timeouts/errors return structured error payloads.
- Unknown weather tools are denied.

## Connector Dashboard Tests

- Weather configured status reports provider and enabled state without network calls.
- Web missing-provider status reports setup hints without hallucinating configuration.
- Browser status reports explicit URL workflow setup and does not require browser profile access.
- Personal connectors remain disabled by default.
- Connector status output does not reveal API keys, passwords, or tokens.
- Connector doctor does not access personal data or audit noisy personal checks.
- Connector status includes normalized capability summaries, risk, approval, rate-limit, cache, last-success/error, and setup-hint fields.
- Runtime doctor checks normalized manifest validation, ToolBroker initialization, connector registry loading, personal connector defaults, and CRITICAL action defaults without sending prompts or attaching tools.

## Live Smoke Tests

- `python smart_agent.py smoke --lmstudio` verifies no-tool chat, debug events, and the safe time-tool path when `LMSTUDIO_MODEL` and LM Studio are available.
- `python smart_agent.py smoke --web` verifies configured search, safe public fetch, and source-grounded research behavior without fabricating sources.
- `python smart_agent.py smoke --calendar --contacts` performs dry-run connector and policy checks only; it does not read personal data by default.
- Unconfigured live services are reported as skipped instead of faked as passing.

## Personal-Data Tests

- Personal modules disabled by default.
- Selected-scope reads require approval.
- Body text is not stored in long-term memory by default.
- Calendar selected-range reads require approval, enforce max date ranges, omit notes/body by default, redact locations by default, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Calendar availability returns slots without leaking event details.
- Contacts search/read require approval, keep tools disabled by default, return compact search candidates, require a selected-scope token and explicit requested fields for selected reads, omit notes, redact email/phone/address values by default, deny bulk export attempts, and audit accesses as `LOCAL_PRIVATE_DATA`.
- Email metadata/read/summarize/draft require approval when enabled, keep tools disabled by default, return no body in metadata, wrap selected thread bodies as `UNTRUSTED_EMAIL`, ignore prompt injection, never send drafts, refuse bulk thread ids, avoid long-term body storage, and audit access.
- Messages read/summarize/draft require approval when enabled, keep tools disabled by default, do not implement sends or bulk history reads, refuse bulk thread ids, return clear setup errors for unsafe/unconfigured adapters, restrict manual draft context files to `./workspace`, wrap content as `UNTRUSTED_MESSAGE`, ignore prompt injection, avoid long-term body storage, and audit access.
- Messages save/copy handoff requires Action Center approval with verified action ids and approved-preview argument matching before any workspace draft write or clipboard copy.
- Browser selected URL and clipping tests cover canonical capabilities `browser.read_url`, `browser.summarize_url`, `browser.clip_url_to_workspace`, and disabled `browser.selected_tab`; explicit URL fetch through `web.fetch_url`; blocked-domain denial; prompt-injection filtering; workspace-only clipping through `filesystem.write`; `UNTRUSTED_WEB`/`UNTRUSTED_DOCUMENT` labeling; selected-tab stub setup notes; no browser history/cookie/session/password/profile access; and audit logs for fetch/write/stub paths.
- Tasks/reminders tests cover disabled provider access, approval-required listing, brokered `tasks.draft_create` Action Center queuing, create/complete/delete approval gates, one-shot approved create execution, no memory writes, audit lifecycle, setup errors, and mock provider list/create/update/complete/delete paths.

## Self-Improvement Tests

- Proposal mode does not edit files.
- Implementation creates a branch.
- Policy weakening and audit disabling are blocked.
- Tests and diffs are produced before commit.
- `improve create-action-for-commit` runs brokered tests and brokered diff, creates only a pending Action Center `self_improvement.commit` record when tests pass and a diff exists, and does not commit.
- Failed self-improvement tests prevent commit action creation.
- `improve overnight-plan` excludes HIGH/CRITICAL and personal-data work, ranks docs/tests/hardening candidates first, reads tracking docs through `ToolBroker`, and creates no branch, schedule, memory write, commit, or file edit.
- Overnight runbook and report template existence tests verify safe-mode constraints and review fields are documented.

## Release-Gate Tests

- All selected milestone tests pass or failures are documented.
- Forbidden capabilities are absent.
- Audit and policy checks pass.
- Full release-gate maturity reviews run the full suite, startup policy validation, capability manifest validation, safe eval suite, command registry validation, native skill validation, unknown-tool denial, ToolBroker path scans, personal-data default checks, HIGH approval checks, and CRITICAL per-action/no-reuse checks.

## Prompt Tracking Tests

- `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_AUDIT.md`, and `docs/templates/prompt_record_template.md` exist.
- `docs/PROMPT_PACK_FORMAT.md` and `docs/templates/prompt_pack_template.md` exist.
- Every queued prompt has a `prompt_id`.
- At most one prompt is active at a time.
- `docs/PROJECT_STATE.md` references `active_prompt_id`, `next_prompt_id`, `prompt_queue_status`, and `last_prompt_audit_result`.
- `AGENTS.md` requires prompt ledger/queue updates.
- `prompts mark-complete` requires test/docs status fields or `--unknown`.
- Prompt pack parser tests cover valid packs, duplicate ids, duplicate order, missing end markers, missing metadata, invalid risk levels, missing dependencies, circular dependencies, execute-all rejection, validate-without-write behavior, import file writes, queue updates, dependency-aware next prompt selection, approval-gate blocking, body preservation, and missing completion evidence.
- PromptOps Workbench tests cover import from stdin/file/clipboard, raw single prompt import, invalid metadata/risk rejection, dependency-aware next prompt selection, copy-next clipboard behavior, disabled-by-default run-next, safe-only autopilot rejection of HIGH/approval-gated prompts, secret redaction in reports, and mark-complete evidence requirements.

## Command Registry Tests

- `docs/COMMAND_REGISTRY.md`, `docs/COMMAND_TEST_MATRIX.md`, `docs/COMMAND_LEGACY.md`, `docs/COMMAND_QA_RUNBOOK.md`, and command templates exist.
- Every registered command has an id, command string, group, status, maturity level, risk level, approval requirement, description, example, docs link, and test/manual QA status.
- Command registry validation catches missing docs, missing matrix rows, invalid status values, invalid risk values, missing examples, and missing AGENTS/README references.
- CLI tests cover `commands list`, `commands show`, `commands search`, `commands legacy`, `commands deprecated`, `commands validate`, `commands qa-plan`, and `commands qa-run`.
- `commands qa-run` does not execute command examples in v1 and only prints SAFE/LOW active command examples for the requested group.

## Native Skills Program Tests

- `docs/native_skills/NATIVE_SKILLS_PROGRAM.md` exists.
- `docs/native_skills/SKILL_INTAKE_PROCESS.md` exists.
- `docs/native_skills/NATIVE_SKILL_CRITERIA.md` exists.
- `docs/native_skills/NATIVE_SKILL_CANDIDATES.md` exists.
- `docs/native_skills/SKILL_RISK_MODEL.md` exists.
- `docs/templates/native_skill_record_template.md` exists.
- Program docs define native skills as reviewed local workflows mapped to `ToolBroker`.
- Program docs state native skills are not unreviewed external scripts, direct tool access, hidden network access, automatic installs, or approval bypasses.
- Native skill vetter tests cover safe `SKILL.md` files, shell-command flags, network-call flags, secret references, filesystem escapes, prompt-injection language, approval-bypass language, opaque binaries, missing license warnings, no script execution, workspace-only reads, and audit logging.
- Native skill manifest tests cover valid manifest loading, invalid manifest rejection, unknown capability rejection, missing risk/trust rejection, ToolBroker-bypass language rejection, personal-data disabled-by-default enforcement, and `skills list/show/validate/doctor` command behavior.
- Native skill finder tests cover implemented manifest matches, planned candidate matches, maturity/readiness reporting, approval reporting, no-match candidate creation guidance, no external marketplace search/install, brokered execution, and audit logging of local docs read.
- PDF workspace native skill tests cover path traversal, denied paths, PDF info fixtures, embedded text extraction, no-table extraction behavior, no-memory summaries, file-size limits, malformed PDFs, audit logging, no external binary execution, CLI broker path, and native manifest/docs validation.
- Criteria docs include disqualifiers for unrestricted filesystem access, browser cookies/session tokens, Keychain/password access, private app database scraping, opaque binaries, unclear licenses, and unsandboxable behavior.
- Risk model docs cover external skill supply-chain risk and prohibit running external code during intake.

## Scheduler Tests

- Schedule create/list writes and reads explicit local schedule records.
- Manual `schedule run` executes a safe supported workflow and audits run start/finish.
- Personal scheduled Daily Briefing sections require normal approval and do not read personal data when approval is unavailable.
- Unsupported or CRITICAL workflows are rejected and not executed.
- Pause prevents runs and delete removes the local schedule record.
- Scheduler v1 creates no LaunchAgent, cron, daemon, login item, or hidden persistence.
- CLI tests cover schedule create/list with a test-local `SCHEDULE_PATH`.
- Scheduler backup tests verify `backup_create` runs through brokered `backup.create`, writes a redacted backup, audits the provider call, reads no personal connectors, writes no memory, and rejects unredacted backup args.
