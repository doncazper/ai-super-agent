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
- Lead Inbox v1 supports mock-only lead listing, classification, local response drafts, and pending follow-up task actions without reading real providers or sending.
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

## Agent DNA And Cloneability

The long-lived architecture is captured in [docs/AGENT_DNA.md](</Users/sambehdjou/Documents/AI Super Agent/docs/AGENT_DNA.md>) and [docs/ARCHITECTURE_PRINCIPLES.md](</Users/sambehdjou/Documents/AI Super Agent/docs/ARCHITECTURE_PRINCIPLES.md>). Rewrites, model migrations, and platform ports must start from [docs/CLONE_BLUEPRINT.md](</Users/sambehdjou/Documents/AI Super Agent/docs/CLONE_BLUEPRINT.md>), [docs/MODEL_MIGRATION_GUIDE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/MODEL_MIGRATION_GUIDE.md>), and [docs/PLATFORM_MIGRATION_GUIDE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/PLATFORM_MIGRATION_GUIDE.md>).

Historical prompt provenance is tracked in [docs/BUILD_HISTORY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/BUILD_HISTORY.md>), [docs/BUILD_PROVENANCE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/BUILD_PROVENANCE.md>), [docs/DECISION_INDEX.md](</Users/sambehdjou/Documents/AI Super Agent/docs/DECISION_INDEX.md>), and [docs/RECONSTRUCTED_PROMPT_PACKS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/RECONSTRUCTED_PROMPT_PACKS.md>). Reconstructed prompt packs are labeled as reconstructed and are not exact originals unless the source evidence says so.

## Tracking System

Start with the short tracker dashboard at [docs/TRACKER_DASHBOARD.md](</Users/sambehdjou/Documents/AI Super Agent/docs/TRACKER_DASHBOARD.md>) and the source-of-truth map at [docs/TRACKER_INDEX.md](</Users/sambehdjou/Documents/AI Super Agent/docs/TRACKER_INDEX.md>). Command metadata lives in [docs/COMMAND_REGISTRY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/COMMAND_REGISTRY.md>), feature readiness lives in [docs/FEATURE_MATURITY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/FEATURE_MATURITY.md>), and the current resumable state lives in [docs/PROJECT_STATE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/PROJECT_STATE.md>).

## Setup

1. Install Python 3.11+ (Python 3.12 is recommended for local development).
2. Create a virtual environment.
3. Install test dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
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

Runtime control plane:

```bash
./scripts/agent runtime status
./scripts/agent runtime doctor
./scripts/agent runtime services
./scripts/agent runtime features
./scripts/agent runtime health
./scripts/agent workflows list
./scripts/agent workflows run connector_doctor
./scripts/agent jobs list
./scripts/agent events tail
```

Runtime orchestration is metadata-only in v1. These commands do not call LM Studio, read personal connectors, start background jobs, or execute tools. Real tool execution remains behind `ToolBroker`, `PolicyEngine`, approvals, and audit logging.

Brain Runtime Independence is a controlled track for decoupling the agent brain from one concrete model runtime while preserving current LM Studio/Qwopus behavior. LM Studio remains the current supported runtime and default provider. The provider-neutral interface, lazy model registry, LM Studio provider adapter, disabled-by-default llama.cpp server provider scaffold, disabled-by-default Ollama provider scaffold, optional disabled-by-default llama-cpp-python in-process scaffold, MLX strategy/stub, mock-first benchmark/eval layer, dry-run provider router, disabled MCP interop stubs, and release-gate evidence now exist; no runtime install, model download, paid/cloud API default, MCP server, network listener, in-process model load at startup, or persisted default-provider switch is enabled. See [docs/brain/BRAIN_RUNTIME_STRATEGY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/BRAIN_RUNTIME_STRATEGY.md>), [docs/brain/BRAIN_PROVIDER_INTERFACE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/BRAIN_PROVIDER_INTERFACE.md>), [docs/brain/MODEL_REGISTRY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/MODEL_REGISTRY.md>), [docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/BRAIN_RUNTIME_RELEASE_GATE.md>), [docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/BRAIN_RUNTIME_MATURITY_REVIEW.md>), and [docs/decisions/brain_runtime_independence.md](</Users/sambehdjou/Documents/AI Super Agent/docs/decisions/brain_runtime_independence.md>).

Provider diagnostics and safe routing:

```bash
./scripts/agent brain providers
./scripts/agent brain status
./scripts/agent brain doctor
./scripts/agent brain benchmark --safe
./scripts/agent brain eval --safe
./scripts/agent brain report --last
./scripts/agent brain fallback-status
./scripts/agent brain switch lmstudio --dry-run
./scripts/agent session continuity status
./scripts/agent session continuity export --redacted
./scripts/agent session continuity clear
./scripts/agent brain route "hello" --no-tools
./scripts/agent brain mcp-decision
./scripts/agent mcp status
./scripts/agent mcp doctor
./scripts/agent mcp server --dry-run
./scripts/agent mcp clients
```

Provider listing/status/doctor/fallback/route/MCP commands are metadata-only diagnostics. Safe benchmark/eval commands use deterministic mock fixtures by default and write local redacted reports; they do not call paid/cloud providers, access personal data, execute high-risk tools, start runtimes, start MCP, or download models. Fallback remains disabled by default, `brain switch` creates a compatibility/rollback preview and non-dry-run switch requests remain blocked in v1, cloud/paid fallback is disabled by default, and routing decisions cannot alter ToolBroker, policy, approval, audit, or memory behavior. Session continuity is opt-in and disabled by default; redacted continuity export writes no file, carries no personal data, and does not bypass memory policy. MCP remains optional interoperability, not the brain runtime; MCP server/client stubs are disabled by default and start no listener or external connection. See [docs/brain/PROVIDER_FALLBACK_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/PROVIDER_FALLBACK_POLICY.md>), [docs/brain/MODEL_ROUTING_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/MODEL_ROUTING_POLICY.md>), [docs/autonomy/MODEL_SWITCHING.md](</Users/sambehdjou/Documents/AI Super Agent/docs/autonomy/MODEL_SWITCHING.md>), [docs/autonomy/CROSS_SESSION_CONTINUITY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/autonomy/CROSS_SESSION_CONTINUITY.md>), [docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md>), and [docs/mcp/MCP_ADAPTER_BOUNDARIES.md](</Users/sambehdjou/Documents/AI Super Agent/docs/mcp/MCP_ADAPTER_BOUNDARIES.md>).

Safe gateway channel inspection:

```bash
./scripts/agent channels list
./scripts/agent channels status
./scripts/agent channels show telegram
./scripts/agent telegram doctor
./scripts/agent telegram status
./scripts/agent mobile status
./scripts/agent mobile pairing-status
```

The Hermes-inspired channel gateway scaffold is metadata-only. It lists future CLI, Telegram, iOS companion, Mac app, Windows app, local dashboard, email, manual handoff, and mock channel records without connecting to external services, reading personal data, sending messages, approving actions, executing tools, starting listeners, or creating background persistence. Telegram/mobile commands are config/status only: no bot starts, no polling/webhook server starts, no Telegram API call is made, no message is sent, and no mobile pairing or approval path is enabled. Future channel requests must route through the orchestrator and then ToolBroker, PolicyEngine, PermissionManager, ApprovalManager where required, and AuditLogger. See [docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/channels/GATEWAY_CHANNEL_ARCHITECTURE.md>), [docs/channels/CHANNEL_SECURITY_MODEL.md](</Users/sambehdjou/Documents/AI Super Agent/docs/channels/CHANNEL_SECURITY_MODEL.md>), [docs/channels/TELEGRAM_MOBILE_ACCESS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/channels/TELEGRAM_MOBILE_ACCESS.md>), and [docs/channels/MOBILE_CHANNEL_SECURITY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/channels/MOBILE_CHANNEL_SECURITY.md>).

Creative media planning:

```bash
./scripts/agent media plan "make me a thumbnail for this vlog"
./scripts/agent media thumbnail "make me a thumbnail for this vlog" --dry-run
./scripts/agent media generate image "a product sketch" --dry-run
./scripts/agent media generate video "a 10-second intro animation" --dry-run
./scripts/agent media generate audio "soft notification chime" --dry-run
./scripts/agent media generate music "short lo-fi bed" --dry-run
./scripts/agent eval run --media
```

Creative media commands are planning-only in this track. They run safety preflight and return dry-run plans, provider/setup hints, and exact next commands, but they do not call providers, generate media, upload, publish, read personal media, store request history, or bypass the safety control plane. Natural-language requests such as "make me a thumbnail" can route to `media plan` as preflight metadata only. Fixture-backed media evals and dogfood suites validate these boundaries without real generation. See [docs/media/MEDIA_WORKFLOW_COMMANDS_AND_NL_ROUTING.md](</Users/sambehdjou/Documents/AI Super Agent/docs/media/MEDIA_WORKFLOW_COMMANDS_AND_NL_ROUTING.md>) and [docs/media/MEDIA_DOGFOOD_RUNBOOK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/media/MEDIA_DOGFOOD_RUNBOOK.md>).

Optional local runtime scaffold:

