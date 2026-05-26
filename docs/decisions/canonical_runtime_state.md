# Decision: Canonical Runtime State

Date: 2026-05-25
Status: Accepted for CANON-01 scaffolding

## Context

The repo now has many trackers, prompt packs, command registries, release gates, and validation reports. Drift is possible when a batch is interrupted or when summaries are updated at different times.

## Decision

Add a portable Python canonical runtime state model under `agent/runtime/canonical_state.py`. It provides JSON metadata and a fixed source-of-truth hierarchy for reconciliation.

The model is read-only. It does not replace the CLI, ToolBroker, PolicyEngine, ApprovalManager, AuditLogger, prompt trackers, or feature trackers.

## Consequences

- Runtime state can be inspected with `python smart_agent.py runtime canonical-state`.
- Source-of-truth ordering can be inspected with `python smart_agent.py runtime source-of-truth`.
- Tracker conflicts can be previewed without file changes with `python smart_agent.py runtime reconcile-preview`.
- Future prompts can build durable execution records on this model without rewriting runtime architecture.
