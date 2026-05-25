# SearXNG Provider

SearXNG is the preferred free/self-hosted search provider for the Internet Access track. It is optional and disabled by default.

## Safety Defaults

- No public SearXNG instance is used by default.
- Search only runs when `SEARXNG_BASE_URL` is set and `SEARXNG_ENABLED=true`.
- SearXNG requires no API key.
- Results are labeled `UNTRUSTED_WEB`.
- Query history is not persisted by default.
- Provider calls must route through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.
- Webpage text and search snippets are data only; they cannot request tools, reveal secrets, alter policy, or bypass rules.

## Configuration

```bash
export WEB_ACCESS_ENABLED=true
export WEB_SEARCH_PROVIDER=searxng
export SEARXNG_BASE_URL="https://search.example"
export SEARXNG_ENABLED=true
export SEARXNG_TIMEOUT_SECONDS=10
export SEARXNG_MAX_RESULTS=10
export SEARXNG_SAFE_SEARCH=1
export SEARXNG_CATEGORIES=general
```

The configured instance must support JSON responses for `/search?format=json`. If JSON output is disabled or blocked, the provider returns a setup error instead of scraping HTML.

## Commands

```bash
python smart_agent.py web searxng doctor
python smart_agent.py connectors status searxng
python smart_agent.py web search "local AI news" --provider searxng
```

`web searxng doctor` and `connectors status searxng` are config-only checks. They do not call the provider.

## Error Handling

- Missing `SEARXNG_BASE_URL`: setup hint.
- `SEARXNG_ENABLED=false`: setup hint.
- Invalid base URL: setup hint.
- Timeout: structured timeout error.
- HTTP 403: clear JSON/API-access setup hint.
- HTTP 429: rate-limit error.
- Malformed JSON or HTML response: clear JSON-output setup hint.

## Release Notes

Live validation requires a user-configured self-hosted instance. Unit tests use mocked HTTP responses and do not call public providers.
