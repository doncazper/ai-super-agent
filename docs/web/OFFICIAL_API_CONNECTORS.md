# Official API Connectors

Official API connectors are the preferred path for public web sources that expose documented APIs. This framework is a local v1 scaffold: it defines provider interfaces, status metadata, domain matching, result normalization, ToolBroker-routed commands, and setup hints. It does not make live API calls by default.

## Commands

```bash
python smart_agent.py web official-apis
python smart_agent.py web api-status github
python smart_agent.py web api-search github "openai"
```

`official-apis` and `api-status` are metadata-only. `api-search` routes through `ToolBroker` as `web.official_api.search`; in this milestone the built-in providers return setup hints unless tests inject mocked public results or a later approved live connector is implemented.

## Provider Candidates

- GitHub public API: public repository/resource candidate; no personal account data in v1.
- Wikipedia/Wikidata: public encyclopedia and entity APIs; no account data.
- arXiv: public paper metadata API; no account data.
- Reddit Data API: read-only setup-gated stub only; no Reddit web scraping substitute.
- Crossref/OpenAlex/Semantic Scholar: documented as future candidates, not implemented in this milestone.

## Safety Rules

- All execution must go through `ToolBroker`, `PolicyEngine`, and `AuditLogger`.
- API keys and OAuth tokens must never be printed.
- OAuth/authenticated APIs remain disabled unless a later provider-specific prompt implements and gates them.
- No write operations are exposed.
- No personal account data is read by status checks.
- Results are labeled `UNTRUSTED_WEB`.
- Query text is redacted in audit logs by default.
- No search history or article body is stored in memory by default.
- Reddit web pages must not be scraped as an API substitute.

## Provider Matching

The registry can match known public domains to official providers:

- `github.com` and `api.github.com` -> `github`
- `wikipedia.org`, `wikidata.org`, and `mediawiki.org` -> `wikipedia`
- `arxiv.org` and `export.arxiv.org` -> `arxiv`
- `reddit.com`, `old.reddit.com`, `redd.it`, and `oauth.reddit.com` -> `reddit`

Matching is advisory. A matched provider still cannot execute unless its capability exists in the manifest, the provider is configured/enabled, and the call is brokered.

## Current Limitations

- Built-in live provider calls are deferred.
- Public provider normalization is covered with mocked results.
- Reddit remains a read-only OAuth-gated stub.
- Crossref/OpenAlex/Semantic Scholar are planned candidates only.
