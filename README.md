# Local Mac AI Agent

A local-first Mac AI agent built safety-first. The initial runtime talks to LM Studio through the OpenAI-compatible chat completions API and can execute only approved tools through a brokered policy/audit layer.

## Current Status

M0-M11 are complete:

- LM Studio chat client.
- Thin orchestrator.
- `--no-tools` mode for clean Qwopus chat.
- Safe `time.get_current_time` tool.
- `ToolBroker` enforcement.
- Manifest-backed `PolicyEngine`.
- Approval manager with request IDs, preview formatting, audit lifecycle logging, and conservative non-interactive denial.
- Interactive approval prompts for live CLI sessions.
- Hash-chained audit JSONL.
- Deterministic router so normal chat attaches no tools by default.
- Redacted debug payload formatting.
- Workspace-bounded filesystem tools.
- Fixed git status/diff/branch tools, with commit approval-gated.
- Fixed pytest runner inside the project repo.
- Web search tool with optional Brave Search provider support and clear provider-not-configured behavior.
- Web fetch tool with blocked-domain checks, binary-download refusal, script-stripping extraction, and untrusted-content wrapping.
- Session and SQLite-backed persistent memory.
- Memory tools refuse secrets and personal content by default.
- Personal-memory storage is approval-gated.
- Read-only personal module interfaces are present but disabled by default.
- Calendar read-only selected-range connector support is present but disabled by default.
- Contacts read-only selected-scope connector support is present but disabled by default.
- Email metadata, selected-thread read, summary, and draft-only connector support is present but disabled by default.
- Email/message reply drafting is draft-only and never sends.
- Assistant workflows compose existing tools only through `ToolBroker`.
- Workflow action reports show each step and result.
- Approved write/send action tools are present but disabled by default.
- Critical write/send actions require explicit per-action approval with preflight summaries.
- Controlled self-improvement manager supports propose, branch-bound implement, run-tests, show-diff, commit-action checkpointing, and approval-gated commit.
- Self-improvement blocks protected safety file edits and safety-weakening content.
- Self-improvement backlog commands inspect approved project files through `ToolBroker` and propose read-only improvements without editing, granting, installing, or committing.
- CLI inspection commands for tools, permissions, audit, memory, config, setup, and interactive entry.
- Agent Dashboard v1 consolidates runtime, LM Studio, tools, connectors, permissions, approvals, audit metadata, memory counts, risk settings, last test run, and setup hints.
- Local packaging/setup docs.
- Release-gate validation tests.
- M0-M11 tests.

Higher-risk capabilities are documented but locked until their prerequisites pass.

## Setup

1. Install Python 3.11+.
2. Create a virtual environment.
3. Install test dependencies:

```bash
python -m pip install -e ".[dev]"
```

4. Start LM Studio with the OpenAI-compatible server enabled at `http://localhost:1234/v1`.
5. Set the model:

```bash
export LMSTUDIO_MODEL="your-local-model-name"
```

On this Mac, the bundled Codex runtime is the known-good Python 3.12 path:

```bash
PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
```

## Usage

No-tool chat:

```bash
python smart_agent.py --no-tools "Explain RCS vs iMessage"
```

Tool-enabled chat:

```bash
python smart_agent.py --debug "What time is it?"
```

Dry-run mode:

```bash
python smart_agent.py --dry-run --debug "What time is it?"
python smart_agent.py --dry-run web "local AI news"
python smart_agent.py preflight "email.read_selected_thread"
python smart_agent.py preflight "What's the weather in Phoenix?"
```

Dry-run mode routes normally and evaluates policy, approval requirements, sanitized args, and action previews, but does not execute tools. Dry-run evaluations are audited with `dry_run=true`. The `preflight` command is a prompt-free preview path: it uses the deterministic router or an exact tool/capability name, evaluates likely tool calls through `ToolBroker.dry_run()`, and shows risk, policy, approval, sanitized arguments, and whether exact action details are still missing.

Web tools:

```bash
python smart_agent.py --debug "Read this URL https://example.com"
python smart_agent.py --debug "Look up local AI news"
python smart_agent.py web "local AI news"
python smart_agent.py research "local AI news"
```

`web.search` returns a clear error until a supported provider is configured. With Brave Search:

```bash
export WEB_ACCESS_ENABLED=true
export WEB_SEARCH_PROVIDER=brave
export BRAVE_SEARCH_API_KEY="..."
python smart_agent.py web "local AI news"
```

The direct `web` command executes `web.search` through `ToolBroker`, `PolicyEngine`, rate limits, and audit logging. It returns search-result metadata only; it does not fetch full pages. Search results are labeled `UNTRUSTED_WEB`, and search queries are redacted from audit logs by default unless `WEB_SEARCH_AUDIT_QUERIES=true` is explicitly set.

`web.fetch_url` treats fetched pages as untrusted data and refuses binary downloads by default. It validates public HTTP(S) URLs, validates redirect targets before following them, strips common tracking parameters, enforces content-type and size limits, extracts readable text, strips scripts/styles, and wraps page text with the untrusted-web warning.

Source-grounded research:

```bash
python smart_agent.py research "local AI news"
python smart_agent.py research --max-results 2 --no-fetch "local AI news"
python smart_agent.py research --locale es --summary-language en "últimas noticias de IA"
```

The research command runs `web.search` and optional `web.fetch_url` calls through `ToolBroker`, then returns a source-aware JSON report. It does not fabricate citations; if search or fetch fails, the report says so in `summary` and `fetch_failures`. Foreign-language titles, snippets, and excerpts are preserved, with a simple language hint when available. Fetched page text is treated as `UNTRUSTED_WEB` data; page instructions are filtered from excerpts and cannot request tools or change policy.

Browser selected URL and clipping:

```bash
python smart_agent.py browser read-url "https://example.com"
python smart_agent.py browser summarize-url "https://example.com"
python smart_agent.py browser clip-url "https://example.com" --to workspace
python smart_agent.py browser selected-tab
```

Browser v1 is URL-based only. The workflow capabilities are `browser.read_url`, `browser.summarize_url`, `browser.clip_url_to_workspace`, and the disabled `browser.selected_tab` stub. `read-url` and `summarize-url` fetch explicit public URLs through `web.fetch_url`; `clip-url` fetches through `web.fetch_url` and writes through `filesystem.write` under `./workspace`. Fetched page content is `UNTRUSTED_WEB`, and saved clips are `UNTRUSTED_DOCUMENT`. The connector does not read browser history, cookies, sessions, passwords, forms, bookmarks, private browser databases, or password managers, and it does not submit forms or automate a browser. `selected-tab` is a clear stub until a safe selected-scope native integration is reviewed; see `docs/decisions/browser_selected_tab_clipping.md`.

Knowledge Capture:

