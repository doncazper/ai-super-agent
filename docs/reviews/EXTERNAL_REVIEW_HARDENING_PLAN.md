# External Review Hardening Plan

Status: EXTREV-01 plan created.

This plan tracks small follow-ups from the external architecture review. Items are intentionally scoped so they do not rebuild the runtime or create new execution surfaces.

## Priority Follow-Ups

| Priority | Follow-up | Scope | Risk | Expected files | Tests required | Approval gate |
|---|---|---|---|---|---|---|
| P1 | Audit chain verifier | Add a read-only `audit verify-chain` command that validates `hash_previous` / `hash_current` continuity in local audit JSONL files. | SAFE | `agent/safety/audit_receipts.py`, CLI/command registry docs, tests | Unit tests for valid chain, broken chain, malformed JSONL, redaction, and no raw arg export | None if read-only |
| P1 | Audit receipt exporter | Add a redacted `audit export-receipt <audit_id>` command that returns request id, tool, capability, risk, policy decision, approval result, audit hash, previous hash, and redacted summary. | LOW | `agent/safety/audit_receipts.py`, CLI/command registry docs, tests | Unit tests for known/unknown receipt, redaction, no raw secrets, no personal data, no memory write | None if read-only |
| P2 | Gateway audit correlation check | Extend CANON-10 release gate to assert gateway/frontends carry audit correlation fields in preview/result contracts. | SAFE | Release-gate docs/tests | Gateway/kernel boundary tests | None |
| P2 | Native skill lockfile update design | Specify an approval-gated lockfile write workflow before any external skill pinning command exists. | MEDIUM | Native skill docs, roadmap, tests if commands planned | Docs tests and command registry validation | Required before any write command |
| P2 | Provider explainability regression matrix | Add a cross-provider docs/test matrix requiring selected provider, skipped providers, setup hints, cost mode, no-store/no-memory flags, and audit fields. | SAFE | Docs/tests only | Docs test and provider-policy tests | None |
| P2 | Approval semantics release-gate checklist | Add CANON-10 checks for exact preview matching, edit invalidation, consume-once approval, CRITICAL no-reuse, and ToolBroker re-entry. | SAFE | Release-gate docs/tests | Action Center and approved write/send targeted tests | None |
| P3 | Manual restore drill | Run `backup create`, `backup inspect`, `backup verify`, `backup restore-check`, and one approved restore in a disposable repo copy. | HIGH | Manual QA report only | Manual QA evidence and backup tests | Explicit user approval in disposable workspace |

## Planned Command Rows Added

The external review found a real UX gap around audit receipts. EXTREV-01 added planned command registry rows only:

- `python smart_agent.py audit verify-chain`
- `python smart_agent.py audit export-receipt <audit_id>`

These commands are not implemented yet. They are tracked as `planned`, with no runtime dispatch and no hidden execution path.

## Acceptance Criteria For Future Audit Receipt Work

- Read-only by default.
- Does not execute tools or providers.
- Does not consume approvals.
- Does not write memory.
- Redacts args and result summaries.
- Does not print raw secrets, raw personal data, raw email/message bodies, or raw document contents.
- Verifies hash-chain continuity deterministically.
- Returns structured missing/malformed/tampered states.
- Uses local audit files only.
- Preserves append-only audit behavior.

## What Not To Do

- Do not rewrite `AuditLogger` storage format without a migration plan.
- Do not make audit receipt export a bypass for redaction.
- Do not treat an audit receipt as approval.
- Do not let frontends approve or execute actions based only on receipt metadata.
- Do not mark planned/stubbed capabilities user-ready because this review exists.