- `llama_cpp_server` is available as a disabled-by-default provider for a user-managed OpenAI-compatible llama.cpp server.
- Configure it with `LLAMA_CPP_SERVER_ENABLED=true`, `LLAMA_CPP_SERVER_BASE_URL`, and `LLAMA_CPP_SERVER_MODEL` only after starting the server yourself.
- Tool-call support remains off unless `LLAMA_CPP_SERVER_SUPPORTS_TOOL_CALLS=true` is explicitly set after verification.
- See [docs/brain/providers/llama_cpp_server.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/providers/llama_cpp_server.md>).
- `ollama` is available as a disabled-by-default provider for a user-managed local Ollama daemon.
- Configure it with `OLLAMA_ENABLED=true`, `OLLAMA_BASE_URL`, `OLLAMA_OPENAI_COMPAT_BASE_URL`, and `OLLAMA_MODEL` only after starting Ollama and pulling the model yourself.
- Tool-call support remains off unless `OLLAMA_SUPPORTS_TOOL_CALLS=true` is explicitly set after verification.
- See [docs/brain/providers/ollama.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/providers/ollama.md>).
- `llama_cpp_inprocess` is available as an optional disabled-by-default scaffold for a user-installed `llama-cpp-python` runtime and local GGUF model path.
- Configure it with `LLAMA_CPP_INPROCESS_ENABLED=true` and `LLAMA_CPP_INPROCESS_MODEL_PATH` only after installing the optional dependency and choosing a model yourself.
- Health checks do not load the model; chat loading is lazy and future provider routing remains gated.
- See [docs/brain/providers/llama_cpp_inprocess.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/providers/llama_cpp_inprocess.md>).
- `mlx` is available as an experimental disabled-by-default strategy stub for future Apple Silicon MLX/MLX-LM support.
- The current stub only reports setup/status. It does not install MLX, download models, start a server, import native MLX modules, load a model, generate text, or become the default provider.
- See [docs/brain/providers/mlx.md](</Users/sambehdjou/Documents/AI Super Agent/docs/brain/providers/mlx.md>) and [docs/decisions/mlx_provider_strategy.md](</Users/sambehdjou/Documents/AI Super Agent/docs/decisions/mlx_provider_strategy.md>).

Cross-platform scaffolding is metadata-only and disabled/lazy by default. `agent.platforms` can detect `macos`, `windows`, `linux`, or `unknown`, infer an explicit runtime mode such as `cli` or `test`, and compute project-local platform paths without scanning personal files, creating directories, importing native frameworks, requesting permissions, starting app bridge servers, or enabling platform actions. Future bridges still require manifest entries, ToolBroker routing, PolicyEngine/PermissionManager checks, ApprovalManager gates, and AuditLogger evidence.

Read-only platform inspection commands:

```bash
python smart_agent.py platform doctor
python smart_agent.py platform status
python smart_agent.py platform capabilities
python smart_agent.py platform matrix
python smart_agent.py platform explain macos.calendar.read
```

These commands execute through `ToolBroker`, `PolicyEngine`, and `AuditLogger`, but they only inspect static metadata, safe config flags, and `sys.platform` detection. They do not execute bridge actions, request OS permissions, import native frameworks, access personal data, start an app bridge server, or enable planned platform capabilities.

Dry-run mode:

```bash
python smart_agent.py --dry-run --debug "What time is it?"
python smart_agent.py --dry-run web "local AI news"
python smart_agent.py preflight "email.read_selected_thread"
python smart_agent.py preflight "What's the weather in Phoenix?"
python smart_agent.py router explain "What is the latest OpenAI API pricing?"
```

Dry-run mode routes normally and evaluates policy, approval requirements, sanitized args, and action previews, but does not execute tools. Dry-run evaluations are audited with `dry_run=true`. The `preflight` command is a prompt-free preview path: it uses the deterministic router or an exact tool/capability name, evaluates likely tool calls through `ToolBroker.dry_run()`, and shows risk, policy, approval, sanitized arguments, internet-routing metadata, and whether exact action details are still missing.

The router only attaches internet-capable tools for current/live/external/source-required requests, explicit URLs, explicit lookup/search/verify/source requests, citations, or likely-stale niche facts. Stable explanations, creative writing, local-repo coding questions, personal advice without current facts, math, user-provided-text summaries, and `--no-tools` stay tool-clean. `router explain` shows `needs_internet`, `reason`, `suggested_sources`, `provider_policy`, `tools`, `risk_hint`, and `ask_clarification` without calling providers, rewriting the user message, or storing query history. See [docs/web/INTERNET_ROUTING_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/INTERNET_ROUTING_POLICY.md>).

Web tools:

```bash
python smart_agent.py --debug "Read this URL https://example.com"
python smart_agent.py --debug "Look up local AI news"
python smart_agent.py web "local AI news"
python smart_agent.py research "local AI news"
```

`web.search` returns a clear error until a supported provider is configured. Brave Search is optional and quota-limited, so it is not selected just because a key exists:

```bash
export WEB_ACCESS_ENABLED=true
export PROVIDER_COST_MODE=free_first
export WEB_SEARCH_PROVIDER=brave
export BRAVE_SEARCH_API_KEY="..."
export BRAVE_SEARCH_ENABLED=true
export BRAVE_SEARCH_TIMEOUT_SECONDS=10
export BRAVE_SEARCH_MAX_RESULTS=10
export BRAVE_SEARCH_SAFE_SEARCH=true
export ALLOW_PAID_APIS=true
export MAX_PAID_API_CALLS_PER_DAY=5
python smart_agent.py web brave doctor
python smart_agent.py connectors status brave
python smart_agent.py web "local AI news"
python smart_agent.py web search "local AI news" --provider brave
```

The direct `web` command executes `web.search` through `ToolBroker`, `PolicyEngine`, rate limits, and audit logging. It returns search-result metadata only; it does not fetch full pages. Search results are labeled `UNTRUSTED_WEB`, and search queries are redacted from audit logs by default unless `WEB_SEARCH_AUDIT_QUERIES=true` is explicitly set.

Provider selection follows the cost-aware policy in [docs/connectors/PROVIDER_SELECTION.md](</Users/sambehdjou/Documents/AI Super Agent/docs/connectors/PROVIDER_SELECTION.md>) and [docs/connectors/COST_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/connectors/COST_POLICY.md>). Defaults prefer local/cache/no-key/official/user-configured sources before paid or quota-limited APIs. Brave, SerpAPI, and WeatherAPI are not used as defaults unless explicitly configured and allowed.

Provider policy inspection:

```bash
python smart_agent.py web providers
python smart_agent.py web provider-policy
python smart_agent.py web provider-decision "https://example.com/source"
python smart_agent.py web search-providers
python smart_agent.py web official-apis
python smart_agent.py web api-status github
python smart_agent.py web api-search github "openai"
```

These commands are read-only, execute through `ToolBroker`, make no provider API calls, and write no search history. Provider decisions include selected/skipped providers, skip reasons, cost mode, paid API use, cache use, and a redacted audit summary. Query text is redacted from audit logs by default. Search provider registry behavior is documented in [docs/web/SEARCH_PROVIDER_REGISTRY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/SEARCH_PROVIDER_REGISTRY.md>).

News Intelligence is currently a planned/scaffolded track, not an active runtime command set. The repo declares disabled/planned `news.*` capability manifest entries and safe `NEWS_*` defaults so future news commands must be implemented deliberately through ToolBroker, PolicyEngine, and AuditLogger. Provider policy is free-first/cache-first; paid providers stay skipped by default, readable search/news history is off, full article-body storage is off, and no news provider calls or article fetches exist yet. See [docs/news/NEWS_INTELLIGENCE_TRACK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/news/NEWS_INTELLIGENCE_TRACK.md>) and [docs/news/NEWS_PROVIDER_STRATEGY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/news/NEWS_PROVIDER_STRATEGY.md>).

Official API connector framework:

```bash
python smart_agent.py web official-apis
python smart_agent.py web api-status wikipedia
python smart_agent.py web api-status reddit
python smart_agent.py web api-search github "openai"
```

Official API providers are preferred over scraping when a site has a documented API, but v1 is framework/stubbed and performs no live API calls by default. GitHub, Wikipedia/Wikidata, arXiv, and Reddit provider metadata are available; Reddit is read-only/setup-gated and explicitly has no web-scraping fallback. All official API command paths are brokered, audited, query-redacted by default, and return `UNTRUSTED_WEB` result metadata. See [docs/web/OFFICIAL_API_CONNECTORS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/OFFICIAL_API_CONNECTORS.md>).

Internet dogfood and eval release gate:

```bash
python smart_agent.py dogfood run internet_core --dry-run
python smart_agent.py dogfood run web_research --dry-run
python smart_agent.py eval run --internet
python smart_agent.py eval report --internet
```

The internet eval category is fixture-backed and does not call live providers. It checks source lists, citations, `retrieved_at`, failed fetch reporting, prompt-injection handling, free-first provider policy, no paid provider default, no query/web-content memory persistence, and network-domain audit fixtures. Live web dogfood suites such as `web_fetch`, `web_research`, and `web_blocked_sources` are opt-in and should be run only when public network checks are acceptable. See [docs/web/INTERNET_DOGFOOD_RUNBOOK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/INTERNET_DOGFOOD_RUNBOOK.md>).

Public web cache and local index commands:

```bash
python smart_agent.py web cache status
python smart_agent.py web cache show <source_id>
python smart_agent.py web cache clear
python smart_agent.py web index search "local cache policy"
python smart_agent.py web index rebuild
```

