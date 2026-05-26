# Native Skill Proposal Process

Native skill proposals are a planning artifact. They are useful for finding repeated workflows, but they are not permission to install, import, enable, or run a skill.

## Proposal Lifecycle

1. Generate a proposal from redacted metadata.
2. Review risk, privacy, source evidence, suggested tests, and suggested docs.
3. If still useful, open a separate implementation prompt.
4. Build the skill as reviewed native code only.
5. Run static inspection, manifest validation, dependency gating, conflict checks, tests, docs validation, and release gates.
6. Update feature maturity conservatively.

## Required Manifest Metadata

Every suggested manifest must include:

- `risk_level`
- `trust_level`
- `default_enabled: false`
- `approval_required`
- `memory_behavior`
- `audit_fields`
- `status: candidate_unreviewed` or `needs_review`
- docs reference

Proposal-generated manifests are never loaded as live native skill manifests.

## Review Rules

- Personal-data patterns are skipped by default.
- HIGH and CRITICAL candidates require human review and later approval-gated implementation.
- Send/write, background persistence, package installation, external scripts, arbitrary browser automation, and plugin runtime execution remain forbidden unless a future explicit approval gate changes that boundary.
- Skill vetting must happen before any future import or enablement.
- ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger remain mandatory for future executable behavior.

## Storage

Proposal reports store redacted metadata only. They must not store raw session content, raw command histories, secrets, personal connector content, provider responses, or untrusted skill bodies.

