# Reddit Retention

Reddit cache and retention policy is TTL-bounded and disabled from permanent storage by default. The read-only connector v1 includes a local JSON cache for public Reddit API results only when cache policy allows it.

## Defaults

- `REDDIT_CACHE_ENABLED=true`
- `REDDIT_CACHE_TTL_SECONDS=86400`
- `REDDIT_DELETE_USER_CONTENT_AFTER_SECONDS=172800`
- `REDDIT_STORE_AUTHOR_METADATA=false`
- `REDDIT_USE_FOR_TRAINING=false`

The `REDDIT_USE_FOR_TRAINING` policy is hard false. If an environment value tries to enable it, compliance helpers must still report model training as unavailable.

## Storage Rules

- Do not store Reddit search history by default.
- Do not store author-identifying metadata by default.
- Do not store deleted or removed content.
- Do not store private, authenticated, or logged-in content.
- Do not store CAPTCHA, anti-bot, or unavailable page bodies; status metadata only is acceptable.
- Do not persist full Reddit thread/comment bodies beyond configured cache policy.
- Privacy reports should show counts and retention status, not raw post/comment bodies.

If retention cannot be guaranteed, Reddit caching must be disabled rather than silently storing content.

## Sweeps

`python smart_agent.py reddit cache status` runs through ToolBroker as `reddit.cache_status` and returns local Reddit cache counts plus TTL/content-hash/policy metadata only. It does not call Reddit, read memory, or return raw post/comment bodies.

`python smart_agent.py reddit retention sweep` runs through ToolBroker as `reddit.retention_sweep` and deletes expired cached Reddit entries according to `REDDIT_CACHE_TTL_SECONDS` and the entry `expires_at` timestamp. Sweep operations are audited and return counts and cache metadata only.

`python smart_agent.py reddit cache clear` runs through ToolBroker as `reddit.cache_clear` and removes local Reddit cache entries. It reports counts and path metadata, not raw post/comment bodies.

`python smart_agent.py reddit retention status` runs through ToolBroker as `reddit.retention_status` and reports whether the configured TTL/cache policy can be guaranteed. If TTL policy cannot be guaranteed, cache writes are treated as disabled rather than storing content silently.

`python smart_agent.py reddit privacy-report` runs through ToolBroker as `reddit.privacy_report` and returns a counts-only privacy report: entry totals, active/expired counts, content-hash coverage, author-metadata counts, removed-content counts, query-history counts, and policy flags. It never returns raw Reddit content, author names, or search query text.

## Read-Only Connector Behavior

- Search, post, subreddit, comment, and thread results are eligible for TTL cache only when `REDDIT_CACHE_ENABLED=true`.
- Cache entries track `cache_key`, `source`, `retrieved_at`, `expires_at`, `content_hash`, and sanitized payload metadata.
- Author display fields are stripped by default when `REDDIT_STORE_AUTHOR_METADATA=false`.
- Payloads containing deleted or removed content are not cached.
- Raw query-like fields are redacted before cache write if they appear in a payload; query-derived cache keys use hashes.
- `REDDIT_CACHE_TTL_SECONDS<=0` disables cache writes because retention cannot be guaranteed.
- Query strings are hashed for cache keys and are not stored as readable history.
- Cached content remains `UNTRUSTED_WEB` and cannot instruct the agent to call tools, alter policy, approve actions, or store memory.
- `reddit thread-export` is explicit-only, writes under `workspace/reddit_threads/`, labels the file `UNTRUSTED_DOCUMENT`, and does not write memory.
- Reddit summarization commands do not persist summaries to memory. They may reuse the configured TTL-bounded underlying search/thread cache, but deleted/removed content and prompt-injection-like comments are not summarized as evidence.
