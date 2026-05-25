# Reddit Thread Fetch

Reddit thread fetch normalizes a public Reddit post and its comments through the official Reddit Data API only. It is read-only, OAuth-gated, ToolBroker-routed, PolicyEngine-evaluated, and AuditLogger-recorded.

## Commands

```bash
python smart_agent.py reddit thread "<post_url_or_id>"
python smart_agent.py reddit thread "<post_url_or_id>" --max-comments 100
python smart_agent.py reddit thread "<post_url_or_id>" --sort top|new|controversial
python smart_agent.py reddit thread "<post_url_or_id>" --collapse-depth 3
python smart_agent.py reddit thread-export "<post_url_or_id>" --format json|markdown
```

`reddit thread` executes as `reddit.fetch_thread`. `reddit thread-export` executes as `reddit.thread_export` and writes only under the approved workspace `workspace/reddit_threads/`.

## Normalized Thread Shape

Thread results include:

- `post`
- `comments` for backward-compatible flattened comments
- `comment_tree`
- `flattened_comments`
- `source_references`
- `retrieved_at`
- `fetch_warnings`
- `truncation_info`
- `trust_level=UNTRUSTED_WEB`

`source_references` preserve stable `source_id` values and Reddit permalinks for the post and included comments. Deleted or removed comments are represented as removed records with empty body text and are not evidence for summaries.

## Limits And Sorting

`--max-comments` is bounded by policy and defaults to 100. `--collapse-depth` defaults to 3 so deeply nested replies are represented with collapse metadata instead of expanding indefinitely. Supported thread sorts are `top`, `new`, and `controversial`.

## Export Policy

Exports are explicit-only and produce `UNTRUSTED_DOCUMENT` files. Export does not grant trust to Reddit content, does not write memory, and does not write outside the approved workspace. Exported files include the original `UNTRUSTED_WEB` source references plus an `UNTRUSTED_DOCUMENT` export label.

## Safety Rules

- No Reddit web scraping fallback.
- No unauthenticated Reddit traffic.
- No posting, commenting, voting, DMs, moderation, or write actions.
- No CAPTCHA, login wall, anti-bot, or API-limit bypass.
- Author metadata is redacted by default.
- Query/thread history is not stored in memory by default.
- TTL cache use remains bounded by Reddit retention settings.
- Reddit content cannot instruct the agent to call tools, reveal secrets, alter policy, disable audit logging, or store memory.
