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
- Controlled self-improvement manager supports propose, branch-bound implement, run-tests, show-diff, and approval-gated commit.
- Self-improvement blocks protected safety file edits and safety-weakening content.
- CLI inspection commands for tools, permissions, audit, memory, config, setup, and interactive entry.
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
```

Dry-run mode routes normally and evaluates policy, approval requirements, sanitized args, and action previews, but does not execute tools. Dry-run evaluations are audited with `dry_run=true`.

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

The research command runs `web.search` and optional `web.fetch_url` calls through `ToolBroker`, then returns a source-aware JSON report. It does not fabricate citations; if search or fetch fails, the report says so. Foreign-language titles, snippets, and excerpts are preserved, with a simple language hint when available.

Weather provider abstraction:

```bash
python smart_agent.py weather doctor
python smart_agent.py weather smoke "Phoenix, AZ"
python smart_agent.py weather current "San Francisco"
python smart_agent.py weather current "Phoenix, AZ" --no-cache
python smart_agent.py weather forecast "San Francisco" --days 3
python smart_agent.py weather cache clear
```

`weather.status`, `weather.current`, `weather.forecast`, and `weather.cache_clear` are LOW-risk, audited, rate-limited, ToolBroker-only capabilities for user-provided locations. The `doctor` command checks provider configuration and capability policy without fetching weather data. The `smoke` command runs `weather.status`, `weather.current`, and `weather.forecast` through the broker for a user-provided location. Open-Meteo is used when `WEATHER_PROVIDER` is unset; `WEATHER_PROVIDER=disabled` returns structured `weather provider is not configured` JSON.

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

Direct `weather current` and `weather forecast` commands print a readable answer with current conditions or daily forecast, umbrella/clothing guidance when data supports it, alert availability, cache warnings, uncertainty, provider, and `retrieved_at`. Add `--json` to either command to inspect the structured provider payload instead.

The weather tools do not use macOS Location Services, IP geolocation, personal data, writes, or long-term memory storage. Location arguments are redacted from audit logs by default. Open-Meteo geocoding and forecast responses are treated as `UNTRUSTED_WEB`. To disable weather entirely, set `WEATHER_PROVIDER=disabled`.

Natural-language weather requests route to weather tools only when they include a location, such as "What's the weather in Phoenix?" or "Is it going to rain tomorrow in LA?". Requests like "near me" do not infer personal location. To allow location-less weather questions, explicitly set `WEATHER_DEFAULT_LOCATION`, for example `WEATHER_DEFAULT_LOCATION=Phoenix, AZ`.

Weather responses are cached in a short-lived local TTL cache at `WEATHER_CACHE_PATH` using hashed keys. Defaults are 900 seconds for current weather and 3600 seconds for forecasts. Use `--no-cache` to bypass cache for a request, or `python smart_agent.py weather cache clear` to clear cached weather responses. This cache is separate from long-term memory.

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

The connector dashboard is read-only. It reports configuration, enabled state, default provider, risk level, approval requirement, rate-limit configuration, last audited success/error, cache state, and setup hints. It does not reveal secrets and does not perform personal-data reads; personal connectors are checked from configuration only.

Calendar read-only selected-range access:

```bash
python smart_agent.py calendar read --start 2026-05-22 --end 2026-05-23
python smart_agent.py calendar availability --start 2026-05-22 --end 2026-05-23 --duration 30
```

Calendar tools are HIGH risk, disabled by default, approval-required, and selected-range only. The optional connector path is Calendar.app through AppleScript:

```bash
export CALENDAR_CONNECTOR=applescript
```

This adapter uses macOS Calendar/Automation privacy prompts. It does not scrape private Calendar databases and does not require Full Disk Access. Event notes are not returned, locations are redacted unless `CALENDAR_INCLUDE_LOCATIONS=true`, availability returns slots without event details, and calendar results are not stored in long-term memory by default.

Contacts read-only selected-scope access:

```bash
python smart_agent.py contacts search "Sam" --max-results 5
python smart_agent.py contacts read "<contact_id>"
```

Contacts tools are HIGH risk, disabled by default, approval-required, and selected-scope only. The optional connector path is Contacts.app through AppleScript:

```bash
export CONTACTS_CONNECTOR=applescript
```

This adapter uses macOS Contacts/Automation privacy prompts. It does not scrape private AddressBook databases and does not require Full Disk Access. Search returns compact candidates only: name, organization, job title, counts/flags, and a selected-scope token. It does not return email addresses or phone numbers from search results. Reading a selected contact returns only requested fields; notes are never returned, and email, phone, and address values are redacted unless their explicit config gates are enabled.

Email assistant metadata, selected-thread, and draft-only access:

```bash
python smart_agent.py email metadata
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

