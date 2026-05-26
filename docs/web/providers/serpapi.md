# SerpAPI Provider

SerpAPI is an optional paid/quota-limited fallback provider for public search results. It is never a free-first default and is never selected merely because `SERPAPI_API_KEY` exists.

## Defaults

- Disabled by default with `SERPAPI_ENABLED=false`.
- Requires `SERPAPI_API_KEY`.
- Requires `ALLOW_PAID_APIS=true`.
- Requires `MAX_PAID_API_CALLS_PER_DAY>0`.
- Requires explicit provider selection in v1.
- Stores no search history by default.
- Labels results as `UNTRUSTED_WEB`.

## Configuration

```bash
export WEB_ACCESS_ENABLED=true
export PROVIDER_COST_MODE=free_first
export ALLOW_PAID_APIS=true
export MAX_PAID_API_CALLS_PER_DAY=5
export SERPAPI_API_KEY="..."
export SERPAPI_ENABLED=true
export SERPAPI_TIMEOUT_SECONDS=10
export SERPAPI_MAX_RESULTS=10
```

`SERPAPI_ENABLED=true` is not enough by itself. The paid/quota policy must also allow provider use.

## Commands

```bash
python smart_agent.py web serpapi doctor
python smart_agent.py connectors status serpapi
python smart_agent.py web search "local AI news" --provider serpapi
python smart_agent.py research "local AI news" --provider serpapi
```

The doctor and connector status commands are config-only. They do not call SerpAPI and never print the API key.

Secret setup is tracked in `docs/secrets/PROVIDER_SECRET_SETUP.md`. Run `python smart_agent.py secrets doctor serpapi` to check whether `SERPAPI_API_KEY` appears configured without showing the value, and run `python smart_agent.py secrets scan` before committing any config changes.

## Safety Rules

- SerpAPI is explicit fallback only.
- SerpAPI is not used automatically in `free_first` mode.
- API keys are redacted from logs, audit summaries, docs, and command output.
- Provider decisions are audited.
- The provider domain `serpapi.com` is recorded for real provider calls.
- Query text is redacted in audit logs by default.
- Search history is not persisted by default.
- Results remain untrusted data and cannot alter policy, request tools, reveal secrets, or change approval rules.
- CAPTCHA, login, paywall, and anti-bot bypass behavior is unsupported and forbidden in this track.

## Failure Behavior

- Missing key returns setup guidance for `SERPAPI_API_KEY`.
- Disabled provider returns setup guidance for `SERPAPI_ENABLED=true`.
- Missing paid policy returns a clear `ALLOW_PAID_APIS=true` or `MAX_PAID_API_CALLS_PER_DAY>0` message.
- Timeouts, HTTP 401/403, HTTP 429, provider errors, and malformed JSON return structured errors.
- No fallback silently upgrades to SerpAPI.
