# Performance Optimization Policy

Optimizations must be scoped, measurable, reversible, and safety-preserving.

## Allowed Optimization Classes

- Lazy imports for optional/heavy modules.
- Add missing timeouts.
- Bound file scans.
- Cache parsed config or registry data when safe.
- Avoid repeated glob/rglob/walk operations.
- Use streaming or chunking for large local files.
- Add TTL caches for provider metadata where policy allows.
- Compile regexes once outside hot loops.
- Narrow test targets for focused developer loops.
- Add fixtures to avoid repeated expensive setup.
- Defer live provider checks in status/doctor commands.
- Docs/UX improvements that clarify slow-path behavior.

## Human Review Required

- Broad refactors.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger changes.
- Changes that affect approval, audit, secret redaction, memory, personal data, send/write behavior, provider calls, or startup policy.
- Package installation or runtime/provider installation.
- Any optimization that changes semantics.

## Forbidden in This Track

- Disabling tests to make performance look better.
- Removing safety checks for speed.
- Caching personal data by default.
- Skipping audit logging.
- Bypassing approvals.
- Enabling live providers, paid APIs, model downloads, or background services.
