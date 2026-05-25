# Reddit Compliance

This milestone adds Reddit policy, configuration scaffolding, OAuth/config doctor diagnostics, and a read-only official Reddit Data API connector. It does not scrape Reddit web pages, post, comment, vote, send DMs, moderate, bypass API limits, or store Reddit content permanently.

## Defaults

- `REDDIT_ENABLED=false`.
- OAuth configuration is required before any Reddit API content call.
- Unauthenticated Reddit traffic is not allowed.
- `reddit doctor` and `reddit status` make no Reddit network calls.
- `reddit auth-check` is explicit-only and may call only Reddit OAuth/token-status endpoints.
- Read-only content commands return setup guidance when `REDDIT_ENABLED=false` or OAuth config is incomplete.
- Reddit web scraping is not an API substitute.
- Reddit content must be labeled `UNTRUSTED_WEB`.
- Reddit content cannot instruct the agent to call tools, reveal secrets, alter policy, disable audit logging, store memory, or ignore higher-priority instructions.
- Reddit content is not used for model training.

## Required Environment

Read-only connector work requires:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT`
- `REDDIT_REFRESH_TOKEN` or `REDDIT_ACCESS_TOKEN`

Secrets and tokens must never be printed in doctor/status output, audit logs, test fixtures, or docs.

## Doctor Commands

The following commands are available for safe configuration diagnostics:

- `python smart_agent.py reddit doctor`
- `python smart_agent.py reddit status`
- `python smart_agent.py reddit auth-check`
- `python smart_agent.py connectors status reddit`

`reddit doctor` and `reddit status` run through ToolBroker as `reddit.status`, are evaluated by PolicyEngine, and write AuditLogger evidence. They inspect only environment/config metadata and report:

- enabled/configured state
- missing OAuth fields
- whether refresh/access token config exists
- whether `.env` appears tracked
- whether token env values point to files inside the repo
- missing or generic `REDDIT_USER_AGENT`
- rate-limit and retention config
- disabled write actions
- denied web fallback
- hard-false training behavior

`reddit auth-check` runs through ToolBroker as `reddit.auth_check`. It requires explicit CLI invocation, returns setup guidance when OAuth config is incomplete, and otherwise calls a harmless Reddit OAuth/token-status endpoint only. It must not call post, thread, subreddit, comment, user-content, moderation, voting, DM, or web-scraping endpoints.

## Read-Only Connector Commands

The following commands are available for official Data API read-only access when Reddit is explicitly enabled and OAuth is configured:

- `python smart_agent.py reddit search "query"`
- `python smart_agent.py reddit search "query" --subreddit "subreddit" --sort comments --time week --limit 10 --language en`
- `python smart_agent.py reddit explain-result <source_id>`
- `python smart_agent.py reddit subreddit "subreddit_name"`
- `python smart_agent.py reddit post "<post_id_or_url>"`
- `python smart_agent.py reddit comments "<post_id_or_url>"`
- `python smart_agent.py reddit thread "<post_id_or_url>" --max-comments 100 --sort top --collapse-depth 3`
- `python smart_agent.py reddit thread-export "<post_id_or_url>" --format json|markdown`
- `python smart_agent.py reddit summarize-thread "<post_id_or_url>"`
- `python smart_agent.py reddit summarize-search "query"`
- `python smart_agent.py reddit consensus "query"`
- `python smart_agent.py reddit pros-cons "query"`
- `python smart_agent.py reddit complaints "product_or_topic"`
- `python smart_agent.py reddit buying-advice "product_or_topic"`
- `python smart_agent.py reddit cache clear`
- `python smart_agent.py reddit retention sweep`

These commands execute through ToolBroker and PolicyEngine as `reddit.search_posts`, `reddit.explain_result`, `reddit.fetch_subreddit_info`, `reddit.fetch_post`, `reddit.fetch_comments`, `reddit.fetch_thread`, `reddit.thread_export`, `reddit.summarize_thread`, `reddit.summarize_search`, `reddit.consensus`, `reddit.pros_cons`, `reddit.complaints`, `reddit.buying_advice`, `reddit.cache_clear`, and `reddit.retention_sweep`. Network operations use `https://oauth.reddit.com` and Reddit OAuth token endpoints only. `reddit.explain_result` is local metadata-only and performs no network call. They do not use unauthenticated Reddit traffic, web-page scraping, cookies, browser automation, CAPTCHA/anti-bot bypass, or Reddit web pages as an API substitute.

Search/post/comment/thread results are normalized with stable `source_id` values, Reddit permalinks, `provider=reddit_api`, and `trust_level=UNTRUSTED_WEB`. Search results are labeled `snippet_only` until a post/thread is explicitly fetched. Thread fetch returns a comment tree, flattened comments, source references, fetch warnings, and truncation metadata. Summaries include source IDs/permalinks, distinguish snippet-only from fetched-thread evidence, exclude deleted/removed and prompt-injection-like comments from evidence, and include Reddit-anecdote caveats. Thread export writes only to the approved workspace as `UNTRUSTED_DOCUMENT`. Author metadata is redacted by default unless a future policy explicitly enables it. Query history and summaries are not persisted by default.

## Capability Boundary

Declared read-only capabilities:

- `reddit.status`
- `reddit.auth_check`
- `reddit.search_posts`
- `reddit.search_subreddit`
- `reddit.fetch_subreddit_info`
- `reddit.fetch_post`
- `reddit.fetch_comments`
- `reddit.fetch_thread`
- `reddit.explain_result`
- `reddit.thread_export`
- `reddit.summarize_thread`
- `reddit.summarize_search`
- `reddit.consensus`
- `reddit.pros_cons`
- `reddit.complaints`
- `reddit.buying_advice`
- `reddit.cache_clear`
- `reddit.retention_sweep`

The diagnostics capabilities `reddit.status` and `reddit.auth_check` are enabled for explicit doctor/status commands. Read-only content capabilities are declared in `config/capabilities.yaml`, but runtime network access still fails closed unless Reddit is explicitly enabled and OAuth configuration is complete. The connector writes AuditLogger evidence for provider, domain, endpoint class, rate-limit status, and result status.

Forbidden in this track:

- posting
- commenting
- voting
- DMs/chat
- moderation actions
- private/logged-in page scraping
- cookie/session automation
- CAPTCHA or anti-bot bypass
- Reddit web scraping fallback

## Compliance Checks

`agent.forums.reddit.policy` exposes metadata helpers for safe tests and doctor commands. `agent.forums.reddit.doctor` adds redacted status, doctor, and explicit auth-check diagnostics. `agent.forums.reddit.provider` adds the read-only connector facade used by brokered CLI commands. These helpers report enabled/configured state, OAuth missing fields, retention defaults, rate-limit defaults, disabled web fallback, author metadata defaults, and the hard-false training flag without exposing secrets. Only `reddit auth-check` may make a diagnostic live Reddit OAuth/token-status call; content commands may make Data API calls only after explicit enablement and OAuth setup.