The web cache stores public unauthenticated source metadata only by default. It uses URL/provider/query-hash cache keys, avoids raw query history, keeps full content storage disabled unless explicitly configured, and labels cached/indexed sources as untrusted. See [docs/web/WEB_CACHE_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/WEB_CACHE_POLICY.md>) and [docs/web/LOCAL_WEB_INDEX.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/LOCAL_WEB_INDEX.md>).

The Internet Access graduation track is documented in [docs/decisions/internet_access_graduation_track.md](</Users/sambehdjou/Documents/AI Super Agent/docs/decisions/internet_access_graduation_track.md>) with companion policy docs in [docs/web/WEB_ACCESS_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/WEB_ACCESS_POLICY.md>), [docs/web/INTERNET_PROVIDER_STRATEGY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/INTERNET_PROVIDER_STRATEGY.md>), [docs/web/SOURCE_GROUNDING_REQUIREMENTS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/SOURCE_GROUNDING_REQUIREMENTS.md>), and [docs/web/BLOCKED_SOURCE_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/BLOCKED_SOURCE_POLICY.md>). The track is free-first and cache-first, treats all web content as untrusted data, forbids CAPTCHA/anti-bot/login-wall bypass, and does not store web history or fetched content in memory by default.

SearXNG is available as the free/self-hosted search provider. It is never pointed at a public instance by default and only runs when explicitly configured:

```bash
export WEB_ACCESS_ENABLED=true
export WEB_SEARCH_PROVIDER=searxng
export SEARXNG_BASE_URL="https://search.example"
export SEARXNG_ENABLED=true
export SEARXNG_TIMEOUT_SECONDS=10
export SEARXNG_MAX_RESULTS=10
export SEARXNG_SAFE_SEARCH=1
export SEARXNG_CATEGORIES=general
python smart_agent.py web searxng doctor
python smart_agent.py connectors status searxng
python smart_agent.py web search "local AI news" --provider searxng
```

The configured SearXNG instance must support JSON output for search. If the instance returns HTML, HTTP 403/429, malformed JSON, or times out, the command returns a structured setup/error response instead of scraping HTML or falling back silently. SearXNG results are normalized as `UNTRUSTED_WEB`, provider domains are audited, and search history is not stored by default. See `docs/web/providers/searxng.md`.

Brave Search is available as an optional quota-limited provider. It requires an API key, `BRAVE_SEARCH_ENABLED=true`, and paid/quota policy opt-in:

```bash
export WEB_ACCESS_ENABLED=true
export WEB_SEARCH_PROVIDER=brave
export BRAVE_SEARCH_API_KEY="..."
export BRAVE_SEARCH_ENABLED=true
export ALLOW_PAID_APIS=true
export MAX_PAID_API_CALLS_PER_DAY=5
python smart_agent.py web brave doctor
python smart_agent.py connectors status brave
python smart_agent.py web search "local AI news" --provider brave
```

The Brave path executes through the brokered `web.search` tool, audits the provider decision and `api.search.brave.com` domain when called, labels results `UNTRUSTED_WEB`, and stores no search history by default. If the key, enablement flag, or paid/quota policy is missing, the command returns setup guidance instead of falling back silently. See `docs/web/providers/brave.md`.

SerpAPI is available only as an optional paid/quota-limited fallback. It is never selected by `web "query"` or `research "query"` under `free_first` just because `SERPAPI_API_KEY` exists. To use it, explicitly opt in:

```bash
export WEB_ACCESS_ENABLED=true
export PROVIDER_COST_MODE=free_first
export ALLOW_PAID_APIS=true
export MAX_PAID_API_CALLS_PER_DAY=5
export SERPAPI_API_KEY="..."
export SERPAPI_ENABLED=true
export SERPAPI_TIMEOUT_SECONDS=10
export SERPAPI_MAX_RESULTS=10
python smart_agent.py web serpapi doctor
python smart_agent.py connectors status serpapi
python smart_agent.py web search "local AI news" --provider serpapi
python smart_agent.py research "local AI news" --provider serpapi
```

The SerpAPI path executes as `web.search.serpapi` through `ToolBroker`, uses the same query redaction behavior as `web.search`, audits the provider decision and `serpapi.com` domain when called, labels results `UNTRUSTED_WEB`, and stores no search history by default. If the key, `SERPAPI_ENABLED=true`, or paid/quota policy is missing, the command returns setup guidance instead of falling back silently. SerpAPI is not used for CAPTCHA, login, paywall, or anti-bot bypass behavior. Explicit provider selections return setup hints unless the matching provider is implemented, configured, enabled, and allowed by policy. See `docs/web/providers/serpapi.md`.

Free-first web acquisition:

```bash
python smart_agent.py web robots "example.com"
python smart_agent.py web sitemap "example.com"
python smart_agent.py web feed "https://example.com/feed.xml"
python smart_agent.py web acquire-url "https://example.com"
python smart_agent.py web acquire "example.com"
python smart_agent.py web source-status "https://example.com"
python smart_agent.py web fetch "https://example.com/article"
python smart_agent.py web extract "https://example.com/article"
python smart_agent.py web metadata "https://example.com/article"
```

Robots, sitemap, and feed acquisition uses bounded public fetches, TTL cache metadata, domain audit logging, and `UNTRUSTED_WEB`/`UNTRUSTED_DOCUMENT` labels. Feed parsing accepts common RSS/Atom MIME types and does not fetch article bodies; binary payloads, blocked domains, CAPTCHA/login/paywall/anti-bot pages, and paid-provider defaults remain denied or unavailable.

These commands execute through `ToolBroker` as `web.robots`, `web.sitemap`, `web.feed`, `web.acquire_url`, `web.acquire`, `web.source_status`, `web.fetch_url`, `web.extract_readable_text`, and `web.extract_metadata`. They prefer local cache, explicit feeds/sitemaps, robots-aware direct public URL fetch, and no-key sources before paid or quota-limited providers. `source-status` is a no-fetch inspection path for URL handling, blocked-domain checks, trust labels, and provider-decision metadata. `fetch`, `extract`, and `metadata` are selected-URL workflows with URL validation, tracking-parameter stripping, timeout/redirect/content-type/size bounds, sanitized HTML, readable text extraction, source metadata extraction, and untrusted-content wrapping. Webpage content is `UNTRUSTED_WEB`; fetched feed/sitemap documents are `UNTRUSTED_DOCUMENT`. CAPTCHA, anti-bot, login, browser profile, cookie, session, and paywall barriers return an unavailable result rather than a bypass attempt. Query acquisition does not store raw search history by default and returns a limitation when no free configured source can satisfy the query.

Robots and crawler limits are documented in [docs/web/ROBOTS_AND_RATE_LIMITS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/ROBOTS_AND_RATE_LIMITS.md>). Feed and sitemap behavior is documented in [docs/web/FEEDS_AND_SITEMAPS.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/FEEDS_AND_SITEMAPS.md>); default limits are 500 sitemap URLs and 50 feed items, and article bodies are not fetched by the feed command. Direct selected-URL fetch and extraction behavior is documented in [docs/web/SAFE_FETCH_AND_EXTRACTION.md](</Users/sambehdjou/Documents/AI Super Agent/docs/web/SAFE_FETCH_AND_EXTRACTION.md>).

Secret/config doctor:

```bash
python smart_agent.py secrets doctor
python smart_agent.py secrets status
python smart_agent.py secrets list
python smart_agent.py secrets redaction-test
python smart_agent.py secrets policy
python smart_agent.py secrets sources
python smart_agent.py secrets doctor reddit
python smart_agent.py secrets doctor all
python smart_agent.py connectors status searxng
python smart_agent.py connectors status brave
python smart_agent.py connectors status serpapi
python smart_agent.py connectors status weatherapi
python smart_agent.py connectors status gmail
python smart_agent.py connectors status telegram
python smart_agent.py connectors status reddit
python smart_agent.py gmail doctor
python smart_agent.py gmail scopes
python smart_agent.py telegram doctor
python smart_agent.py telegram status
python smart_agent.py reddit doctor
python smart_agent.py reddit status
python smart_agent.py reddit auth-check
```

These checks report whether optional Brave, SerpAPI, WeatherAPI, Gmail, Telegram, and Reddit credentials appear configured, whether cost policy allows them, whether they are defaults, and which setup hints apply. Status and doctor commands do not call provider APIs, read Gmail, send Telegram messages, fetch Reddit posts/comments, or print raw secret values. Existing keys do not promote Brave, SerpAPI, or WeatherAPI into the default path; paid/quota-limited providers remain disabled unless the cost-policy config explicitly allows them.

The focused Gmail and Telegram doctors are config-only. Gmail checks `GMAIL_USER`, `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_TOKEN_PATH`, and `GMAIL_SCOPES`, warns on broad or send-capable scopes, and warns if the token path points inside the repo. Telegram checks `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID`, and `TELEGRAM_ALLOWED_CHAT_IDS`, warns when default or allowed chat IDs are missing, and never prints the bot token. Gmail and Telegram connectors remain disabled by default; future sends remain CRITICAL, per-action approval-only, and not enabled by these doctor commands.

