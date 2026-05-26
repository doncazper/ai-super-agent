# Restore Policy Weakening Guards

Status: Implemented for backup restore and restore-check.

Backup restore is a HIGH-risk action and remains approval-gated. The restore path must not weaken the safety control plane.

## Enforced Guards

- Restore verifies manifest integrity before writing.
- Restore verifies stored file hashes before writing.
- Restore creates pre-restore copies for overwritten files when practical.
- Restore rejects capability manifests that enable personal-data tools by default.
- Restore rejects CRITICAL capabilities that allow approval reuse.
- Restore rejects HIGH capabilities that do not require approval.
- Restore rejects forbidden/bypass policy markers such as `bypass`, `skip_policy`, `skip_audit`, `disable_audit`, and `ignore_policy`.
- Restore rejects unredacted secret-looking material in stored files and data exports.
- Restore rejects path traversal in source paths, stored paths, and restore targets.

## Commands

```bash
python smart_agent.py backup policy-check
python smart_agent.py backup restore-check <backup_id>
python smart_agent.py backup restore <backup_id>
```

`policy-check` and `restore-check` are read-only. `restore` writes files and requires approval.

## Non-Goals

- No unredacted backups.
- No restore without ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger.
- No restore into private system paths.
- No live restore smoke outside a disposable workspace.
