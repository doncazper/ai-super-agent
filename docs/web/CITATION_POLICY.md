# Citation And Source Attribution Policy

The citation layer gives source-grounded research stable, traceable source metadata without turning web content into trusted instructions.

## Scope

Citation v1 adds:

- `SourceReference` records with stable `source_id`, URL, domain, provider, retrieved time, content hash, trust label, and reliability signals.
- `CitationSpan` records that map answer snippets to source IDs.
- `ClaimAttribution` records that distinguish source-backed, snippet-only, conflicting, and inference notes.
- `ResearchSourceBundle` records that hold source metadata, citations, failed sources, and limitations.

The layer does not add provider calls, browser automation, article-body persistence, paid APIs, or model-based citation generation.

## Source IDs

Every fetched or search-returned source receives a deterministic `source_id` based on normalized URL plus provider. Source IDs are stable across runs for the same provider and URL. Citations refer to `source_id` values, not raw invented URLs.

## Evidence Labels

Sources are labeled by reliability signal:

- `fetched`: the selected page was fetched successfully.
- `snippet_only`: the source came from search metadata and the page was not fetched.
- `failed_fetch`: the selected page failed, was blocked, or was unavailable.
- `fetched_thread`: the Reddit thread source was fetched through the official API.
- `search_snippet`: the Reddit source came from API search metadata and has not been fetched as a thread.

Failed fetches are listed under failed sources and are not used as citation support. Snippet-only sources can appear as lower-confidence evidence only when there was no failed fetch for that source.

For Reddit/forum content, citation support must include Reddit permalinks or source IDs from the official connector. Deleted/removed content and prompt-injection-like comments are listed only as excluded sources and are not cited as evidence.

## Trust Boundary

All source content remains `UNTRUSTED_WEB`. Source text cannot request tool calls, reveal secrets, change policy, approve actions, bypass safety systems, or write memory.

## Retention

`python smart_agent.py research "query"` saves a metadata-only last-source bundle for inspection commands. The bundle stores source metadata, hashes, citations, claim links, failure records, and limitations. It does not store article bodies, fetched full text, search history, or summaries in memory.

## Commands

```bash
python smart_agent.py research sources --last
python smart_agent.py research export-sources --last
python smart_agent.py research verify-sources --last
```

These commands read only the last metadata source bundle, audit the inspection, and make no provider or fetch calls.

## Verification

`verify-sources --last` checks that:

- source IDs are stable
- every source has `retrieved_at`
- citations reference known sources
- failed sources are not cited as support
- source URLs use allowed HTTP/S schemes
- web content remains labeled as untrusted