Secrets policy and setup docs live under [docs/secrets/SECRETS_MANAGEMENT_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/secrets/SECRETS_MANAGEMENT_POLICY.md>). Real API keys, OAuth tokens, private keys, and credential files must stay out of git. Use a password manager, macOS Keychain, process environment variables, or a local ignored `.env`; `.env.example` and [docs/templates/env_template.example](</Users/sambehdjou/Documents/AI Super Agent/docs/templates/env_template.example>) are placeholder-only. If a key is exposed, revoke/rotate it before continuing release work.

Keychain inspection is dry-run/status-only in v1:

```bash
python smart_agent.py secrets keychain status
python smart_agent.py secrets keychain get github_token --dry-run
python smart_agent.py secrets keychain set github_token --dry-run
```

These commands do not read or write Keychain values and return setup metadata only.

Before committing or pushing, run the redacted local preflight:

```bash
python smart_agent.py secrets scan
python smart_agent.py secrets scan --staged
python smart_agent.py git preflight
python smart_agent.py git preflight --staged
```

The scanner is best-effort and dependency-free. It reports redacted paths/line numbers for likely leaks and never rewrites Git history.

### Reddit Setup

Reddit access is disabled by default. The read-only connector is implemented for the official Reddit Data API, but live content calls require explicit OAuth configuration and `REDDIT_ENABLED=true`:

```bash
REDDIT_ENABLED=false
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=
REDDIT_REFRESH_TOKEN=
REDDIT_ACCESS_TOKEN=
python smart_agent.py reddit doctor
python smart_agent.py reddit status
python smart_agent.py connectors status reddit
python smart_agent.py reddit search "local llm"
python smart_agent.py reddit search "gpu advice" --subreddit LocalLLaMA --sort comments --time week --limit 10 --language en
python smart_agent.py reddit explain-result <source_id>
python smart_agent.py reddit subreddit LocalLLaMA
python smart_agent.py reddit post "<post_id_or_url>"
python smart_agent.py reddit comments "<post_id_or_url>"
python smart_agent.py reddit thread "<post_id_or_url>" --max-comments 100 --sort top --collapse-depth 3
python smart_agent.py reddit thread-export "<post_id_or_url>" --format json
python smart_agent.py reddit summarize-thread "<post_id_or_url>"
python smart_agent.py reddit summarize-search "gpu advice"
python smart_agent.py reddit consensus "best local LLM UI"
python smart_agent.py reddit pros-cons "laptop model"
python smart_agent.py reddit complaints "laptop model"
python smart_agent.py reddit buying-advice "laptop model"
python smart_agent.py reddit cache status
python smart_agent.py reddit cache clear
python smart_agent.py reddit retention status
python smart_agent.py reddit retention sweep
python smart_agent.py reddit privacy-report
```

`reddit doctor` and `reddit status` execute through `ToolBroker` as `reddit.status`, audit the diagnostic call, and perform no Reddit network calls. They report missing OAuth fields, generic user-agent warnings, tracked `.env` warnings, repo-local token-file warnings, rate-limit config, retention config, disabled write actions, denied web fallback, and hard-false training use.

`reddit auth-check` is the only doctor command that may call Reddit, and only when explicitly invoked. It uses Reddit OAuth/token-status endpoints, audits the Reddit OAuth domain, redacts tokens and client secrets, fetches no posts/comments/threads, stores no user content, and returns setup guidance when OAuth config is incomplete. Reddit web scraping fallback, posting, commenting, voting, DMs, moderation, CAPTCHA/anti-bot bypass, and unauthenticated traffic are not enabled.

The read-only commands run through `ToolBroker` as `reddit.search_posts`, `reddit.explain_result`, `reddit.fetch_subreddit_info`, `reddit.fetch_post`, `reddit.fetch_comments`, `reddit.fetch_thread`, `reddit.thread_export`, `reddit.summarize_thread`, `reddit.summarize_search`, `reddit.consensus`, `reddit.pros_cons`, `reddit.complaints`, `reddit.buying_advice`, `reddit.cache_status`, `reddit.cache_clear`, `reddit.retention_status`, `reddit.retention_sweep`, and `reddit.privacy_report`. Search supports optional subreddit, sort, time, limit, and advisory language parameters. Thread fetch returns a bounded normalized post, comment tree, flattened comments, source references, warnings, and truncation metadata. Thread export writes only under `workspace/reddit_threads/` and labels the exported file `UNTRUSTED_DOCUMENT`. Summaries include short answer, consensus, viewpoints, disagreements, repeated complaints/praise, caveats, source list, and fetch limitations; search summaries are snippet-only until a thread is fetched. Results are labeled `UNTRUSTED_WEB`, include source IDs and permalinks, distinguish snippet-only search results from fetched thread data, redact author metadata by default, store no query history or summary memory, and return setup guidance instead of network calls when Reddit is disabled or OAuth config is incomplete. `reddit explain-result` reads cached metadata only and does not call Reddit or scrape pages. `reddit cache status`, `reddit retention status`, and `reddit privacy-report` return counts and policy flags only, never raw post/comment bodies, authors, or query text. Deleted or removed Reddit content and prompt-injection-like comments are not summarized as evidence.

### Multilingual Forum Language Tools

The language layer is local-first and designed for Reddit/forum/web text. Detection uses local heuristics; translation uses the local LM Studio/Qwopus model by default and returns setup guidance instead of falling back to cloud or paid translation APIs.

```bash
python smart_agent.py language detect --text "hola mundo"
python smart_agent.py language translate --from auto --to en --text "你好，世界"
python smart_agent.py language translate-file ./workspace/input.txt --to en
python smart_agent.py language glossary ./workspace/input.txt
```

These commands execute through `ToolBroker` as `language.detect`, `language.translate_text`, and `language.extract_terms`; file commands first read approved workspace files through `filesystem.read`. Source text remains `UNTRUSTED_WEB` or `UNTRUSTED_DOCUMENT`, translations are labeled `MODEL_GENERATED_TRANSLATION`, source IDs/chunk IDs are preserved, prompt-injection-like source text is treated as data, and no translation, summary, glossary, or source text is written to memory by default. See [docs/language/MULTILINGUAL_SUPPORT.md](</Users/sambehdjou/Documents/AI Super Agent/docs/language/MULTILINGUAL_SUPPORT.md>).

### Cross-Language Forum Research

The forum research workflow is brokered, source-labeled, and setup-gated by default. Reddit uses the official API connector when configured; V2EX now has a disabled-by-default documented read-only API connector; web discovery and Chinese discovery-only platforms report setup or unavailable status until approved search-provider paths exist.

```bash
python smart_agent.py forums research "local LLM experiences"
python smart_agent.py forums research "local LLM experiences" --languages en,zh,ja,ko --sources reddit,v2ex,web --translate-to en
python smart_agent.py forums compare "local LLM experiences" --sources reddit,v2ex
```

Forum provider registry diagnostics are metadata-only and perform no provider calls, logged-in reads, personal-data access, or scraping:

```bash
python smart_agent.py forums providers
python smart_agent.py forums status reddit
python smart_agent.py forums doctor
python smart_agent.py forums capabilities zhihu
```

See [docs/forums/FORUM_PROVIDER_REGISTRY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/forums/FORUM_PROVIDER_REGISTRY.md>).

V2EX read-only commands are available once `V2EX_ENABLED=true` is configured. They use documented API endpoints only, redact optional `V2EX_TOKEN`, normalize topics/replies as untrusted forum records, enforce local rate limits, and write no memory:

```bash
python smart_agent.py v2ex doctor
python smart_agent.py v2ex nodes
python smart_agent.py v2ex node python --limit 10 --detect-language
python smart_agent.py v2ex topic 12345
python smart_agent.py v2ex replies 12345 --limit 100
python smart_agent.py v2ex latest
python smart_agent.py v2ex hot
python smart_agent.py connectors status v2ex
```

See [docs/forums/providers/v2ex.md](</Users/sambehdjou/Documents/AI Super Agent/docs/forums/providers/v2ex.md>).

Chinese forum discovery commands use approved web search providers with site filters, and selected public URL fetches only where safe fetch policy allows. They do not use platform login cookies, browser sessions, CAPTCHA bypasses, or platform-specific scrapers:

```bash
python smart_agent.py cn-forums providers
python smart_agent.py cn-forums search "local LLM" --sites zhihu,v2ex,tieba
python smart_agent.py cn-forums fetch "https://www.v2ex.com/t/12345"
python smart_agent.py cn-forums research "local LLM" --translate-to en
```

Results are labeled `UNTRUSTED_WEB`, search results remain snippet-only until fetched, blocked/login/CAPTCHA pages return unavailable, language detection runs on fetched public text, optional translation uses the local model path by default, and no forum search history, fetched content, translations, summaries, cookies, or browser session state are written to memory. See [docs/forums/CHINESE_FORUM_DISCOVERY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/forums/CHINESE_FORUM_DISCOVERY.md>).

Outputs preserve source IDs/permalinks, label translations as `MODEL_GENERATED_TRANSLATION`, keep original-language snippets where useful, report unavailable sources, and avoid cultural or statistical consensus claims from sparse forum data. The workflow performs no scraping behind login/CAPTCHA/anti-bot barriers, uses no paid providers by default, and writes no forum content, translations, summaries, or search history to memory. See [docs/forums/CROSS_LANGUAGE_RESEARCH.md](</Users/sambehdjou/Documents/AI Super Agent/docs/forums/CROSS_LANGUAGE_RESEARCH.md>).

Forum dogfood and eval checks are available for mock-first validation:

