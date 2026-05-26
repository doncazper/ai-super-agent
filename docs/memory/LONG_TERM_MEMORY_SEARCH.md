# Long-Term Memory Search

Long-term memory search is a local, policy-gated SQLite search surface for approved memory records. It is not a broad personal-data archive and it does not use cloud embeddings by default.

## Commands

```bash
python smart_agent.py memory search "query"
python smart_agent.py memory search "query" --scope default --category project_fact --limit 10
python smart_agent.py memory context-preview "query"
```

## Safety Rules

- Memory search runs through `ToolBroker` as `memory.search`.
- Results are scoped and category-filtered.
- Secrets are refused before storage through the brokered memory tools.
- Personal categories and personal trust levels require approval before storage.
- Search does not write memory, create embeddings, or store query history.
- Deleting a record removes it from later search results.

## Current Limits

- Search is simple local SQLite `LIKE` matching, not semantic embedding search.
- Deletion cannot rewrite existing audit logs or filesystem backups.
- Live UX/manual QA is still pending beyond local CLI smoke tests.
