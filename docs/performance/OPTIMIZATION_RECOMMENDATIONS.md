# Optimization Recommendations

`PERF-07` adds an advisory recommendation engine for redacted local performance reports.

## Command

```bash
python smart_agent.py perf suggest-fixes
```

The command reads the latest redacted performance report, maps findings or pytest duration evidence into prioritized optimization recommendations, and writes a redacted recommendation report under `reports/performance/`.

## Recommendation Fields

Each recommendation includes:

- expected impact
- effort
- risk
- patch area
- required tests
- required docs
- rollback plan
- `safe_for_self_heal`
- `human_review_required`
- status

No patch is applied by this command.

## Categories

The v1 rule set covers:

- lazy imports
- add timeout
- bound file scan
- cache parsed config
- cache command registry
- avoid repeated glob
- avoid full tracker read in hot path
- use streaming/chunking
- TTL cache
- compile regex once
- narrow test target
- add fixture
- defer live provider check
- docs/UX only
- needs architecture review

## Safety

Recommendations must not weaken ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, secret redaction, personal-data defaults, test coverage, or release gates. Broad rewrites, safety-policy changes, and HIGH/CRITICAL optimizations require separate explicit approval and a future scoped prompt.