```bash
python smart_agent.py dogfood run reddit_core --session
python smart_agent.py dogfood run reddit_research --session
python smart_agent.py dogfood run forum_multilingual --session
python smart_agent.py eval run --forums
python smart_agent.py eval report --forums
```

The forum eval category is fixture-backed and makes no live provider calls. It checks source grounding, generated translation labels, preserved source IDs/original snippets, prompt-injection resistance, deleted/removed-content exclusion, blocked-source unavailable reporting, no scraping bypass, no paid provider default, no memory write, retention/cache policy evidence, and provider-call audit fixtures. Live Reddit, V2EX, and Chinese forum checks remain opt-in and configuration-dependent. See [docs/forums/FORUM_DOGFOOD_RUNBOOK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/forums/FORUM_DOGFOOD_RUNBOOK.md>).

`web.fetch_url` treats fetched pages as untrusted data and refuses binary downloads by default. It validates public HTTP(S) URLs, validates redirect targets before following them, strips common tracking parameters, enforces content-type and size limits, extracts readable text, strips scripts/styles, and wraps page text with the untrusted-web warning.

Source-grounded research:

```bash
python smart_agent.py research "local AI news"
python smart_agent.py research "local AI news" --provider auto --max-sources 5 --freshness recent
python smart_agent.py research --max-sources 2 --no-fetch "local AI news"
python smart_agent.py research --locale es --summary-language en "últimas noticias de IA"
python smart_agent.py research "local AI news" --provider serpapi
python smart_agent.py research sources --last
python smart_agent.py research export-sources --last
python smart_agent.py research verify-sources --last
```

The research command runs `web.search` and optional `web.fetch_url` calls through `ToolBroker`, then returns a source-aware JSON report with `Answer`, `Sources`, `Coverage / limitations`, `Fetch failures`, and a metadata-only `source_bundle`. It does not fabricate citations; if search or fetch fails, the report says so in `answer`, `coverage_note`, and `fetch_failures`. The source bundle gives each source a stable `source_id`, labels fetched versus snippet-only evidence, and keeps failed fetches out of citation support. Foreign-language titles, snippets, and excerpts are preserved, with a simple language hint when available. Fetched page text is treated as `UNTRUSTED_WEB` data; page instructions are filtered from excerpts and cannot request tools, alter policy, reveal secrets, or become model instructions. The `research sources/export-sources/verify-sources --last` commands inspect the last metadata-only bundle without provider calls or article-body storage.

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
python smart_agent.py prompts evidence PTM-10
python smart_agent.py prompts missing
python smart_agent.py prompts missed
python smart_agent.py prompts stale
python smart_agent.py prompts recover-plan
```

Prompt tracking is SDLC metadata only. It reads `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, prompt record files under `prompts/<status>/`, and project tracking docs. It does not execute agent tools, add connectors, access personal data, send messages, or weaken policy. `mark-complete` requires test/docs status fields unless `--unknown` is used, `mark-failed` requires a reason, and the tracker enforces at most one active prompt.

Prompt evidence and recovery are documented in `docs/prompt_tracker/PROMPT_EVIDENCE_POLICY.md` and `docs/prompt_tracker/PROMPT_RECOVERY_PLAN.md`. Evidence classifications include `complete_verified`, `likely_complete`, `partial`, `no_evidence`, `failed`, `blocked`, `superseded`, and `stale`. Recovery commands report missed/stale/orphaned/ghost state and never auto-run prompts.

Prompt packs are documented in `docs/PROMPT_PACK_FORMAT.md`. `validate-pack` checks delimiters, metadata, unique ids/orders, dependencies, cycles, risk levels, and import-only mode without writing files. `import` and `split` are intentionally conservative: they copy the original pack into `prompts/packs/`, split individual prompts into `prompts/queued/`, append prompt ledger and queue rows, and add a prompt audit summary. Imported prompts are not executed automatically; delimiter examples inside prompt bodies are preserved as untrusted prompt text; `prompts next` returns only the next queued prompt whose dependencies are complete and whose approval gate is not blocking.

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
python smart_agent.py commands intents
python smart_agent.py commands suggest "what is the weather in phoenix"
python smart_agent.py nl preflight "what is the weather in Phoenix"
python smart_agent.py nl explain "send this email"
python smart_agent.py nl suggest "look up latest Python release"
python smart_agent.py commands legacy
python smart_agent.py commands validate
python smart_agent.py commands qa-plan
python smart_agent.py commands qa-run Weather
```

The durable command catalog lives in `docs/COMMAND_REGISTRY.md`; manual test coverage lives in `docs/COMMAND_TEST_MATRIX.md`; deprecated and blocked paths live in `docs/COMMAND_LEGACY.md`; and the manual QA process lives in `docs/COMMAND_QA_RUNBOOK.md`. Use `commands intents` and `commands suggest` to inspect the deterministic natural-language intent index; both commands print metadata only and do not execute suggested commands. Use `nl preflight`, `nl explain`, and `nl suggest` to preview natural-language command plans; they execute no tools or commands and HIGH/CRITICAL or missing-setup requests are not safe to execute from natural language. Use `commands qa-plan` to find commands that need manual testing, and log command bugs by adding bug IDs to the test matrix before creating regression tests.

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
python smart_agent.py skills validate native_skill_vetter
python smart_agent.py skills doctor
python smart_agent.py skills doctor native_skill_vetter
python smart_agent.py skills roots
python smart_agent.py skills precedence
python smart_agent.py skills registry
python smart_agent.py skills explain-root experimental_skills
python smart_agent.py skills provenance native_skill_vetter
python smart_agent.py skills trust native_skill_vetter
python smart_agent.py skills lock status
python smart_agent.py skills lock verify
python smart_agent.py skills profiles
python smart_agent.py skills profile show default
python smart_agent.py skills profile allowed default
python smart_agent.py skills profile validate default
python smart_agent.py skills compatibility
python smart_agent.py skills compatibility native_skill_vetter
python smart_agent.py skills platform matrix
python smart_agent.py skills conflicts
python smart_agent.py skills conflicts --json
python smart_agent.py skills explain-conflict <conflict_id>
python smart_agent.py skills test native_skill_vetter
python smart_agent.py skills test --all-safe
python smart_agent.py skills dogfood native_skill_vetter
python smart_agent.py skills docs-generate --dry-run
python smart_agent.py skills docs-generate --write
python smart_agent.py skills catalog
python smart_agent.py skills docs-check
python smart_agent.py skills propose-from-sessions
python smart_agent.py skills propose-from-commands
python smart_agent.py skills proposals list
python smart_agent.py skills proposals show <proposal_id>
python smart_agent.py skills proposals approve <proposal_id> --dry-run
python smart_agent.py skills improve-propose <skill_id>
python smart_agent.py skills improve-from-bugs <skill_id>
python smart_agent.py skills improve-from-dogfood <skill_id>
python smart_agent.py skills improvements list
python smart_agent.py skills improvements show <improvement_id>
python smart_agent.py skills find "I need to work with PDFs"
python smart_agent.py skills find "Can you help with meeting follow-up?"
python smart_agent.py skills inspect ./workspace/skills/example/SKILL.md
python smart_agent.py skills inspect native_skill_vetter
python smart_agent.py skills vet ./workspace/skills/example/SKILL.md
python smart_agent.py skills vet-folder ./workspace/skills/example
python smart_agent.py skills score ./workspace/skills/example/SKILL.md
python smart_agent.py skills report --last
```

Native skill manifests are metadata-only workflow definitions under `native_skills/` or `docs/native_skills/manifests/`. The loader reads and validates manifest fields, required capabilities, risk/trust levels, memory behavior, audit requirements, personal-data defaults, and CRITICAL approval rules. It does not execute scripts, import external code, install marketplace skills, grant permissions, or let manifests bypass `ToolBroker`.

Manifest dependency gates are detection-only. They check env var presence with redacted values, config key presence, local binary presence, workspace/project file presence, current platform, ToolBroker capability IDs, Python version, and setup hints for model features. They do not install packages, execute scripts, call providers, call connectors, or scan personal files.

Provenance and lockfile diagnostics track source type, review status, trust status, file hashes, manifest hashes, dependency hashes, and pin metadata. `skills lock status` is read-only and does not write `native_skills.lock`; `skills lock verify` reports `requires_setup` when no reviewed lockfile exists. There is no auto-update behavior.

Native skill roots and precedence are metadata-only diagnostics. Workspace, personal, reconstructed, and experimental skill roots are treated as untrusted candidate sources and cannot silently shadow trusted project or bundled native skills by default. Use `skills roots`, `skills precedence`, and `skills explain-root` to inspect setup hints and shadowing behavior.

