# Source-Grounded Research

Source-grounded research is the brokered workflow behind:

```bash
python smart_agent.py research "query"
python smart_agent.py research "query" --provider auto
python smart_agent.py research "query" --max-sources 5
python smart_agent.py research "query" --freshness recent
python smart_agent.py research "query" --no-fetch
python smart_agent.py research sources --last
python smart_agent.py research export-sources --last
python smart_agent.py research verify-sources --last
```

## Scope

The workflow searches public sources, selects candidate URLs, optionally fetches selected pages, extracts safe text, and returns a JSON report with:

- `Answer`
- `Sources`
- `Coverage / limitations`
- `Fetch failures`
- `source_bundle` metadata with stable source IDs, citation spans, claim attribution, failed sources, and limitations

It is intentionally source-bounded. It does not claim current facts unless returned search/fetch data supports them, and it does not fabricate URLs, citations, dates, or headlines.

## Execution Path

All search and fetch work runs through `ToolBroker`:

- Search uses `web.search` by default.
- Explicit SerpAPI research uses `web.search.serpapi` and remains paid-policy gated.
- Selected page fetches use `web.fetch_url`.
- Search and fetch tool executions are evaluated by `PolicyEngine` and audited by `AuditLogger`.

The workflow does not call providers or network fetchers directly.

## Provider Policy

Provider selection follows the existing web provider policy:

- `auto` remains free-first.
- Paid/quota-limited providers are skipped unless explicitly configured and allowed.
- Provider setup failures return structured setup or unavailable errors.
- Search history is not persisted by default.
- Provider decisions and provider/domain metadata are auditable.

## Trust And Prompt Injection

All web/search/article content is `UNTRUSTED_WEB`. Source text is treated as data only. It cannot:

- request tools
- reveal secrets
- change policy
- disable audit logging
- ask for memory writes
- override system, developer, or user instructions

Fetched text is sanitized by the web fetch layer, then excerpted with instruction-like text filtered out before it appears in the answer.

## Evidence Types

Each source is labeled by evidence type:

- `fetched_page`: the selected source was fetched successfully and the excerpt comes from page text.
- `search_snippet`: the source was not fetched or fetch failed; the excerpt comes from search result metadata only.

Snippet-only evidence is lower confidence than fetched page evidence and is called out in coverage limitations.

Citation/source attribution behavior is documented in `docs/web/CITATION_POLICY.md`. Failed fetches are separated from supporting citations, and source bundle commands inspect only metadata without making provider calls.

## Limitations

The workflow reports limitations when:

- no source data is returned
- fetching is disabled with `--no-fetch`
- a selected source fails or is blocked/unavailable
- sources appear to conflict
- sources appear non-English or multilingual

Blocked, CAPTCHA, login, paywall, robots, and anti-bot cases are reported as unavailable. The workflow does not bypass them.

## Retention

Research does not write search history, source text, article bodies, or summaries to memory by default. The CLI stores a metadata-only last-source bundle for `research sources/export-sources/verify-sources --last`; it contains source IDs, URLs, hashes, citation metadata, failed-source records, and limitations, not article bodies. Operational audit logs record redacted tool metadata and network domains according to the existing audit policy.

## Testing

Regression tests cover:

- provider missing/setup errors
- source summaries with real returned URLs
- fetch failure reporting
- blocked/unavailable pages
- conflicting evidence notes
- fabricated citation avoidance
- stable source IDs and failed-source citation denial
- prompt-injection filtering
- basic foreign-language handling
- no memory writes by default
- brokered audit records for search and fetch