```bash
python smart_agent.py capture note "Project fact: the agent uses ToolBroker for tools."
python smart_agent.py capture from-file workspace/research.txt
python smart_agent.py capture from-file workspace/my-note.txt --trusted-user
python smart_agent.py capture from-url "https://example.com"
python smart_agent.py capture list
python smart_agent.py capture summarize
python smart_agent.py capture promote-to-memory <capture_id>
```

Knowledge Capture v1 is a local workspace inbox, not Apple Notes. Captures are stored as JSON files under `./workspace/captures` through brokered `filesystem.write`, and source files are read through brokered `filesystem.read`. URL captures fetch explicit URLs through `web.fetch_url`; web content remains `UNTRUSTED_WEB`, and file captures are `UNTRUSTED_DOCUMENT` by default. Use `--trusted-user` only for user-authored workspace files you intentionally want labeled `TRUSTED_USER`. Secrets are rejected before capture storage. `promote-to-memory` reads the capture through `filesystem.read` and then calls `memory.store`, so Memory v2 policy decides whether the content may be stored; personal-looking content is blocked by default and no personal data is written to memory automatically.

Project file assistant:

```bash
python smart_agent.py files list workspace
python smart_agent.py files read workspace/note.txt
python smart_agent.py files summarize workspace/note.txt
python smart_agent.py files search "query" --path workspace
python smart_agent.py files write workspace/note.txt --content "hello"
python smart_agent.py files write workspace/note.txt --content "updated" --overwrite
python smart_agent.py files patch workspace/note.txt --old-text "hello" --new-text "hi"
python smart_agent.py files diff
```

File commands execute only through `ToolBroker` using the existing `filesystem.*` and `git.diff` tools. They are bounded to approved project roots, block path traversal, block `.env` and private macOS app folders, enforce file-size limits, audit reads/writes, and back up files before overwriting or patching. Read and summarized file content is labeled `UNTRUSTED_DOCUMENT`; document text is data only and cannot request tools or change policy. Delete remains approval-required through `filesystem.delete`; the file assistant CLI does not add a delete shortcut.

Self-improvement backlog:

```bash
python smart_agent.py improve backlog
python smart_agent.py improve propose
python smart_agent.py improve backlog --dry-run --json
python smart_agent.py improve implement <proposal_id>
python smart_agent.py improve run-tests
python smart_agent.py improve show-diff
python smart_agent.py improve overnight-plan
python smart_agent.py improve create-action-for-commit --message "Update docs"
python smart_agent.py improve commit --from-action <action_id>
```

The backlog/propose commands are read-only. They inspect an approved list of project docs, tests, capability config, self-improvement workflow files, and audit-log paths through brokered `filesystem.read` calls. Reads are audited, file contents are treated as `UNTRUSTED_DOCUMENT`, and dry-run mode evaluates the planned reads without reading file contents. Safety-weakening ideas such as disabling audit logs, relaxing ToolBroker/PolicyEngine checks, or enabling personal-data tools by default are reported as blocked suggestions.

The implementation loop is branch-based and requires an approved proposal record in `data/self_improvement/approved_proposals.json`. `improve implement <proposal_id>` creates or switches to a `codex/` branch, writes only approved project/workspace files through brokered `filesystem.write`, runs brokered tests, shows brokered diff, and creates a pending Action Center commit item. `improve create-action-for-commit` is the manual checkpoint: it runs brokered tests, shows brokered diff, and queues a pending Action Center commit action without committing. It blocks protected safety files, policy weakening, audit disabling, package installs without a separate approval gate, persistence paths, personal-data access grants, and send/write side effects. `improve commit --from-action <action_id>` executes only an approved Action Center commit action through `ToolBroker`; no commit happens from implement or create-action-for-commit alone.

Overnight self-improvement is planning-only unless explicitly approved. `improve overnight-plan` reads `docs/FEATURE_MATURITY.md`, `docs/PROJECT_STATE.md`, `docs/FEATURE_REGISTRY.md`, and `docs/FEATURE_ROADMAP.md` through `ToolBroker` and returns safe docs/tests/hardening candidates. It does not edit files, create a branch, schedule background work, run prompts, or commit. See `docs/SELF_IMPROVEMENT_OVERNIGHT_RUNBOOK.md` before any long unattended run.

Prompt tracking:

```bash
python smart_agent.py prompts list
python smart_agent.py prompts next
python smart_agent.py prompts show PROMPT-LEDGER-QUEUE
python smart_agent.py prompts add ./prompts/queued/example.md
python smart_agent.py prompts validate-pack ./prompt-pack.md
python smart_agent.py prompts import ./prompt-pack.md
python smart_agent.py prompts split ./prompt-pack.md
python smart_agent.py prompts mark-active NATIVE-SKILLS-FOUNDATION
python smart_agent.py prompts mark-complete NATIVE-SKILLS-FOUNDATION --test-result "passed" --docs-updated yes
python smart_agent.py prompts mark-superseded OLD-PROMPT --by NEW-PROMPT
python smart_agent.py prompts audit
python smart_agent.py prompts missing
```

