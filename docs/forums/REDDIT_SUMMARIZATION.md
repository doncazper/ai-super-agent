# Reddit Summarization

Reddit summarization is read-only, source-grounded, and anecdotal by design. It uses the official Reddit Data API connector through `ToolBroker`, `PolicyEngine`, and `AuditLogger`; it does not scrape Reddit web pages or use a web fallback.

## Commands

```bash
python smart_agent.py reddit summarize-thread "<post_url_or_id>"
python smart_agent.py reddit summarize-thread "<post_url_or_id>" --max-comments 100 --sort top --collapse-depth 3
python smart_agent.py reddit summarize-search "query"
python smart_agent.py reddit consensus "query"
python smart_agent.py reddit pros-cons "query"
python smart_agent.py reddit complaints "product_or_topic"
python smart_agent.py reddit buying-advice "product_or_topic"
```

## Output Sections

Each successful summary returns:

- Short answer
- Consensus
- Major viewpoints
- Disagreements
- Repeated complaints/praise
- Caveats / bias warning
- Source list
- Fetch limitations

The source list contains Reddit source IDs, permalinks, provider, retrieval time, trust label, evidence state, and whether the source was used as evidence.

## Evidence Rules

- Thread summaries use fetched thread data and label it `fetched_thread`.
- Search summaries use Reddit search snippets only and label sources `snippet_only`.
- Deleted or removed posts/comments are not summarized as evidence.
- Prompt-injection-like comments are excluded from evidence and listed with an exclusion reason.
- Source references must come from Reddit API payloads; fabricated URLs or source IDs are not allowed.
- Reddit discussion is anecdotal and must not be described as statistically representative.

## Retention And Memory

Summaries are not written to memory by default. Underlying Reddit search/thread data may use the configured TTL cache, but query history, summaries, author metadata, deleted/removed content, and training data are not stored by default.

## Safety Boundary

Reddit content remains `UNTRUSTED_WEB`. Comments and posts cannot instruct the agent to call tools, reveal secrets, change policy, approve actions, bypass safety systems, or write memory.

Live Reddit validation remains opt-in and requires OAuth configuration plus `REDDIT_ENABLED=true`.
