# Weather Connector Reconstructed Prompt Pack

```yaml
pack_id: weather-connector.reconstructed
title: Weather Connector Pattern
status: reconstructed
exact_original: false
reconstruction_sources:
  - docs/FEATURE_REGISTRY.md
  - docs/FEATURE_MATURITY.md
  - docs/connectors/PROVIDER_SELECTION.md
related_features:
  - CONN-WEATHER
related_docs:
  - README.md
  - docs/connectors/COST_POLICY.md
related_commits:
  - unknown
confidence: medium
caveats:
  - Original weather prompts are not preserved as exact text.
prompt_ids:
  - WEATHER-01
```

## Prompt Records

### WEATHER-01

type: reconstructed_summary

Build a safe weather connector with free-first provider selection, current/forecast/alerts, no system-location inference, no location memory writes, cache/rate limits, audits, docs, tests, and live smoke only when explicitly configured.