Native skill profiles are advisory visibility rules for modes such as `default`, `research`, `coding`, `personal_assistant`, `lead_response`, `locked_down`, and `experimental`. Profiles can hide skills by allowlist, blocklist, category, risk ceiling, network/write/personal-data flags, and CRITICAL-action rules, but they do not enable skills or grant capabilities. `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, and `AuditLogger` remain the final authority for execution.

Native skill compatibility commands report platform/runtime/setup metadata across macOS, iOS companion, Windows, Linux, CLI-only, app bridge, and local web dashboard dimensions. They compute from manifests only and do not import native platform modules, execute skills, call providers, install dependencies, or enable platform-specific behavior.

Native skill conflict commands report duplicate skill IDs, command/capability overlaps, unsafe shadowing, missing dependencies, disabled providers, platform incompatibility, approval/memory policy mismatches, and missing docs/tests. They are metadata-only diagnostics and never auto-resolve, enable, disable, install, import, or execute skills; use `skills explain-conflict <conflict_id>` for one finding before human review.

Native skill test and dogfood commands validate reviewed skill metadata, dependency/setup status, provenance, lockfile status, conflicts, profile visibility, compatibility, prompt-injection fixtures, secret fixtures, docs, and command registry evidence. `skills test --all-safe` skips HIGH/CRITICAL/FORBIDDEN and personal-data skills by default. `skills dogfood <skill_id>` prints a plan only. These commands do not run external skill scripts, install dependencies, execute plugin runtimes, call providers, enable skills, grant permissions, or write memory.

Native skill docs generation creates `docs/native_skills/SKILL_CATALOG.md` from reviewed manifests, command registry metadata, compatibility/profile/provenance/lock status, tests, dogfood declarations, docs paths, and known limitations. `skills docs-generate` defaults to dry-run behavior; use `--write` only after reviewing the output. The generator preserves manual notes outside marked generated sections, reports missing docs, includes deprecated/blocked skills, and never executes skills, installs dependencies, calls providers, or invents maturity.

The native skill system release gate is recorded in `docs/native_skills/NATIVE_SKILL_SYSTEM_RELEASE_GATE.md` and `docs/native_skills/NATIVE_SKILL_SYSTEM_MATURITY_REVIEW.md`. It validates the metadata-only control plane and does not approve external skill installation, marketplace enablement, plugin runtime execution, or personal-data skill execution.

`skills find` searches only local reviewed metadata: native skill manifests, the native candidate matrix, feature registry, and maturity tracker. It returns implemented matches, planned candidates, maturity/readiness, required approvals, and next work needed. It does not browse external marketplaces, install skills, execute external code, or write memory.

Skill proposal commands create candidate ideas from redacted command/session metadata only. They skip personal-data patterns by default, mark higher-risk candidates for review, write redacted local proposal reports under `reports/autonomy/`, and never create, import, enable, install, or execute skills. `skills proposals approve <proposal_id> --dry-run` is a preview of review steps only.

Skill improvement commands create evidence-backed proposals from redacted bug and dogfood metadata. They include expected files, tests, docs, lockfile impact, rollback plan, and human-review status, but they do not modify skill files, update lockfiles, enable skills, execute scripts, or raise maturity. Use `skills improvements show <improvement_id>` as review evidence for a later explicit implementation prompt.

Native skill inspection and vetting are static analysis only. They read candidate skill files only from approved workspace/project skill paths or known native skill ids, treat them as `UNTRUSTED_DOCUMENT`, parse `SKILL.md` frontmatter when present, and flag scripts, shell commands, package installs, network calls, secret references, filesystem escapes, personal-data access, browser cookie/session access, prompt-injection language, approval-bypass language, opaque binaries, and missing license/tests/docs/risk metadata. The vetter never executes scripts, installs dependencies, grants permissions, accesses network, or stores skill content in memory by default. Vetting reports are saved under `reports/native_skills/`; all inspection/vetting commands execute through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.

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
python smart_agent.py schedule explain
python smart_agent.py schedule templates
python smart_agent.py schedule preview connector_doctor
python smart_agent.py schedule dry-run connector_doctor
python smart_agent.py schedule risks daily_briefing
python smart_agent.py schedule review
python smart_agent.py schedule list
python smart_agent.py schedule create --workflow connector_doctor --schedule daily@08:00 --name "Connector doctor"
python smart_agent.py schedule create --workflow daily_briefing --arg sections=weather --arg weather_location="Phoenix, AZ"
python smart_agent.py schedule create --workflow backup_create --arg backup_dir=workspace/backups
python smart_agent.py schedule run <schedule_id>
python smart_agent.py schedule pause <schedule_id>
python smart_agent.py schedule delete <schedule_id>
```

Scheduler v1 is manual-run only: it stores explicit local schedule records and never installs a LaunchAgent, cron job, daemon, login item, or hidden background runner. Scheduler UX commands let you explain, preview, dry-run, and review workflow metadata before manual runs; dry-runs execute no tools and create no Action Center items. Scheduled workflows still use the existing safety path where tools are involved; personal-data sections require approval, CRITICAL actions are never executed automatically, and scheduled backups are redacted-only brokered `backup.create` calls. Details live in `docs/SCHEDULER.md` and `docs/autonomy/SCHEDULER_UX.md`.

Subagent isolation profiles are mock-only safety metadata for future researcher/coder/tester/security/docs/planner roles:

```bash
python smart_agent.py subagents list
python smart_agent.py subagents show researcher
python smart_agent.py subagents policy
python smart_agent.py subagents dry-run coder "review this diff"
```

No real subagent launches in this scaffold. Profiles cannot call tools directly, write files by default, access personal data, execute CRITICAL actions, approve actions, or bypass ToolBroker/PolicyEngine/PermissionManager/ApprovalManager/AuditLogger. Dry-run output is `MODEL_OUTPUT` and reports `tools_executed=[]`.

Sandbox backend abstraction is mock-only and policy-first for future execution backends:

```bash
python smart_agent.py sandbox backends
python smart_agent.py sandbox policy
python smart_agent.py sandbox dry-run
```

Sandbox v1 does not execute commands, run scripts, install Docker/VM tools, start browser automation, enable networked sandboxes, mount broad filesystem roots, or access personal data. The mock backend is the only default backend; planned Docker/rootless, macOS sandbox, VM, browser, and cloud backends return setup/stub guidance until future approval gates add real execution.

Weather-aware research:

Simple weather prompts use weather tools only. Weather-impact prompts that need current public context, such as flight delays, school closures, or latest hurricane updates, may attach `web.search` in addition to weather tools when web search is configured. Web content remains `UNTRUSTED_WEB`, weather provider data and web results stay separated in workflow output, and the agent must not claim current closures or delays without web sources. Requests such as "near me" or "my area" do not infer personal location; configure an explicit default location first or provide a location in the request.

Weather provider abstraction:

```bash
python smart_agent.py weather doctor
python smart_agent.py weather providers
python smart_agent.py weather provider auto "Phoenix, AZ"
python smart_agent.py weather smoke "Phoenix, AZ"
python smart_agent.py weather current "San Francisco"
python smart_agent.py weather current "Phoenix, AZ" --provider auto
python smart_agent.py weather current "Phoenix, AZ" --provider weatherapi
python smart_agent.py weather current "Phoenix, AZ" --no-cache
python smart_agent.py weather forecast "San Francisco" --days 3
python smart_agent.py weather alerts "Los Angeles, CA" --provider nws
python smart_agent.py weather config show
python smart_agent.py weather config set-default "Phoenix, AZ"
python smart_agent.py weather config clear-default
python smart_agent.py weather cache clear
```

`weather.status`, `weather.current`, `weather.forecast`, `weather.alerts`, and `weather.cache_clear` are LOW-risk, audited, rate-limited, ToolBroker-only capabilities for user-provided locations. The `doctor` command checks provider configuration and capability policy without fetching weather data. `weather providers` shows cost-policy availability for Open-Meteo, NOAA/NWS, and WeatherAPI. `weather provider auto "<location>"` shows the selected free-first provider by executing the brokered current-weather path. The `smoke` command runs `weather.status`, `weather.current`, and `weather.forecast` through the broker for a user-provided location. Auto mode prefers Open-Meteo for current/forecast weather and NOAA/NWS for U.S. alerts; `WEATHER_PROVIDER=disabled` returns structured `weather provider is not configured` JSON.

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

WeatherAPI is available only as an optional paid/quota-limited fallback. A configured key does not make it the default under `free_first`. Explicit provider use requires `WEATHERAPI_API_KEY` or `WEATHER_API_KEY`; configured-default use also requires paid-API allowance through the cost policy.

```bash
export WEATHERAPI_API_KEY="..."
python smart_agent.py weather current "Phoenix, AZ" --provider weatherapi
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
python smart_agent.py messages draft --to "+15555555555" --body "Reviewed reply text"
python smart_agent.py messages handoff <draft_id>
python smart_agent.py actions approve <action_id>
python smart_agent.py messages save-draft <draft_id>
python smart_agent.py messages copy-draft <draft_id>
python smart_agent.py messages save-draft --from-action <action_id>
python smart_agent.py messages copy-draft --from-action <action_id>
python smart_agent.py messages macos status
python smart_agent.py messages macos allow-recipient "+15555555555"
python smart_agent.py messages macos live-send-probe --to "+15555555555"
python smart_agent.py messages send --from-action <action_id>
```

Messages read/draft tools are disabled by default and approval-gated where personal data is involved. The project does not scrape `~/Library/Messages`, does not request broad Full Disk Access, and does not bulk-read history. The safe fallback is the brokered `messages.draft_from_text` capability using a manually provided UTF-8 text file inside `./workspace`; its content is treated as `UNTRUSTED_MESSAGE`, audited as a file read, labeled as data rather than instructions, not stored in long-term memory, and used only to create a draft. Draft replies are marked draft-only and never delete, move, archive, harvest contacts, or modify messages.

Messages safe handoff:

