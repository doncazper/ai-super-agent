# Capability Manifest Reconciliation

Last reconciled: 2026-05-25

## Validation Result

- `make policy-check`: passed.
- Startup policy validation: passed.
- Capability manifest validation: passed.
- Quick manifest scan: 234 capabilities, 18 news capabilities, 5 platform-prefixed capabilities, and no default-enabled CRITICAL capabilities.

## Findings

- `config/capabilities.yaml` remains the runtime source of truth for capability risk, approval, and default-enable behavior.
- Personal-data tools remain disabled by default per `./scripts/agent doctor`.
- CRITICAL actions remain disabled by default and require strict per-action approval by policy.
- News capabilities are declared as disabled/planned/provider-policy bounded; no live news provider behavior was enabled in this pass.
- Platform bridge capabilities remain disabled/stubbed/planned; no native platform action was enabled.
- Natural-language command understanding remains advisory and cannot bypass ToolBroker or PolicyEngine.
- QA runner behavior remains safe-tier bounded and cannot run HIGH/CRITICAL by default.

## Deferred Checks

- A future release gate should map every implemented tool callable to an explicit manifest entry and flag any stale planned capability with no docs.
- Existing static scans include many expected policy/test references to forbidden bypasses; those are not evidence of runtime bypass behavior by themselves.
