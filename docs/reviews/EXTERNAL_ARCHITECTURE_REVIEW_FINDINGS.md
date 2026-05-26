# External Architecture Review Findings

Status: EXTREV-01 local review complete.

This document converts the external architecture review themes into evidence-backed local findings. The review is a parity check only. It does not implement a web server, replace the CLI, run live providers, enable personal-data tools, add send/write behavior, or weaken ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

## Scope Confirmed

- Audit receipts and hash-chain evidence.
- Native skill vetting diagnostics.
- Source/provider explainability.
- HIGH/CRITICAL approval semantics.
- Backup restore policy-weakening checks.
- Self-improvement safety lints.
- Overclaim cleanup for planned, stubbed, and metadata-only capabilities.

## Non-Goals Confirmed

- No runtime architecture rewrite.
- No Fastify/TypeScript gateway.
- No background service or web server.
- No new live provider calls.
- No personal-data access.
- No send/write enablement.
- No command execution outside existing safe validations.

## Findings

| Area | Current evidence | Status | Gap / follow-up |
|---|---|---|---|
| Audit hash-chain verification | `agent/safety/audit.py` writes `hash_previous` and `hash_current`; `tests/test_tool_broker.py` verifies chained execution and denial events. | Partially covered | Add a future `audit verify-chain` CLI that verifies all local audit JSONL records without exposing raw args. |
| Audit receipt export | `ToolBroker._debug_from_audit()` exposes `audit_request_id` and `audit_hash`; runtime kernel docs mention audit receipt references. | Partially covered | Add a future redacted `audit export-receipt <audit_id>` command that exports request/tool/capability/policy/approval/hash metadata only. |
| Tool/action tied to audit receipt | ToolBroker result debug metadata includes current audit hash for executed tool calls. Action Center and approval tests cover lifecycle audit events. | Covered for local tool paths | Keep future gateway/frontends carrying audit correlation IDs through ToolBroker. |
| Native skill manifest validation | `agent/native_skills/manifest.py`, validator tests, and `skills validate` style diagnostics exist. | Covered for metadata-only v1 | Do not treat manifest validity as permission to install, execute, or enable external skills. |
| Native skill trust/provenance/lockfile/conflict/test harness | Native skill provenance, trust, lockfile, profile, compatibility, conflict, test harness, dogfood, docs generator, and release-gate docs/tests exist. | Covered for metadata-only v1 | Reviewed real `native_skills.lock` write/pinning workflow and manual external-skill QA remain future work. |
| Source/provider explainability | Web provider policy, source-grounded research, source bundles, `web provider-decision`, `research sources/export-sources/verify-sources --last`, brain routing, media dry-run plans, and news provider policy expose selected/skipped providers and storage behavior. | Covered locally | Continue requiring selected/skipped provider reason, no-store/no-memory flags, and setup hints in future provider modules. |
| HIGH/CRITICAL approval semantics | Action Center, ApprovalManager, ToolBroker, and approved write/send tests cover exact previews, edit invalidation, consume-once approval, CRITICAL no-reuse, and brokered execution. | Covered locally | Keep every future action execution re-entering ToolBroker after Action Center approval. |
| Backup restore policy weakening | `backup.restore_check`, `backup.policy_check`, and `backup.restore` validate manifest hashes, path traversal, unredacted secrets, CRITICAL approval reuse, and capability policy weakening. | Covered locally | Live restore smoke remains disposable-workspace-only and opt-in. |
| Self-improvement safety lints | `improve lint-diff`, `improve artifact-hashes`, and `improve verify-artifacts` are read-only and block safe-only plans on policy/audit/ToolBroker/approval/personal-data/persistence/package/live-provider/server/secret/backup-restore weakening patterns. | Covered locally | Lints are heuristic and do not replace human review or release gates. |
| Overclaim cleanup | `docs/FEATURE_MATURITY.md` marks canonical runtime and related hardening as local Tested/Hardened where evidence supports it, with live/manual validation gaps called out. | No clear correction made in EXTREV-01 | Keep planned/stubbed/provider tracks below User-Ready until live validation and release gates support promotion. |

## Review Notes

- The audit system already has tamper-evident hash chaining, but user-facing audit receipt inspection is still planned, not implemented.
- Native skills are strong for review/vetting metadata. They are not a green light to install or execute external skill scripts.
- Provider explainability is a reusable pattern across web, research, weather, brain routing, media planning, and news policy, but live provider validation remains opt-in.
- Approval semantics are strongest around Action Center and approved write/send tests; future gateway or app surfaces must not create parallel approval paths.
- Backup restore hardening is local-tested, but real restore validation should happen only in a disposable repo copy.