`messages draft-from-text` now queues reviewed Action Center handoff records for saving the draft to `./workspace` or copying it to the clipboard. `messages.save_draft` and `messages.copy_draft` are disabled by default, HIGH risk, approval-required, and never send a message. Low-level save/copy tool execution requires the verified Action Center action id, and submitted recipient/draft/path arguments must match the approved preview. Saved drafts must remain inside approved workspace paths. Clipboard copy requires an approved Action Center item because clipboard contents may be personal data and can be read by other local apps.

macOS approved iMessage sending is experimental and disabled by default. It requires `MACOS_MESSAGES_ENABLED=true`, `MACOS_MESSAGES_ALLOW_SEND=true`, one allowlisted recipient, a recent passing `messages macos live-send-probe`, a `channel=macos_messages` local draft, an exact `messages.macos.send_approved` Action Center item, CRITICAL per-action approval with no reuse, and the daily send rate limit. Unsupported machines return a clear error and should use iOS compose, manual handoff, or Apple Messages for Business planning instead.

The draft-id handoff workflow stores reviewed local drafts in `./workspace/messaging/drafts/` and lets the user inspect or edit them before any handoff. `messages draft` creates a manual-handoff draft from user-provided text. `messages draft-from-text` reads only an approved workspace context file, labels it `UNTRUSTED_MESSAGE`, creates a local draft record, and creates pending save/copy Action Center items. `messages handoff <draft_id>` recreates reviewed save/copy handoff actions for an existing draft. `messages save-draft <draft_id>` and `messages copy-draft <draft_id>` execute only after a matching approved Action Center action exists; otherwise they return the pending approval instructions. `messages.draft_from_lead` is available for mock/selected Lead Inbox draft creation only and does not create send actions.

Incoming message manual/mock inbox:

```bash
python smart_agent.py messages import --from-file ./workspace/incoming_message.md
python smart_agent.py messages inbox list
python smart_agent.py messages inbox show <message_id>
python smart_agent.py messages inbox draft-reply <message_id>
```

Incoming message v1 is manual/mock only. Manual imports must be user-selected files inside `./workspace`, are labeled `UNTRUSTED_MESSAGE`, and are stored under `./workspace/messaging/inbound/`. The inbox can list/show manual and mock messages, expose Lead Inbox candidate metadata, and create a local draft reply under `./workspace/messaging/drafts/`. It does not read `~/Library/Messages`, does not request Full Disk Access, does not run a background watcher, does not auto-reply, does not send, and does not write message bodies to memory by default. See `docs/decisions/incoming_message_strategy.md`.

macOS Messages feasibility probe:

```bash
python smart_agent.py messages probe
python smart_agent.py messages probe --explain-permissions
```

The probe is metadata-only. It checks macOS, standard Messages.app locations, AppleScript availability, and harmless application identity/version lookup where possible. It records a redacted connector-status artifact and audit event, but it does not read `~/Library/Messages`, request Full Disk Access, read message content, inspect account status, or press Send. This metadata probe does not prove send support; the separate `messages macos live-send-probe` is CRITICAL and disabled by default.

Messaging architecture:

```bash
python smart_agent.py messaging channels
python smart_agent.py messaging draft-create --channel manual_handoff --to "Name" --body "Reviewed reply"
python smart_agent.py messaging draft show <draft_id>
python smart_agent.py messaging draft validate <draft_id>
python smart_agent.py messaging create-send-action <draft_id>
python smart_agent.py messaging ios-compose-payload <draft_id>
python smart_agent.py messaging ios-compose-status <draft_id>
```

The channel-neutral messaging layer defines one internal schema for future `ios_compose`, `macos_messages`, `apple_messages_for_business`, `telegram`, `email`, `manual_handoff`, and `mock` adapters. It can create local workspace drafts and create a CRITICAL Action Center send proposal with an exact local preview showing channel, recipient, full body, attachments, source context, rollback impossibility, explicit per-action approval, allowlist status, and rate-limit status. Creating or editing a draft invalidates older pending/approved send actions for that draft.

The channel layer itself still does not send. Unknown channels are denied, group/bulk recipients are rejected, attachments are denied for send actions, and send approval reuse is forbidden. The only executable message-send adapter in this build is `messages.macos.send_approved`, and it is disabled by default plus probe/allowlist/Action Center gated. Local draft files live under `./workspace/messaging/drafts/`; broker audit logs and action exports redact bodies/recipients while the local Action Center preview remains exact for user review. The layer does not read private app data, access Messages databases, request Full Disk Access, or store message content in memory.

iOS user-confirmed compose bridge:

`messaging ios-compose-payload` creates a local handoff payload under `./workspace/messaging/ios_compose/payloads/` for a future iOS companion app or deep-link bridge. The payload contains the exact draft recipient and body, expiration timestamp, nonce, integrity hash, risk level, and approval status. It either uses a matching approved Action Center action via `--from-action <action_id>` or the command's user-confirmed compose mode, where Apple's compose UI is the final confirmation surface. The user must tap Send or Cancel in iOS; the agent has no silent-send path and cannot mark a send complete unless a future iOS companion app reports `sent` or `queued`. Status records stay under `./workspace/messaging/ios_compose/results/`. See `docs/decisions/ios_companion_message_compose.md`.

Lead Inbox abstraction:

```bash
python smart_agent.py leads list
python smart_agent.py leads show mock-lead-001
python smart_agent.py leads classify mock-lead-001
python smart_agent.py leads summarize mock-lead-001
python smart_agent.py leads draft-response mock-lead-001
python smart_agent.py leads suggest-followup mock-lead-001
python smart_agent.py leads suggest-meeting mock-lead-001
python smart_agent.py leads create-send-action mock-lead-001 <draft_id>
python smart_agent.py leads send --from-action <action_id>
python smart_agent.py leads handoff <draft_id>
python smart_agent.py leads mark-responded mock-lead-001
```

Lead Inbox v1 is channel-neutral and mock-only. It defines the shared schema for future Gmail, Telegram, Apple Messages for Business, personal iMessage manual handoff, web form, manual, and mock sources, but it does not read real provider inboxes or send responses. `leads list`, `leads classify`, `leads summarize`, `leads draft-response`, `leads suggest-followup`, and `leads suggest-meeting` use synthetic mock/local records through `ToolBroker`; `leads show` represents future selected full-message reads and is HIGH risk plus disabled by default until a selected-scope provider is explicitly approved.

Lead content is treated as untrusted message data. Classification and summarization create no actions, draft-response creates an editable local `MessageDraft` with source and assumptions, suggest-followup queues a pending Action Center `tasks.create` item without creating a real task, and suggest-meeting reads no calendar and creates no event. `leads create-send-action` creates a CRITICAL exact-preview Action Center proposal only. `leads send --from-action` either routes to an already gated channel path, such as iOS compose handoff or disabled-by-default macOS Messages, or returns fallback options. Manual handoff saves/copies only after separate approval. No lead content is written to long-term memory by default, no CRM sync exists in v1, bulk responses are forbidden, auto-send is disabled, and approval reuse is denied. See `docs/workflows/lead_response_drafting.md` and `docs/workflows/lead_response_send.md`.

Apple Messages for Business provider stub:

```bash
python smart_agent.py apple-business doctor
python smart_agent.py apple-business status
python smart_agent.py apple-business mock-inbound
python smart_agent.py apple-business draft-response <lead_id>
```

The Apple Messages for Business v1 path is a mock/local provider stub for the business lead-response lane. `apple-business doctor` and `status` are config metadata only and do not call a provider or print secrets. `mock-inbound` writes a local `UNTRUSTED_MESSAGE` Lead Inbox record under `./workspace/leads/apple_business/`; `draft-response` creates a local `MessageDraft` with `channel=apple_messages_for_business`. Live provider credentials are not required, live webhooks are not polled, personal iMessage automation is not used, and no send action or send execution is added. Future Apple Business sends remain disabled, CRITICAL, exact-preview, per-action, and no-reuse.

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
python smart_agent.py memory context-preview "ToolBroker" --max-records 3
python smart_agent.py memory continuity status
python smart_agent.py memory continuity build-summary --query "ToolBroker"
python smart_agent.py memory continuity clear
```

Memory refuses secrets and personal email/message/contact/calendar content by default. Approval-gated personal memory exists as a separate capability. Memory search supports category filters, and context injection is bounded, non-personal by default, redacted, and audited with the injected memory IDs. `context-preview` shows the bounded context candidate without injecting it. Continuity commands build redacted, non-personal summaries only; they do not create a separate continuity store, use cloud embeddings, write memory, or carry personal data by default. Deletion is best effort: SQLite rows are deleted and `VACUUM` is attempted, but external logs and filesystem backups are not rewritten. See [docs/memory/LONG_TERM_MEMORY_SEARCH.md](</Users/sambehdjou/Documents/AI Super Agent/docs/memory/LONG_TERM_MEMORY_SEARCH.md>), [docs/memory/CROSS_SESSION_CONTINUITY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/memory/CROSS_SESSION_CONTINUITY.md>), and [docs/memory/MEMORY_INJECTION_POLICY.md](</Users/sambehdjou/Documents/AI Super Agent/docs/memory/MEMORY_INJECTION_POLICY.md>).

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
python smart_agent.py backup roundtrip --dry-run
python smart_agent.py backup policy-check
python smart_agent.py backup restore-check <backup_id>
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
python smart_agent.py backup roundtrip --dry-run
python smart_agent.py backup policy-check
python smart_agent.py backup restore-check <backup_id>
python smart_agent.py backup restore <backup_id>
```