Prompt tracking is SDLC metadata only. It reads `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, prompt record files under `prompts/<status>/`, and project tracking docs. It does not execute agent tools, add connectors, access personal data, send messages, or weaken policy. `mark-complete` requires test/docs status fields unless `--unknown` is used, so future runs cannot quietly mark prompts complete without evidence.

Prompt packs are documented in `docs/PROMPT_PACK_FORMAT.md`. `validate-pack` checks delimiters, metadata, unique ids/orders, dependencies, cycles, risk levels, and import-only mode without writing files. `import` and `split` are intentionally conservative: they copy the original pack into `prompts/packs/`, split individual prompts into `prompts/queued/`, append prompt ledger and queue rows, and add a prompt audit summary. Imported prompts are not executed automatically; `prompts next` returns only the next queued prompt whose dependencies are complete and whose approval gate is not blocking.

One-command PromptOps workflow:

```bash
pbpaste | python smart_agent.py work import --stdin --pack-id tonight
python smart_agent.py work import-clipboard --pack-id tonight
python smart_agent.py work import prompts/packs/messaging-track.md
pbpaste | python smart_agent.py work import --stdin --single --id QUICK-001 --pack-id quick
python smart_agent.py work next
python smart_agent.py work show-next
python smart_agent.py work copy-next
python smart_agent.py work run-next
python smart_agent.py work autopilot --safe-only --max-prompts 3
python smart_agent.py work review
```

PromptOps Workbench is documented in `docs/PROMPTOPS_WORKBENCH.md`. It imports prompt packs or raw prompts, updates the prompt ledger/queue/audit/project state, and helps copy or inspect the next safe prompt. `work run-next` is disabled unless `CODEX_RUNNER_ENABLED=true`; when disabled it writes a safe report and does not execute Codex. Autopilot is limited to safe categories, refuses HIGH/CRITICAL prompts, and stops at approval gates.

Command registry and manual QA:

```bash
python smart_agent.py commands list
python smart_agent.py commands show CMD-WEATHER-003
python smart_agent.py commands search weather
python smart_agent.py commands legacy
python smart_agent.py commands validate
python smart_agent.py commands qa-plan
python smart_agent.py commands qa-run Weather
```

The durable command catalog lives in `docs/COMMAND_REGISTRY.md`; manual test coverage lives in `docs/COMMAND_TEST_MATRIX.md`; deprecated and blocked paths live in `docs/COMMAND_LEGACY.md`; and the manual QA process lives in `docs/COMMAND_QA_RUNBOOK.md`. Use `commands qa-plan` to find commands that need manual testing, and log command bugs by adding bug IDs to the test matrix before creating regression tests.

Live session logging and replay:

```bash
python smart_agent.py session start --name "core-smoke"
python smart_agent.py session run -- --no-tools "Explain RCS vs iMessage"
python smart_agent.py session run -- weather current "Phoenix, AZ"
python smart_agent.py session replay --last
python smart_agent.py session review --last
python smart_agent.py session review --last --create-bugs
python smart_agent.py bugs list
python smart_agent.py session end
```

Session logs are redacted dogfooding records under `reports/sessions/`; raw session outputs are ignored by git. They are not a replacement for the security audit log and they do not create a new tool execution path. Wrapped commands keep their existing ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger behavior. See `docs/SESSION_LOGGING.md`.

Session review and bug generation are local QA tools. Reviews read redacted session command previews and feedback, write reports under `reports/session_reviews/`, and can create redacted bug JSON under `bugs/`. They do not send data externally, access personal connectors, fix bugs automatically, or write memory. See `docs/BUG_TRIAGE.md`.

Native skill vetting:

```bash
python smart_agent.py skills list
python smart_agent.py skills show native_skill_vetter
python smart_agent.py skills validate
python smart_agent.py skills doctor
python smart_agent.py skills find "I need to work with PDFs"
python smart_agent.py skills find "Can you help with meeting follow-up?"
python smart_agent.py skills vet ./workspace/skills/example/SKILL.md
python smart_agent.py skills vet-folder ./workspace/skills/example
python smart_agent.py skills score ./workspace/skills/example/SKILL.md
```

Native skill manifests are metadata-only workflow definitions under `native_skills/` or `docs/native_skills/manifests/`. The loader reads and validates manifest fields, required capabilities, risk/trust levels, memory behavior, audit requirements, personal-data defaults, and CRITICAL approval rules. It does not execute scripts, import external code, install marketplace skills, grant permissions, or let manifests bypass `ToolBroker`.

`skills find` searches only local reviewed metadata: native skill manifests, the native candidate matrix, feature registry, and maturity tracker. It returns implemented matches, planned candidates, maturity/readiness, required approvals, and next work needed. It does not browse external marketplaces, install skills, execute external code, or write memory.

Native skill vetting is static analysis only. It reads candidate skill files only from approved workspace paths, treats them as `UNTRUSTED_DOCUMENT`, parses `SKILL.md` frontmatter when present, and flags scripts, shell commands, package installs, network calls, secret references, filesystem escapes, personal-data access, browser cookie/session access, prompt-injection language, approval-bypass language, opaque binaries, and missing license information. The vetter never executes scripts, installs dependencies, grants permissions, or stores skill content in memory by default. All vetting commands execute through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

PDF workspace native skill:

```bash
python smart_agent.py pdf info ./workspace/file.pdf
python smart_agent.py pdf extract-text ./workspace/file.pdf
python smart_agent.py pdf summarize ./workspace/file.pdf
python smart_agent.py pdf extract-tables ./workspace/file.pdf
```

PDF operations are workspace-bounded, audited, and labeled `UNTRUSTED_DOCUMENT`. OCR, split/merge, generated PDF writes, and external binaries are not enabled in v1. The PDF skill uses embedded text extraction only and does not store document content in memory by default.

Scheduler / Automation v1:

```bash
python smart_agent.py schedule list
python smart_agent.py schedule create --workflow connector_doctor --schedule daily@08:00 --name "Connector doctor"
python smart_agent.py schedule create --workflow daily_briefing --arg sections=weather --arg weather_location="Phoenix, AZ"
python smart_agent.py schedule create --workflow backup_create --arg backup_dir=workspace/backups
python smart_agent.py schedule run <schedule_id>
python smart_agent.py schedule pause <schedule_id>
python smart_agent.py schedule delete <schedule_id>
```

Scheduler v1 is manual-run only: it stores explicit local schedule records and never installs a LaunchAgent, cron job, daemon, login item, or hidden background runner. Scheduled workflows still use the existing safety path where tools are involved; personal-data sections require approval, CRITICAL actions are never executed automatically, and scheduled backups are redacted-only brokered `backup.create` calls. Details live in `docs/SCHEDULER.md`.

Weather-aware research:

Simple weather prompts use weather tools only. Weather-impact prompts that need current public context, such as flight delays, school closures, or latest hurricane updates, may attach `web.search` in addition to weather tools when web search is configured. Web content remains `UNTRUSTED_WEB`, weather provider data and web results stay separated in workflow output, and the agent must not claim current closures or delays without web sources. Requests such as "near me" or "my area" do not infer personal location; configure an explicit default location first or provide a location in the request.

Weather provider abstraction:

```bash
python smart_agent.py weather doctor
python smart_agent.py weather smoke "Phoenix, AZ"
python smart_agent.py weather current "San Francisco"
python smart_agent.py weather current "Phoenix, AZ" --no-cache
python smart_agent.py weather forecast "San Francisco" --days 3
python smart_agent.py weather alerts "Los Angeles, CA" --provider nws
python smart_agent.py weather config show
python smart_agent.py weather config set-default "Phoenix, AZ"
python smart_agent.py weather config clear-default
python smart_agent.py weather cache clear
```

`weather.status`, `weather.current`, `weather.forecast`, `weather.alerts`, and `weather.cache_clear` are LOW-risk, audited, rate-limited, ToolBroker-only capabilities for user-provided locations. The `doctor` command checks provider configuration and capability policy without fetching weather data. The `smoke` command runs `weather.status`, `weather.current`, and `weather.forecast` through the broker for a user-provided location. Open-Meteo is used when `WEATHER_PROVIDER` is unset; `WEATHER_PROVIDER=disabled` returns structured `weather provider is not configured` JSON.

Open-Meteo is the default no-key provider:

```bash
export WEB_ACCESS_ENABLED=true
export WEATHER_PROVIDER=open_meteo
python smart_agent.py weather doctor
python smart_agent.py weather smoke "San Francisco"
python smart_agent.py weather current "San Francisco"
python smart_agent.py weather forecast "San Francisco" --days 3
python smart_agent.py weather forecast "33.4484,-112.0740" --days 3 --hourly
```

NOAA/National Weather Service is available as a U.S.-only no-key provider. It uses user-provided locations, Open-Meteo geocoding for coordinates, and `api.weather.gov` points/grid/alerts endpoints. It does not use device location or IP geolocation.

```bash
python smart_agent.py weather current "Los Angeles, CA" --provider nws
python smart_agent.py weather forecast "Los Angeles, CA" --provider nws --days 3 --hourly
python smart_agent.py weather alerts "Los Angeles, CA" --provider nws
```

WeatherKit is documented as an optional planning stub only. `WEATHER_PROVIDER=weatherkit` checks whether Apple Developer credential env vars are present, but it does not sign JWTs or call Apple yet. Review [docs/decisions/weatherkit_provider.md](</Users/sambehdjou/Documents/AI Super Agent/docs/decisions/weatherkit_provider.md>) before implementing full WeatherKit support.

Direct `weather current`, `weather forecast`, and `weather alerts` commands print a readable answer with current conditions, daily forecast, active alert summaries, umbrella/clothing guidance when data supports it, alert availability, cache warnings, uncertainty, provider, and `retrieved_at`. Add `--json` to inspect the structured provider payload instead.

The weather tools do not use macOS Location Services, IP geolocation, personal data, writes, or long-term memory storage. Location arguments are redacted from audit logs by default. Open-Meteo geocoding, Open-Meteo forecast responses, and NWS responses are treated as `UNTRUSTED_WEB`. To disable weather entirely, set `WEATHER_PROVIDER=disabled`.

Natural-language weather requests route to weather tools only when they include a location, such as "What's the weather in Phoenix?" or "Is it going to rain tomorrow in LA?". Requests like "near me" do not infer personal location. To allow location-less weather questions, explicitly set `WEATHER_DEFAULT_LOCATION`, `WEATHER_DEFAULT_LATITUDE` plus `WEATHER_DEFAULT_LONGITUDE`, or run `python smart_agent.py weather config set-default "Phoenix, AZ"`. Default location use is audited with the source of the setting, while the location value remains redacted from audit args.

Weather responses are cached in a short-lived local TTL cache at `WEATHER_CACHE_PATH` using hashed keys. Defaults are 900 seconds for current weather and 3600 seconds for forecasts; `WEATHER_CACHE_TTL_SECONDS` can override both, and `WEATHER_CACHE_ENABLED=false` disables caching. Use `--no-cache` to bypass cache for a request, or `python smart_agent.py weather cache clear` to clear cached weather responses. This cache is separate from long-term memory.

Daily Briefing v2:

```bash
python smart_agent.py briefing daily --weather "Phoenix, AZ"
python smart_agent.py briefing daily --weather-default
python smart_agent.py briefing daily --sections weather,calendar,tasks,email,web,memory,suggested_actions --web-topic "local AI news"
python smart_agent.py briefing daily --weather "Phoenix, AZ" --calendar --dry-run
python smart_agent.py briefing config show
python smart_agent.py briefing config set sections=weather,memory weather_location="Phoenix, AZ" web_topics="local AI,weather safety"
```

Daily Briefing v2 uses only explicitly selected or configured sections. Weather calls use `weather.current`, `weather.forecast`, and `weather.alerts`; web topics use `web.search`; calendar uses today's selected `calendar.read_date_range`; tasks use selected-scope `tasks.list`; email uses `email.list_metadata` only; memory uses non-personal preference search. Every tool step goes through `ToolBroker`, policy, approval where required, and audit logging. Calendar, tasks, and email metadata remain HIGH risk and are skipped if approval or configuration is missing. Suggested actions create pending Action Center items and are not executed by the briefing. The briefing does not read email bodies, messages, contacts, browser history, or private app folders, does not perform writes/sends, and does not write memory by default. `--weather` without a location and `--weather-default` require an explicit `WEATHER_DEFAULT_LOCATION`; no system or IP location is inferred.

Connector status dashboard:

```bash
python smart_agent.py connectors list
python smart_agent.py connectors doctor
python smart_agent.py connectors status weather
python smart_agent.py connectors status web
python smart_agent.py connectors status calendar
python smart_agent.py connectors status contacts
python smart_agent.py connectors status email
python smart_agent.py connectors status messages
```

The connector dashboard is read-only. It reports connector name, configuration, enabled state, default provider, normalized capabilities, risk level, approval requirement, rate-limit configuration, last audited success/error, cache state, and setup hints. It does not reveal secrets and does not perform personal-data reads; personal connectors are checked from configuration only.

Connector status now runs through the reusable `agent.connectors` framework:

- `agent/connectors/base.py` defines connector metadata, configuration, health, and status models.
- `agent/connectors/registry.py` registers connector definitions for weather, web, calendar, contacts, email, and messages.
- `agent/connectors/status.py` normalizes status output, redacts secrets, reads audit success/error state, and reports rate/cache metadata.
- `agent/connectors/health.py` provides safe health/status reports without executing connector actions.

This framework is metadata-only. It does not execute tools or connector actions; runtime actions still go through `ToolBroker`, `PolicyEngine`, approval handling where applicable, and `AuditLogger`.

Calendar read-only selected-range access:

```bash
python smart_agent.py calendar read --start 2026-05-22 --end 2026-05-23
python smart_agent.py calendar availability --start 2026-05-22 --end 2026-05-23 --duration 30
```

Calendar tools are HIGH risk, disabled by default, approval-required, and selected-range only. The optional connector path is Calendar.app through AppleScript:

```bash
export CALENDAR_CONNECTOR=applescript
```

This adapter uses macOS Calendar/Automation privacy prompts. It does not scrape private Calendar databases and does not require Full Disk Access. Event notes are not returned, locations are redacted unless `CALENDAR_INCLUDE_LOCATIONS=true`, availability returns slots without event details, calendar event text is labeled as data rather than instructions, and calendar results are not stored in long-term memory by default.

Calendar approved writes v1:

```bash
python smart_agent.py calendar draft-create --title "Planning" --start 2026-05-22T10:00 --end 2026-05-22T10:30 --calendar "Work"
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py calendar create --from-action <action_id>

