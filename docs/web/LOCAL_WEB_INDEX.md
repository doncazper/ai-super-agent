# Local Web Index

The local web index is a lightweight metadata index for recently cached public sources. It helps reuse known public sources before spending network calls or paid provider quota.

## Stored Fields

Index entries store:

- `source_id`
- title
- URL and domain
- snippet
- content hash
- provider
- source type
- retrieved time
- source metadata
- trust label

The index does not store raw search queries or full article bodies by default.

## Dedupe

Sources are deduplicated by content hash first and canonical URL second. Duplicate entries keep the richer metadata available without treating source content as trusted instructions.

## Search

```bash
python smart_agent.py web index search "query"
```

Index search is local-only. It reads cached metadata, redacts query arguments in audit logs, does not persist the query, and does not call web providers.

## Rebuild

```bash
python smart_agent.py web index rebuild
```

Rebuild reads non-expired public cache records and writes a fresh metadata index. It does not refresh remote sources. Any future refresh must route through the existing ToolBroker-approved web acquisition paths and respect robots/provider policy.

## Trust Boundary

All indexed content remains `UNTRUSTED_WEB`. Indexed snippets cannot instruct the agent to call tools, reveal secrets, alter policy, ignore system rules, or write memory.