Backups are local redacted archive directories under `workspace/backups` by default, or under `BACKUP_DIR` / `--backup-dir` when explicitly configured. Backup v1 includes config with secrets redacted, docs/tracking files, feature registry/maturity/roadmap, native skill manifests, redacted memory export metadata, redacted Action Center metadata, optional captures, and optional audit metadata. It never fetches personal connector data and does not store or export API keys, tokens, `.env`, private keys, raw mail/messages/calendar/contact data, or browser/session data. Each archive has `manifest.json` with content hashes and an integrity hash. `backup roundtrip --dry-run`, `backup policy-check`, and `backup restore-check` are read-only/brokered guard commands. `backup restore` is HIGH risk, approval-gated, verifies hashes first, creates pre-restore copies where possible, and rejects backed-up capability manifests or archive contents that would weaken policy, reuse CRITICAL approvals, enable personal connectors, expose unredacted secrets, or traverse paths. Live restore smoke tests should use disposable project copies only.

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

This project requires Python 3.11 or newer. Python 3.12 is the recommended local runtime. macOS may run Apple Python 3.9 when you type `python3`; that version is not supported. `smart_agent.py` checks the Python version before importing agent modules and prints setup commands instead of crashing.

Recommended local setup:

```bash
cd "/Users/sambehdjou/Documents/AI Super Agent"
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

If `python3.12` is not installed:

```bash
brew install python@3.12
```

Use the local launcher after setup:

```bash
./scripts/agent doctor
./scripts/agent --no-tools "Explain RCS vs iMessage"
```

The launcher prefers `AI_AGENT_PYTHON`, then `./.venv/bin/python`, then `python3.12`. If none are available, it prints setup guidance instead of falling back to Apple Python 3.9.

Developer shortcuts:

```bash
make doctor
make test
make policy-check
make command-check
make run MESSAGE="Explain RCS vs iMessage"
```

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
PLATFORM_BRIDGES_ENABLED=false
PLATFORM_BRIDGE_MODE=auto
PLATFORM_DETECTION_CACHE_SECONDS=300
PLATFORM_LAZY_LOAD_BRIDGES=true
MACOS_BRIDGE_ENABLED=false
IOS_COMPANION_BRIDGE_ENABLED=false
WINDOWS_BRIDGE_ENABLED=false
WEB_APP_BRIDGE_ENABLED=false
APP_BRIDGE_ENABLED=false
APP_BRIDGE_HOST=127.0.0.1
APP_BRIDGE_PORT=
APP_BRIDGE_TRANSPORT=stdio
APP_BRIDGE_REQUIRE_PAIRING=true
APP_BRIDGE_ALLOW_REMOTE=false
WEB_ACCESS_ENABLED=true
PROVIDER_COST_MODE=free_first
ALLOW_PAID_APIS=false
MAX_PAID_API_CALLS_PER_DAY=0
SEARCH_DEFAULT_PROVIDER=auto
WEB_SEARCH_PROVIDER=brave
BRAVE_SEARCH_API_KEY=
BRAVE_SEARCH_ENABLED=false
BRAVE_SEARCH_TIMEOUT_SECONDS=10
BRAVE_SEARCH_MAX_RESULTS=10
BRAVE_SEARCH_SAFE_SEARCH=true
SEARXNG_BASE_URL=
SERPAPI_API_KEY=
SERPAPI_ENABLED=false
SERPAPI_TIMEOUT_SECONDS=10
SERPAPI_MAX_RESULTS=10
WEB_SEARCH_TIMEOUT_SECONDS=10
WEB_SEARCH_MAX_RESULTS=8
WEB_SAFE_SEARCH=true
WEB_SEARCH_AUDIT_QUERIES=false
WEB_FETCH_MAX_BYTES=500000
WEATHER_DEFAULT_PROVIDER=auto
WEATHER_PROVIDER=open_meteo
WEATHER_API_KEY=
WEATHERAPI_API_KEY=
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
GMAIL_USER=
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_TOKEN_PATH=
GMAIL_SCOPES=
MESSAGES_CONNECTOR=
MESSAGES_THREAD_MAX_CHARS=12000
TELEGRAM_BOT_TOKEN=
TELEGRAM_DEFAULT_CHAT_ID=
TELEGRAM_ALLOWED_CHAT_IDS=
```

`TOOL_MODE` may be `auto`, `no-tools`, or `force-time`. The older `LMSTUDIO_TEMPERATURE`, `LMSTUDIO_TOP_P`, `LMSTUDIO_MAX_TOKENS`, and `AGENT_AUDIT_LOG` names are still accepted as fallbacks.

### App Bridge Contract

Future Mac, iOS companion, Windows, or local web frontends use the App Bridge contract documented in `docs/platforms/APP_BRIDGE_API.md`. The bridge is disabled by default, local-only in v1, requires pairing before sensitive surfaces, starts no server during import, and cannot approve actions, execute tools, change policy, read personal data, or bypass ToolBroker/PolicyEngine/ApprovalManager/AuditLogger.

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
python smart_agent.py eval run --natural-language
python smart_agent.py eval run --lmstudio-live
python smart_agent.py eval run --web
python smart_agent.py eval run --weather
python smart_agent.py eval run --workspace
python smart_agent.py eval run --memory
python smart_agent.py eval report
```

`eval run --safe` now runs the Golden Eval Suite: data-file backed router checks, policy allow/ask/deny checks, ToolBroker denial/allow checks, prompt-injection wrapper checks, natural-language command understanding fixtures, workflow dry-runs, no-tool LM Studio chat when `LMSTUDIO_MODEL` is configured, safe time-tool execution, weather current/forecast when a provider is configured, web search/fetch when configured, controlled workspace read/write under `./workspace/eval`, non-sensitive memory add/search/delete, dry-run/preflight, and connector doctor checks. Personal-data evals for calendar, contacts, email, and messages are skipped by default. `eval run --natural-language` runs only the natural-language fixtures and executes no mapped commands.

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
python smart_agent.py dogfood plan
python smart_agent.py dogfood next
python smart_agent.py dogfood checklist
python smart_agent.py dogfood show all_safe
python smart_agent.py dogfood run all_safe --dry-run
python smart_agent.py dogfood run all_safe
python smart_agent.py session start --name dogfood-all-safe
python smart_agent.py dogfood run all_safe --session
python smart_agent.py dogfood run natural_language_core --session
python smart_agent.py dogfood run natural_language_risky --session
python smart_agent.py session replay --last
python smart_agent.py session end
```

Suites live in `dogfood_suites/` and are documented in [docs/dogfood/DOGFOOD_GUIDE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/DOGFOOD_GUIDE.md>) and [docs/dogfood/COMMAND_SUITES.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/COMMAND_SUITES.md>). The live validation workflow is documented in [docs/dogfood/LIVE_TEST_RUNBOOK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/LIVE_TEST_RUNBOOK.md>), with daily and weekly checklists in [docs/dogfood/DAILY_DOGFOOD_CHECKLIST.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/DAILY_DOGFOOD_CHECKLIST.md>) and [docs/dogfood/WEEKLY_RELEASE_CHECK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/dogfood/WEEKLY_RELEASE_CHECK.md>). Natural-language command dogfood is documented in [docs/natural_language/NL_DOGFOOD_RUNBOOK.md](</Users/sambehdjou/Documents/AI Super Agent/docs/natural_language/NL_DOGFOOD_RUNBOOK.md>). Start with `all_safe`; use `personal_dry_run` only for preflight-only personal connector checks.

Daily dogfood should start a session, run safe suites, add feedback, end the session, review it, generate bugs for confirmed failures, and create regression tests when feasible. `dogfood next` uses feature maturity notes plus the latest session metadata to recommend the next safe step without running commands.

For natural-language command misunderstandings, attach redacted feedback and create a local bug/fixture:

```bash
python smart_agent.py feedback nl-bug --last --expected-intent weather.current
python smart_agent.py bugs create-nl-regression BUG-0001
python smart_agent.py nl regressions list
```

See [docs/natural_language/NL_BUG_TRIAGE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/natural_language/NL_BUG_TRIAGE.md>) for the supported tags and review rules.

Natural-language command release-gate evidence is tracked in [docs/natural_language/NL_COMMAND_RELEASE_GATE.md](</Users/sambehdjou/Documents/AI Super Agent/docs/natural_language/NL_COMMAND_RELEASE_GATE.md>) and [docs/natural_language/NL_COMMAND_MATURITY_REVIEW.md](</Users/sambehdjou/Documents/AI Super Agent/docs/natural_language/NL_COMMAND_MATURITY_REVIEW.md>).

## Product Quality Dashboard

The product quality dashboard is a read-only local health view over redacted session metadata, feedback, bug records, regression-test links, eval reports, feature maturity, and release-gate docs.

```bash
python smart_agent.py quality status
python smart_agent.py quality sessions
python smart_agent.py quality bugs
python smart_agent.py quality regressions
python smart_agent.py quality features
python smart_agent.py quality next
```

`quality status` shows the latest session result, last recorded full test result, open bugs by severity, recent feedback, features lacking live validation or regression coverage, mature/immature feature summaries, the next dogfood recommendation, and release-gate status. It does not execute tools, read personal connectors, show raw personal data, grant approvals, or write memory.

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