python smart_agent.py calendar draft-update <event_id> --title "New title"
python smart_agent.py calendar update --from-action <action_id>

python smart_agent.py calendar draft-delete <event_id>
python smart_agent.py calendar delete --from-action <action_id>
```

Calendar write capabilities remain disabled by default in `config/capabilities.yaml` and are CRITICAL per-action approval capabilities. Draft commands create Action Center records only; they do not create, update, delete, or invite anyone. `create/update/delete --from-action` requires an approved Action Center record and still executes through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`. The low-level write tools reject direct broker calls unless Action Center verifies the matching approved action id. Approved actions are consumed once. The current write connector is a no-external-change stub unless a future safe native write provider is explicitly configured and release-gated. Notes/body text is omitted from drafts unless `--allow-notes` is provided, recurring events are not supported in v1, and automatic invites are disabled.

Reminders / Tasks connector:

```bash
python smart_agent.py tasks list
python smart_agent.py tasks draft-create "Follow up with Alex" --due 2026-05-23 --source-workflow meeting_prep
python smart_agent.py actions approve <action_id>
python smart_agent.py tasks create --from-action <action_id>
python smart_agent.py tasks complete <task_id>
python smart_agent.py tasks update <task_id> --title "Updated title"
python smart_agent.py tasks delete <task_id>
```

