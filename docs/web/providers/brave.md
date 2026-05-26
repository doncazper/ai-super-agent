# Brave Search Provider

Brave Search is an optional quota-limited search provider for public web results. It is not a free-first default and is never selected merely because `BRAVE_SEARCH_API_KEY` exists.

## Policy

- Disabled by default with `BRAVE_SEARCH_ENABLED=false`.
- Requires `BRAVE_SEARCH_API_KEY`.
- Requires cost-policy opt-in before execution: `ALLOW_PAID_APIS=true` and `MAX_PAID_API_CALLS_PER_DAY>0`.
- Runs only through `ToolBroker` as `web.search`.
- Results are labeled `UNTRUSTED_WEB`.
- Search history is not stored by default.
- API keys and sensitive queries are redacted from audit logs.
- CAPTCHA, anti-bot, login-wall, paywall, or browser-profile bypass is forbidden.

## Configuration

```bash
export WEB_ACCESS_ENABLED=true
export WEB_SEARCH_PROVIDER=brave
export BRAVE_SEARCH_API_KEY="..."
export BRAVE_SEARCH_ENABLED=true
export BRAVE_SEARCH_TIMEOUT_SECONDS=10
export BRAVE_SEARCH_MAX_RESULTS=10
export BRAVE_SEARCH_SAFE_SEARCH=true
export ALLOW_PAID_APIS=true
export MAX_PAID_API_CALLS_PER_DAY=5
```

`BRAVE_SEARCH_ENABLED=true` is not enough by itself. The paid/quota policy must also allow provider use.

## Commands

```bash
python smart_agent.py web brave doctor
python smart_agent.py connectors status brave
python smart_agent.py web search "local AI news" --provider brave
```

The doctor and connector status commands are config-only checks. They do not call Brave Search and do not print the API key.

Secret setup is tracked in `docs/secrets/PROVIDER_SECRET_SETUP.md`. Run `python smart_agent.py secrets doctor brave` to check whether `BRAVE_SEARCH_API_KEY` appears configured without showing the value, and run `python smart_agent.py secrets scan` before committing any config changes.

## Errors

- Missing key returns setup guidance for `BRAVE_SEARCH_API_KEY`.
- Disabled provider returns setup guidance for `BRAVE_SEARCH_ENABLED=true`.
- Cost-policy denial returns setup guidance for `ALLOW_PAID_APIS=true` and a nonzero daily paid-call cap.
- HTTP 401/403, 429, timeout, malformed JSON, and provider errors are normalized into structured command errors.

## Limitations

Live Brave Search validation requires a user-provided key and explicit cost-policy opt-in. Unit tests use mocked HTTP responses only.
