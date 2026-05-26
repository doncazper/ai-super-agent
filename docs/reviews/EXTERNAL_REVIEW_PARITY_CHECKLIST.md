# External Review Parity Checklist

Status: EXTREV-01 checklist complete for current local evidence.

| Check | Result | Evidence | Remaining work |
|---|---|---|---|
| Audit log has tamper-evident hash chaining | Pass | `agent/safety/audit.py`; `tests/test_tool_broker.py` | Add first-class chain verifier command later. |
| Audit receipt export exists | Partial | ToolBroker debug metadata includes `audit_request_id` and `audit_hash` | Planned `audit export-receipt <audit_id>` command added to registry only. |
| Tool execution is tied to audit metadata | Pass | `agent/core/tool_broker.py`; ToolBroker tests | Keep gateway/app bridge correlation IDs in future runtime work. |
| Native skill manifest validation exists | Pass | `tests/native_skills/test_skill_manifest_schema.py`; native skill docs | No external skill execution until separately approved. |
| Native skill provenance/trust/lockfile diagnostics exist | Pass | `tests/native_skills/test_skill_provenance_lockfile.py`; `docs/native_skills/` | Real lockfile write/pinning workflow remains future. |
| Native skill conflict detector exists | Pass | `tests/native_skills/test_skill_conflict_detector.py` | Conflict reports remain advisory and do not auto-resolve. |
| Native skill test/dogfood harness exists | Pass | `tests/native_skills/test_skill_test_harness.py`; dogfood suites | Harness remains metadata/fixture-safe by default. |
| Source/provider explainability exists | Pass | `web provider-decision`; `research sources/export-sources/verify-sources --last`; provider policy docs/tests | Add cross-provider explainability matrix in future. |
| No-store/no-memory behavior is visible | Pass | Command registry memory behavior, provider policy docs, research/news/forum/media docs | Keep this mandatory for future providers. |
| Exact preview matching exists for critical actions | Pass | Action preview and approved write/send tests | Add CANON-10 release-gate checklist item. |
| Editing invalidates prior approval | Pass | `tests/test_action_center.py`; email send tests | Keep direct tool calls blocked without matching Action Center action IDs. |
| Approvals are consume-once | Pass | Action Center tests and approved write/send tests | Keep CRITICAL no-reuse invariant in manifest validation. |
| CRITICAL approval reuse is denied | Pass | `tests/test_approved_write_actions.py`; capability manifest validation | Keep future CRITICAL actions per-action/no-reuse. |
| Execution re-enters ToolBroker after approval | Pass | Calendar/contact/email/message approved-action tests | No frontend or gateway direct execution path. |
| Restore rejects policy weakening | Pass | `tests/test_backup_restore.py`; `tests/test_backup_roundtrip_policy.py` | Manual restore drill still pending. |
| Restore verifies hashes and pre-restore copies | Pass | Backup tests and docs | Disposable-workspace live/manual validation only. |
| Self-improvement lints flag safety weakening | Pass | `tests/test_self_improvement_safety_lints.py` | Lints remain heuristic review aids. |
| Planned/stubbed capabilities are not overclaimed | Pass with caution | `docs/FEATURE_MATURITY.md`; productization audit docs | Continue conservative maturity in CANON-10. |

## Current Parity Summary

The repo is locally strong on safety-control evidence, metadata-only diagnostics, and conservative maturity language. The biggest parity gap is not the underlying audit hash chain; it is the lack of user-facing audit receipt commands. EXTREV-01 tracks those commands as planned and defers implementation to a scoped future prompt.

## Stop Conditions For Future Work

Stop and ask before proceeding if a future parity task requires:

- live provider access
- personal-data access
- unredacted audit export
- package installation
- a web server or background service
- changing audit storage format
- weakening policy, approval, redaction, or ToolBroker rules
- committing or pushing