Tasks tools are personal-data tools and disabled by default when they access or mutate a task provider. `tasks.list` is HIGH risk and approval-required. `tasks.create`, `tasks.update`, `tasks.complete`, and `tasks.delete` are CRITICAL per-action approval tools. `draft-create` now routes through the brokered `tasks.draft_create` capability, creates an Action Center record only, and does not access a task provider or create a real reminder. `create --from-action` consumes one approved action and then calls `tasks.create` through `ToolBroker`. The current connector is adapter-first with a mock provider for tests; no native Reminders database scraping, no broad Full Disk Access, and no live macOS Reminders write path are enabled. Task contents are not stored in memory by default, notes are omitted unless explicitly allowed, and no full task export is performed.

Personal task extraction:

```bash
python smart_agent.py tasks extract --from-notes ./workspace/notes.md
python smart_agent.py tasks extract --from-email-thread "<thread_id>"
python smart_agent.py tasks extract --from-meeting "<event_id>"
python smart_agent.py tasks extract --dry-run --from-notes ./workspace/notes.md --json
```

Task extraction reads exactly one selected source through its existing brokered tool: workspace notes and captures use `filesystem.read`, selected email threads use `email.read_selected_thread`, selected meetings use `calendar.read_selected_event`, and selected URLs use `web.fetch_url`. Personal sources require approval. Source content is treated as untrusted data and instruction-like lines are ignored; extracted candidates become pending `tasks.create` Action Center records only. The workflow does not create tasks, send email/texts, write calendar/contact data, or write memory by default. Review, edit, approve, or deny each task from Action Center before any task connector write can execute.

Meeting prep workflow:

```bash
python smart_agent.py meeting prep --event-id "<event_id>"
python smart_agent.py meeting prep --date 2026-05-22 --title "Roadmap Sync"
python smart_agent.py meeting prep --date 2026-05-22 --title "Roadmap Sync" --contact "Alex" --web-topic "Acme roadmap"
python smart_agent.py meeting prep --date 2026-05-22 --title "Roadmap Sync" --dry-run
```

Meeting prep reads one selected calendar event through `calendar.read_selected_event`, then optionally runs approved `contacts.search` calls and public `web.search`. It produces a meeting summary, attendee/context notes, suggested agenda, questions, and a prep checklist. The event id is the selected event token returned by calendar range reads. Calendar/contact data remains `LOCAL_PRIVATE_DATA`; web content remains `UNTRUSTED_WEB`. The workflow sends no emails or texts, performs no calendar/contact edits, does no bulk contact export, and writes no long-term memory by default.

Meeting follow-up workflow:

```bash
python smart_agent.py meeting follow-up --event-id "<event_id>"
python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md
python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md --contact "Alex"
python smart_agent.py meeting follow-up --notes-file ./workspace/notes.md --dry-run --json
```

Meeting follow-up can read one selected calendar event after approval and/or one workspace-bounded notes file through `filesystem.read`. Notes are treated as `UNTRUSTED_DOCUMENT` data, and instruction-like lines such as requests to ignore policy, reveal secrets, call tools, send messages, or disable audit logs are filtered before deterministic synthesis. The workflow produces a meeting summary, decisions, action items, suggested tasks, a draft follow-up email, and optional calendar update suggestions. Suggested tasks, email sends, and calendar updates become pending Action Center records only; the workflow executes no task creation, email send, calendar write, contact edit, or memory write. The draft email uses `review-required@example.invalid` as a placeholder recipient until the user edits the Action Center item.

Contacts read-only selected-scope access:

```bash
python smart_agent.py contacts search "Sam" --max-results 5
python smart_agent.py contacts read "<contact_id>"
```

Contacts tools are HIGH risk, disabled by default, approval-required, and selected-scope only. The optional connector path is Contacts.app through AppleScript:

```bash
export CONTACTS_CONNECTOR=applescript
```

This adapter uses macOS Contacts/Automation privacy prompts. It does not scrape private AddressBook databases and does not require Full Disk Access. Search returns compact candidates only: name, organization, job title, counts/flags, and a selected-scope token. It does not return email addresses or phone numbers from search results. Reading a selected contact returns only requested fields; notes are never returned, contact text is labeled as data rather than instructions, and email, phone, and address values are returned only when requested, approved, and their explicit config gates are enabled.

Contacts approved edits:

```bash
python smart_agent.py contacts draft-update "<contact_id>" --set company=NewCo --old company=OldCo
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py contacts update --from-action <action_id>

python smart_agent.py contacts draft-create --display-name "Sam Example" --field company=ExampleCo
python smart_agent.py contacts create --from-action <action_id>
```

Contact write capabilities remain disabled by default and are CRITICAL per-action approval capabilities. Draft commands create Action Center records only; they do not edit or create Contacts.app records. `update/create --from-action` requires one approved Action Center record and still executes through `ToolBroker`, `PolicyEngine`, `ApprovalManager`, and `AuditLogger`; direct broker calls without the verified Action Center action id are denied. The submitted write arguments must match the approved preview. The current connector is a safe no-external-change stub until a native write provider is separately designed and release-gated. Updates require explicit field-level diffs, sensitive phone/email/address values are redacted in stored previews and audit logs, bulk edits are denied, contact deletion is deferred, and contact details are not written to memory by default.

Email assistant metadata, selected-thread, and draft-only access:

```bash
python smart_agent.py email metadata
python smart_agent.py email triage
python smart_agent.py email triage --selected-thread "<thread_id>"
python smart_agent.py email read "<thread_id>"
python smart_agent.py email summarize "<thread_id>"
python smart_agent.py email draft-reply "<thread_id>"
```

Email tools are disabled by default and approval-gated. The optional first adapter is IMAP:

```bash
export EMAIL_CONNECTOR=imap
export IMAP_HOST="imap.example.com"
export IMAP_USERNAME="you@example.com"
export IMAP_PASSWORD="use-an-app-password-or-external-secret"
```

Credentials are read from the environment or an external secret setup; the agent does not store passwords. Metadata listing and `email triage` return headers only and no body, classify likely priority from metadata, and label email metadata `UNTRUSTED_EMAIL` because sender and subject text can contain instructions. `email triage --selected-thread "<thread_id>"` reads one selected thread only after approval, summarizes it, and creates a draft reply. Selected thread bodies are wrapped as `UNTRUSTED_EMAIL`, omitted from the triage report, and not stored in long-term memory. Draft replies are marked draft-only and never send, delete, move, archive, or approve actions.

Email approved send:

```bash
python smart_agent.py email draft-new --to sam@example.com --subject "Reviewed subject" --body "Full reviewed body"
python smart_agent.py email draft-reply "<thread_id>" --to sam@example.com --subject "Re: Reviewed subject" --body "Full reviewed body"
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py email send --from-action <action_id>
```

