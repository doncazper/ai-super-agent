# Backup Roundtrip Validation

Status: Implemented with dry-run planning and restore-check validation.

Backup roundtrip validation verifies that a redacted backup can be created, integrity-checked, policy-checked, and restored only inside a disposable workspace copy. The default command is dry-run only:

```bash
python smart_agent.py backup roundtrip --dry-run
```

The dry-run lane does not create an archive and does not restore files. It reports the intended sequence:

1. Create a redacted local backup through `backup.create`.
2. Verify manifest integrity and stored file hashes through `backup.verify`.
3. Run restore readiness checks through `backup.restore-check <backup_id>`.
4. Run `backup.restore <backup_id>` only in a disposable project copy with explicit approval.

Related commands:

```bash
python smart_agent.py backup policy-check
python smart_agent.py backup restore-check <backup_id>
python smart_agent.py backup verify <backup_id>
```

## Restore-Check Behavior

`backup restore-check` is read-only. It verifies:

- manifest integrity hash
- stored file hashes
- redacted backup marker
- path traversal refusal
- unredacted secret material refusal
- capability manifest policy validation
- CRITICAL approval reuse refusal
- personal-data capability default-enable refusal
- policy/audit bypass marker refusal

`backup restore-check` does not write restored files and does not replace the approval-gated `backup restore` command.

## Live Smoke Guidance

Live restore smoke tests must use a disposable copy of the project. Do not run restore against the working repo unless the user explicitly approves that specific restore action.
