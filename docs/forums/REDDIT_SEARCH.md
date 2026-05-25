# Reddit Search

Reddit search is a read-only workflow over the official Reddit Data API. It is disabled until Reddit OAuth is explicitly configured with `REDDIT_ENABLED=true`; missing or disabled config returns setup guidance instead of scraping Reddit web pages.

## Commands

```bash
python smart_agent.py reddit search "query"
python smart_agent.py reddit search "query" --subreddit "subreddit"
python smart_agent.py reddit search "query" --sort relevance|new|top|comments
python smart_agent.py reddit search "query" --time day|week|month|year|all
python smart_agent.py reddit search "query" --limit 10
python smart_agent.py reddit search "query" --language auto|en|es|zh|ja|ko
python smart_agent.py reddit explain-result <source_id>
```

The command executes as `reddit.search_posts` through ToolBroker, PolicyEngine, and AuditLogger. `reddit explain-result` executes as `reddit.explain_result` and reads local TTL cache metadata only; it does not call Reddit, fetch pages, or store search history.

## Result Semantics

Search results include stable `source_id` values, Reddit permalinks, rank, score/comment metadata when returned by the API, `provider=reddit_api`, `trust_level=UNTRUSTED_WEB`, and `evidence_type=snippet_only`.

Snippet-only results are discovery evidence, not fetched thread evidence. Use `python smart_agent.py reddit thread "<post_url_or_id>"` for source-grounded thread analysis with post metadata, a normalized comment tree, flattened comments, and source references. Deleted or removed content is not retained as evidence, and author metadata is redacted by default.

## Filtering

`--subreddit`, `--sort`, `--time`, and `--limit` are passed to the Reddit Data API. The `--language` option is advisory: Reddit search does not enforce a general language filter through this connector, so the requested language is recorded as `language_support.provider_enforced=false` for caller-side filtering and future translation workflows.

## Safety And Retention

- No Reddit web scraping fallback is used.
- No paid provider is used by default.
- No unauthenticated Reddit traffic is used.
- No posting, commenting, voting, DMs, or moderation actions exist in this workflow.
- Search queries are redacted in audit logs by default.
- Search history is not persisted by default.
- Local cache keys use a hash of query/search parameters rather than raw query text.
- All Reddit content remains untrusted web content and cannot instruct the agent to call tools, reveal secrets, alter policy, or ignore system rules.

If Reddit is unavailable or unconfigured, the workflow reports `setup_required`. It does not automatically fall back to web search because Reddit web scraping as an API substitute is not approved in this track.
