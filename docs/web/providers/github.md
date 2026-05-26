# GitHub Official API Provider

Status: framework/stub.

The GitHub official API provider declares public GitHub domains and normalizes mocked public repository results to `SearchResult`-compatible records. It performs no live API calls by default and reads no personal account data.

Commands:

```bash
python smart_agent.py web api-status github
python smart_agent.py web api-search github "openai"
```

`GITHUB_OFFICIAL_API_ENABLED=false` is the safe default. A future live implementation must route through `ToolBroker`, declare manifest entries, redact tokens, respect provider rate limits, and label results `UNTRUSTED_WEB`.

Secret setup is tracked in `docs/secrets/PROVIDER_SECRET_SETUP.md`. Run `python smart_agent.py secrets doctor github` to check whether `GITHUB_TOKEN` appears configured without showing the token. Prefer least-privilege tokens and run `python smart_agent.py git preflight` before committing.