`email.send_approved` is disabled by default and is CRITICAL per-action approval only. A send must originate from an Action Center item; direct broker calls without the verified Action Center action id are blocked, and submitted send arguments must match the approved reviewed draft. The preflight shows from account/provider, to, cc, bcc, subject, full body, attachments, thread/reply context, and rollback impossibility. Editing an action through `actions edit` invalidates prior approval. Bulk sends are denied, attachments are blocked in v1, no background sends are available, and email thread content remains `UNTRUSTED_EMAIL` data that cannot approve or instruct sending. The default send provider is not configured; tests may use the mock provider, and a real provider must be separately designed without hard-coded credentials or private Mail database scraping.

Messages/text assistant selected-thread stubs and manual draft-only access:

```bash
python smart_agent.py messages read "<thread_id>"
python smart_agent.py messages summarize "<thread_id>"
python smart_agent.py messages draft-reply "<thread_id>"
python smart_agent.py messages draft-from-text --to "Name" --context-file ./workspace/thread.txt
python smart_agent.py actions approve <action_id>
python smart_agent.py messages save-draft --from-action <action_id>
python smart_agent.py messages copy-draft --from-action <action_id>
```

Messages tools are disabled by default and approval-gated. There is intentionally no live macOS Messages connector yet: the project does not scrape `~/Library/Messages`, does not request broad Full Disk Access, and does not bulk-read history. The safe fallback is the brokered `messages.draft_from_text` capability using a manually provided UTF-8 text file inside `./workspace`; its content is treated as `UNTRUSTED_MESSAGE`, audited as a file read, labeled as data rather than instructions, not stored in long-term memory, and used only to create a draft. Draft replies are marked draft-only and never send, delete, move, archive, harvest contacts, or modify messages.

Messages safe handoff:

`messages draft-from-text` now queues reviewed Action Center handoff records for saving the draft to `./workspace` or copying it to the clipboard. `messages.save_draft` and `messages.copy_draft` are disabled by default, HIGH risk, approval-required, and never send a message. Low-level save/copy tool execution requires the verified Action Center action id, and submitted recipient/draft/path arguments must match the approved preview. Saved drafts must remain inside approved workspace paths. Clipboard copy requires an approved Action Center item because clipboard contents may be personal data and can be read by other local apps. Automatic Messages/iMessage/SMS sending is deferred; see `docs/decisions/messages_send_path.md`.

Memory tools:

```bash
python smart_agent.py --debug "Remember that I prefer concise answers"
python smart_agent.py memory add --category user_preference --content "User prefers concise answers."
python smart_agent.py memory add --category project_fact --scope agent --content "Project uses ToolBroker for tools."
python smart_agent.py memory add --category workflow_lesson --content "Run tests after safety changes."
python smart_agent.py memory list
python smart_agent.py memory search "ToolBroker" --category project_fact
python smart_agent.py memory export
python smart_agent.py memory delete <id>
python smart_agent.py memory clear
python smart_agent.py memory context "ToolBroker" --max-chars 1200
```

Memory refuses secrets and personal email/message/contact/calendar content by default. Approval-gated personal memory exists as a separate capability. Memory search supports category filters, and context injection is bounded, non-personal by default, and audited with the injected memory IDs. Deletion is best effort: SQLite rows are deleted and `VACUUM` is attempted, but external logs and filesystem backups are not rewritten.

Inspection commands:

```bash
python smart_agent.py dashboard
python smart_agent.py dashboard --json
python smart_agent.py status
python smart_agent.py tools list
python smart_agent.py doctor
python smart_agent.py permissions show
python smart_agent.py approvals list
python smart_agent.py approvals show <request_id>
python smart_agent.py approvals approve <request_id>
python smart_agent.py approvals deny <request_id>
python smart_agent.py preflight "calendar.create_event"
python smart_agent.py audit tail
python smart_agent.py privacy status
python smart_agent.py privacy inventory
python smart_agent.py privacy export
python smart_agent.py privacy delete-memory --confirm DELETE-MEMORY
python smart_agent.py privacy audit-summary
python smart_agent.py privacy permissions
python smart_agent.py backup create
python smart_agent.py backup list
python smart_agent.py backup inspect <backup_id>
python smart_agent.py backup verify <backup_id>
python smart_agent.py backup export --redacted
python smart_agent.py backup restore <backup_id>
python smart_agent.py memory list
python smart_agent.py config show
python smart_agent.py setup
```

`dashboard` and `status` are read-only CLI views. They do not send prompts to the model, attach tools, execute connector actions, read personal data, grant permissions, consume approvals, or start background work. The dashboard reports current model/config, LM Studio status from doctor checks, enabled tool metadata, connector metadata/status, permission grants, pending approvals, recent audit metadata, memory counts without memory content, risk-setting summaries, last recorded test result, and setup hints. Secrets are redacted, and personal connectors are shown from configuration/status metadata only.

Privacy Center v1 gives a local data inventory without reading personal connectors. `privacy status` and `privacy inventory` report enabled/disabled connectors, personal-data capability metadata, memory category counts, capture counts, audit log path/size, weather/web cache metadata, pending personal-data actions, approval counts, permission grants, and deletion options. `privacy export` emits a redacted local report with memory/capture previews only; secrets are redacted by default. `privacy delete-memory` requires `--confirm DELETE-MEMORY` and clears memory through the brokered `memory.clear` path, so policy and audit still apply. Privacy reports explain that calendar/contact/email/message/task contents are not read from providers and external logs/backups are not rewritten by memory deletion.

Backup / Restore:

```bash
python smart_agent.py backup create
python smart_agent.py backup create --include-captures --include-audit-metadata
python smart_agent.py backup list
python smart_agent.py backup inspect <backup_id>
python smart_agent.py backup verify <backup_id>
python smart_agent.py backup export --redacted
python smart_agent.py backup restore <backup_id>
```

Backups are local redacted archive directories under `workspace/backups` by default, or under `BACKUP_DIR` / `--backup-dir` when explicitly configured. Backup v1 includes config with secrets redacted, docs/tracking files, feature registry/maturity/roadmap, native skill manifests, redacted memory export metadata, redacted Action Center metadata, optional captures, and optional audit metadata. It never fetches personal connector data and does not store or export API keys, tokens, `.env`, private keys, raw mail/messages/calendar/contact data, or browser/session data. Each archive has `manifest.json` with content hashes and an integrity hash. `backup restore` is HIGH risk, approval-gated, verifies hashes first, creates pre-restore copies where possible, and rejects backed-up capability manifests that would weaken policy or enable personal connectors.

The `doctor` command does not send prompts to the model, attach tools, access personal data, change config, or grant permissions. It checks Python, required imports, runtime config, `LMSTUDIO_BASE_URL`, `LMSTUDIO_MODEL`, LM Studio reachability, `/v1/models`, selected model availability when confirmable, startup policy validation, normalized capability manifest validation, audit path writability, tool registry loading, `ToolBroker` initialization, connector registry loading, whether personal-data tools are disabled by default, and whether any CRITICAL actions are enabled by default.