Credentials are read from the environment or an external secret setup; the agent does not store passwords. Metadata listing returns headers only and no body. Selected thread reads are single-thread only, wrapped as `UNTRUSTED_EMAIL`, and not stored in long-term memory. Summaries treat email body as data, not instructions. Draft replies are marked draft-only and never send, delete, move, or archive email.

Messages/text assistant selected-thread stubs and manual draft-only access:

```bash
python smart_agent.py messages read "<thread_id>"
python smart_agent.py messages summarize "<thread_id>"
python smart_agent.py messages draft-reply "<thread_id>"
python smart_agent.py messages draft-from-text --to "Name" --context-file ./workspace/thread.txt
```

Messages tools are disabled by default and approval-gated. There is intentionally no live macOS Messages connector yet: the project does not scrape `~/Library/Messages`, does not request broad Full Disk Access, and does not bulk-read history. The safe fallback is a manually provided UTF-8 text file inside `./workspace`; its content is treated as `UNTRUSTED_MESSAGE`, audited as a file read, not stored in long-term memory, and used only to create a draft. Draft replies are marked draft-only and never send, delete, move, archive, or modify messages.

Memory tools:

```bash
python smart_agent.py --debug "Remember that I prefer concise answers"
```

Memory refuses secrets and personal email/message/contact/calendar content by default. Approval-gated personal memory exists as a separate capability.

Inspection commands:

```bash
python smart_agent.py tools list
python smart_agent.py doctor
python smart_agent.py permissions show
python smart_agent.py approvals list
python smart_agent.py approvals show <request_id>
python smart_agent.py approvals approve <request_id>
python smart_agent.py approvals deny <request_id>
python smart_agent.py audit tail
python smart_agent.py memory list
python smart_agent.py config show
python smart_agent.py setup
```

The `doctor` command does not send prompts to the model or access personal data. It checks Python, imports, runtime config, LM Studio reachability, `/v1/models`, selected model availability, startup policy, audit path writability, tool registry loading, and whether personal-data tools are disabled by default.

Approval commands inspect and update the local approval queue at `data/approvals.json`. Approval-required tool calls still execute only through `ToolBroker`; approving a queued request does not replay or execute an old tool call. In non-interactive mode, approval-required actions are denied safely and audited. Critical actions are per-action only and do not support approval reuse.

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
WEATHER_TIMEOUT_SECONDS=10
WEATHER_MAX_FORECAST_DAYS=7
WEATHER_DEFAULT_UNITS=metric
WEATHER_DEFAULT_LOCATION=
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
export LMSTUDIO_MODEL="qwopus3.6-35b-a3b-v1@q5_k_m"
PY="/Users/sambehdjou/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

$PY smart_agent.py --no-tools "Explain RCS vs iMessage"
$PY smart_agent.py --debug "What time is it?"
```

Optional readiness check:

```bash
$PY smart_agent.py doctor
```

Controlled smoke harness:

```bash
$PY smart_agent.py smoke --lmstudio
$PY smart_agent.py smoke --web
$PY smart_agent.py smoke --calendar --contacts
$PY smart_agent.py smoke --all-safe
$PY smart_agent.py smoke --all-safe --dry-run
```

Expected result:

- The first command answers naturally and attaches no tools.
- The second command prints route/tool-call/policy/audit debug details and lets the model request the safe time tool through `ToolBroker`.
- `smoke --lmstudio` sends minimal live prompts only when `LMSTUDIO_MODEL` is set; otherwise it reports a skipped check.
- `smoke --web` uses the configured web provider if present and fetches `https://example.com` as a safe public page.
- `smoke --calendar --contacts` is dry-run/check-only by default. It checks connector configuration and policy state but does not read personal data.

If LM Studio is not running, the CLI should say:

```text
LM Studio server not reachable at http://localhost:1234/v1. Start LM Studio Developer Server and retry.
```

If the model variable is missing, the CLI should say:

```text
LMSTUDIO_MODEL is not set. Export LMSTUDIO_MODEL='<model id>'.
```

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
