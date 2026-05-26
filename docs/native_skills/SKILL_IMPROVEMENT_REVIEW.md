# Native Skill Improvement Review

Status: HERMES-05 review policy.

## Purpose

Native skill improvement proposals are evidence packets, not patches. Reviewers can use them to decide whether a later skill edit is justified.

## Review Checklist

Before accepting any proposed improvement:

- Confirm every evidence source is redacted and non-personal.
- Confirm the proposal includes tests and a rollback plan.
- Confirm the lockfile impact is explicit.
- Confirm the proposed files are inside approved native skill, docs, or tests paths.
- Confirm the change does not add unreviewed dependencies, install hooks, external scripts, background persistence, personal-data access, or send/write behavior.
- Confirm ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger requirements remain intact.
- Confirm feature maturity is not raised without tests, docs, policy/audit evidence, and release-gate results.

## Approval Boundary

`skills improvements show` may provide evidence for a future work item, but it is not an approval. Applying an improvement requires a new prompt with explicit scope and tests.

High-risk proposals require human review even if they are generated from trusted metadata. CRITICAL or safety-control-changing proposals should remain blocked until a dedicated safety review is requested.

## Retention

Improvement proposal reports store redacted metadata only and should remain local review artifacts. Do not paste raw session logs, raw bug bodies with personal data, tokens, private repository content, or personal connector output into proposals.

