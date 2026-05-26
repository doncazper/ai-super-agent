# Decision: Performance Bottleneck Scanner

Date: 2026-05-26
Status: accepted for staged implementation

## Context

The agent has grown across many feature tracks, prompt packs, command registries, docs, tests, dogfood suites, and provider stubs. Release hardening now needs a safe way to identify slow startup paths, command overhead, repeated file scans, slow tests, and optimization opportunities without creating new safety risks.

## Decision

Create a Performance Bottleneck Scanner as a local-first, report-driven subsystem. It will use static analysis, bounded safe subprocess timings, command-registry metadata, pytest duration parsing, baselines, recommendations, patch plans, and read-only dashboards.

Runtime commands must remain ToolBroker-routed when implemented. PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger remain non-bypassable. Performance work must never weaken safety systems.

## Consequences

- The project gets a shared evidence format for performance findings and regressions.
- Optimization work can be prioritized without broad speculative rewrites.
- Future self-heal/QA integrations can consume patch plans without applying them automatically.
- Timing results remain advisory because local machine load can vary.

## Rejected Alternatives

- Use heavyweight external profilers by default: rejected because package installation and runtime setup are out of scope.
- Run live provider benchmarks: rejected because live providers are opt-in and may be slow, paid, unavailable, or privacy-sensitive.
- Automatically apply optimization patches: rejected because performance changes can alter behavior and must be reviewed.