Approval commands inspect and update the local approval queue at `data/approvals.json`. Approval-required tool calls still execute only through `ToolBroker`; approving a queued request does not replay or execute an old tool call. In non-interactive mode, approval-required actions are denied safely and audited. Critical actions are per-action only and do not support approval reuse.

Unified Action Center:

```bash
python smart_agent.py actions list
python smart_agent.py actions show <action_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py actions deny <action_id>
python smart_agent.py actions edit <action_id> key=value
python smart_agent.py actions clear-denied
python smart_agent.py actions export
```

Action Center is the review surface for future risky actions such as calendar writes, contact edits, email sends, message sends, personal memory writes, file deletes, git commits, and self-improvement commits. It stores exact secret-redacted previews, rollback notes, approval state, source workflow, and audit references in `data/actions.json` so the user can review exact action details locally before approval. `actions export` and lifecycle audit events use minimized/redacted views of sensitive action bodies and drafts. Action Center does not execute actions directly. Approving an action marks it review-approved once; any real execution must still go through `ToolBroker`, `PolicyEngine`, the approval rules for that capability, and `AuditLogger`. CRITICAL actions remain per-action only, edits invalidate previous approvals, irreversible actions say rollback is unavailable, and non-interactive mode must not execute pending actions.

Interactive mode:

```bash
python smart_agent.py --interactive
```

Inside interactive mode:

```text
:help
:doctor
:tools
:config
:no-tools on
:no-tools off
:debug on
:debug off
:approvals
:approvals <request_id>
:exit
```

Interactive commands such as `:doctor`, `:tools`, `:config`, and `:approvals` do not send prompts to the model. Normal chat turns still use the same orchestrator, router, `ToolBroker`, policy engine, approval manager, and audit logger as one-shot CLI requests. If a live interactive tool call requires approval, the CLI shows the approval preview and waits for `approve once`, `deny`, `abort`, or `show details`. Critical actions still allow only per-action approval.

## Local Startup

This project requires Python 3.11 or newer. macOS may run Apple Python 3.9 when you type `python3`; that version is not supported. `smart_agent.py` now checks the Python version before importing agent modules and prints setup commands instead of crashing.

Recommended local setup:

```bash
cd "/Users/sambehdjou/Documents/AI Super Agent"
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

If `python3.11` is not installed:

```bash
brew install python@3.11
```

Use the local launcher after setup:

```bash
./scripts/agent doctor
./scripts/agent --no-tools "Explain RCS vs iMessage"
```

The launcher prefers `AI_AGENT_PYTHON`, then `./.venv/bin/python`, then the bundled Codex Python runtime if present, and only falls back to system `python3` when it is Python 3.11+.

LM Studio setup:

```bash
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
curl http://localhost:1234/v1/models
export LMSTUDIO_MODEL="<model id from /v1/models>"
./scripts/agent doctor
```

For Qwopus in the current local setup, the model id has been:

```bash
export LMSTUDIO_MODEL="qwopus3.6-35b-a3b-v1@q5_k_m"
```

## Runtime Config

Supported environment variables:

```bash
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=qwopus3.6-35b-a3b-v1@q5_k_m
TEMPERATURE=0.7
TOP_P=0.95
MAX_TOKENS=2048
TOOL_MODE=auto
DEBUG=false
AUDIT_LOG_PATH=logs/audit.jsonl
CAPABILITIES_CONFIG=config/capabilities.yaml
WEB_ACCESS_ENABLED=true
WEB_SEARCH_PROVIDER=brave
BRAVE_SEARCH_API_KEY=
WEB_SEARCH_TIMEOUT_SECONDS=10
WEB_SEARCH_MAX_RESULTS=8
WEB_SAFE_SEARCH=true
WEB_SEARCH_AUDIT_QUERIES=false
WEB_FETCH_MAX_BYTES=500000
WEATHER_PROVIDER=open_meteo
WEATHERKIT_TEAM_ID=
WEATHERKIT_SERVICE_ID=
WEATHERKIT_KEY_ID=
WEATHERKIT_PRIVATE_KEY_PATH=
WEATHER_TIMEOUT_SECONDS=10
WEATHER_MAX_FORECAST_DAYS=7
WEATHER_UNITS=metric
WEATHER_DEFAULT_UNITS=metric
WEATHER_DEFAULT_LOCATION=
WEATHER_DEFAULT_LATITUDE=
WEATHER_DEFAULT_LONGITUDE=
WEATHER_PREFERENCES_PATH=config/weather_preferences.json
WEATHER_CACHE_ENABLED=true
WEATHER_CACHE_TTL_SECONDS=
WEATHER_CACHE_PATH=data/weather_cache.json
WEATHER_CURRENT_CACHE_TTL_SECONDS=900
WEATHER_FORECAST_CACHE_TTL_SECONDS=3600
CALENDAR_CONNECTOR=
CALENDAR_MAX_RANGE_DAYS=31
CALENDAR_INCLUDE_LOCATIONS=false
CONTACTS_CONNECTOR=
CONTACTS_MAX_SEARCH_RESULTS=5
CONTACTS_INCLUDE_EMAILS=false
CONTACTS_INCLUDE_PHONES=false
CONTACTS_INCLUDE_ADDRESSES=false
EMAIL_CONNECTOR=
EMAIL_METADATA_MAX_RESULTS=10
EMAIL_METADATA_SNIPPETS=false
EMAIL_THREAD_MAX_CHARS=12000
IMAP_HOST=
IMAP_PORT=993
IMAP_USERNAME=
IMAP_PASSWORD=
IMAP_MAILBOX=INBOX
```

`TOOL_MODE` may be `auto`, `no-tools`, or `force-time`. The older `LMSTUDIO_TEMPERATURE`, `LMSTUDIO_TOP_P`, `LMSTUDIO_MAX_TOKENS`, and `AGENT_AUDIT_LOG` names are still accepted as fallbacks.

## LM Studio Smoke Test

Start LM Studio Developer Server at `http://localhost:1234/v1`, load Qwopus, then run:

```bash
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
curl http://localhost:1234/v1/models
export LMSTUDIO_MODEL="qwopus3.6-35b-a3b-v1@q5_k_m"

./scripts/agent --no-tools "Explain RCS vs iMessage"
./scripts/agent --debug "What time is it?"
```

Optional readiness check:

```bash
./scripts/agent doctor
```

Controlled smoke harness:

```bash
./scripts/agent smoke --lmstudio
./scripts/agent smoke --web
./scripts/agent smoke --calendar --contacts
./scripts/agent smoke --all-safe
./scripts/agent smoke --all-safe --dry-run
```

Expected result:

