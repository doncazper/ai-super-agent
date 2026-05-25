# SDLC

The project follows a safety-first lifecycle.

1. Specification: define mission, non-goals, architecture, trust boundaries, and acceptance criteria.
2. Requirements: define functional and safety requirements before implementation.
3. Design: describe interfaces, data flow, policies, and audit behavior.
4. Threat model: identify abuse paths, unsafe defaults, and mitigations.
5. Implementation: add the smallest milestone-scoped code needed.
6. Tests: add unit/integration/security tests matching the risk.
7. Security review: confirm policy, permission, approval, and audit behavior.
8. Release gate: check docs, tests, forbidden capabilities, and approvals.
9. Documentation: update milestone docs and completion report.
10. Monitoring and iteration: inspect audit output, failures, and user feedback.

## Release Gate Addendum

Every release gate must run startup capability validation against `config/capabilities.yaml`.

The capability manifest must use the normalized schema for every capability:

- `capability_name`
- `tool_name`
- `connector_name`
- `risk_level`
- `trust_level`
- `default_enabled`
- `approval_required`
- `approval_reuse_allowed`
- `rate_limit`
- `memory_behavior`
- `audit_fields`
- `setup_hint`
- `docs_reference`

The gate must fail if a capability is missing required fields, contains bypass flags, enables personal-data capabilities by default, or defines a CRITICAL capability without per-action approval and no approval reuse.

## Mini-SDLC for Every Milestone

1. Confirm scope.
2. Confirm non-goals.
3. Define requirements.
4. Define risks and threat-model notes.
5. Implement.
6. Add tests.
7. Run tests.
8. Update docs.
9. Update completion report.
10. Stop at approval gates.

## Build Provenance And Cloneability

Major feature tracks should preserve their original prompt packs under `prompts/packs/`. If original prompts are unavailable, reconstructed packs must be labeled reconstructed, include confidence and caveats, and must not be claimed exact without evidence.

Every rewrite, model migration, or platform port must start from `docs/AGENT_DNA.md`, `docs/ARCHITECTURE_PRINCIPLES.md`, `docs/CLONE_BLUEPRINT.md`, `docs/MODEL_MIGRATION_GUIDE.md`, and `docs/PLATFORM_MIGRATION_GUIDE.md`.

Release gates for cloneability must verify prompt provenance, command registry state, feature maturity, project state, changelog, completion report, startup policy validation, capability manifest validation, and preservation of ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger invariants.
