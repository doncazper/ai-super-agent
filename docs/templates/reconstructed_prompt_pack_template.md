# Reconstructed Prompt Pack Template

```yaml
pack_id: example.reconstructed
title: Example Reconstructed Track
status: reconstructed
exact_original: false
reconstruction_sources:
  - docs/FEATURE_REGISTRY.md
related_features:
  - EXAMPLE-FEATURE
related_docs:
  - docs/example.md
related_commits:
  - unknown
confidence: low
caveats:
  - Original prompt text is unavailable.
prompt_ids:
  - EXAMPLE-01
```

## Prompt Records

Each reconstructed prompt should be labeled one of:

- `exact_prompt`: exact text is preserved and cited.
- `reconstructed_summary`: best-effort reconstruction from evidence.
- `unknown`: insufficient evidence.

Do not mark a reconstructed prompt complete, active, or executed unless the prompt ledger and repo evidence prove it.