- The first command answers naturally and attaches no tools.
- The second command prints route/tool-call/policy/audit debug details and lets the model request the safe time tool through `ToolBroker`.
- `smoke --lmstudio` sends minimal live prompts only when `LMSTUDIO_MODEL` is set; otherwise it reports a skipped check.
- `smoke --web` uses the configured web provider if present and fetches `https://example.com` as a safe public page.
- `smoke --calendar --contacts` is dry-run/check-only by default. It checks connector configuration and policy state but does not read personal data.

## Live Eval Harness

The eval harness runs controlled validation checks for features that already exist. It is intended to move beyond mocked tests while keeping personal data out of the default path.

```bash
python smart_agent.py eval list
python smart_agent.py eval run --safe
python smart_agent.py eval run --routing
python smart_agent.py eval run --policy
python smart_agent.py eval run --tools
python smart_agent.py eval run --workflows
python smart_agent.py eval run --prompt-injection
python smart_agent.py eval run --lmstudio-live
python smart_agent.py eval run --web
python smart_agent.py eval run --weather
python smart_agent.py eval run --workspace
python smart_agent.py eval run --memory
python smart_agent.py eval report
```

`eval run --safe` now runs the Golden Eval Suite: data-file backed router checks, policy allow/ask/deny checks, ToolBroker denial/allow checks, prompt-injection wrapper checks, workflow dry-runs, no-tool LM Studio chat when `LMSTUDIO_MODEL` is configured, safe time-tool execution, weather current/forecast when a provider is configured, web search/fetch when configured, controlled workspace read/write under `./workspace/eval`, non-sensitive memory add/search/delete, dry-run/preflight, and connector doctor checks. Personal-data evals for calendar, contacts, email, and messages are skipped by default.

Golden cases live in `eval_cases/` so regression prompts, expected routes, and policy expectations can be reviewed as data. Eval runs produce structured pass/fail/skipped results, category scorecards, `logs/eval_results.json`, per-run JSON under `reports/evals/`, and [docs/EVAL_REPORT.md](</Users/sambehdjou/Documents/AI Super Agent/docs/EVAL_REPORT.md>). Tool actions execute through `ToolBroker` and are audited. Evals do not send emails/texts, do not write calendar/contact data, do not infer location, and do not store personal data in memory.

### Model Router and Prompt Quality Evals

These commands benchmark router choices, policy expectations, and system/untrusted-content prompt guardrails from reviewed fixture prompts. They do not send prompts to LM Studio by default and do not access personal data.

```bash
python smart_agent.py models list
python smart_agent.py models benchmark --safe
python smart_agent.py router eval
python smart_agent.py prompts eval
python smart_agent.py prompts report
```

`models benchmark --safe` covers normal no-tool chat routing, weather routing, web/current-info routing, URL/document routing, memory query routing, personal-data request routing, refusal/approval-gate behavior, prompt-injection handling, and answer-quality guardrails. The live answer-quality smoke case is skipped unless `--live` is passed and `LMSTUDIO_MODEL` is configured. Results are written to `logs/model_router_prompt_quality.json`, per-run JSON under `reports/evals/`, and [docs/PROMPT_QUALITY_REPORT.md](</Users/sambehdjou/Documents/AI Super Agent/docs/PROMPT_QUALITY_REPORT.md>).

If LM Studio is not running, the CLI should say:

```text
LM Studio server not reachable at http://localhost:1234/v1. Start LM Studio Developer Server and retry.
```

If the model variable is missing, the CLI should say:

```text
LMSTUDIO_MODEL is not set. Export LMSTUDIO_MODEL='<model id>'.
```

## Manual Dogfood Suites

Dogfood suites are curated command lists for systematic manual QA. They run existing `smart_agent.py` commands and keep each command's normal ToolBroker, policy, approval, and audit behavior. They do not enable personal-data tools or run personal-data reads by default.

```bash
python smart_agent.py dogfood list
python smart_agent.py dogfood show all_safe
python smart_agent.py dogfood run all_safe --dry-run
python smart_agent.py dogfood run all_safe
python smart_agent.py session start --name dogfood-all-safe
python smart_agent.py dogfood run all_safe --session
python smart_agent.py session replay --last
python smart_agent.py session end
```

Suites live in `dogfood_suites/` and are documented in [docs/dogfood/DOGFOOD_GUIDE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/DOGFOOD_GUIDE.md>) and [docs/dogfood/COMMAND_SUITES.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/COMMAND_SUITES.md>). Start with `all_safe`; use `personal_dry_run` only for preflight-only personal connector checks.

## Test Environments

Default tests are local and should not require live services or personal data:

```bash
$PY -m pytest -q
```

Pytest markers are registered for `unit`, `integration`, `live_lmstudio`, `live_web`, `live_calendar`, `live_contacts`, `requires_approval`, and `personal_data`. The default pytest configuration excludes tests marked `personal_data`.

Examples:

```bash
$PY -m pytest -m unit
$PY -m pytest -m integration
$PY -m pytest -m live_lmstudio
$PY -m pytest -m live_web
```

Personal-data tests must stay opt-in and should use test fixtures or explicitly selected non-production records only:

```bash
$PY -m pytest -m personal_data
```

Live smoke prerequisites:

- LM Studio: set `LMSTUDIO_MODEL` and start the Developer Server.
- Web search: set `WEB_SEARCH_PROVIDER=brave` and `BRAVE_SEARCH_API_KEY`, or expect search to be skipped.
- Calendar/contacts: keep dry-run unless you intentionally enable the disabled read-only capabilities and approve selected-scope access.

## Architecture

Runtime flow:

```text
User request
-> Orchestrator
-> Router
-> LLM
-> optional tool request
-> ToolBroker
-> PolicyEngine
-> PermissionManager/ApprovalManager when present
-> tool execution
-> AuditLogger
-> tool result
-> LLM final answer
```

The model writes final answers. The harness executes only validated tool calls through `ToolBroker`.

## Safety Boundaries

- Unknown tools are denied.
- Unknown capabilities are denied.
- Forbidden actions are denied.
- Higher-risk actions require approval and are denied safely in non-interactive mode.
- Tool calls and denials are audited.
- Approval lifecycle events are audited: requested, displayed, approved, denied, expired/aborted, used, and final execution/denial.
- Dry-run mode evaluates tool calls without execution and records dry-run audit events.
- Webpage content is wrapped as untrusted data.
- Long-term memory refuses secrets and personal content by default.
- Personal modules are disabled by default and selected-scope only.
- Calendar read-only access is selected-range only, approval-gated, and uses macOS privacy prompts when configured.
- Contacts read-only access is selected-scope only, approval-gated, compact in search mode, and uses macOS privacy prompts when configured.
- Email selected-thread access is approval-gated, wraps body content as `UNTRUSTED_EMAIL`, and never sends, deletes, moves, archives, or stores body text by default.
- Email/message drafts do not send.
- Approved send/write actions are disabled by default and require per-action approval.
- Other personal-data and write/send modules remain locked until later approval gates.
