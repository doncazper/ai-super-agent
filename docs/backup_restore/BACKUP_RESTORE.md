# Backup / Restore / Migration v1

Backup v1 creates local, redacted archive directories for project recovery and migration. It is designed to preserve project state without collecting live personal connector data or leaking secrets.

## Commands

```bash
python smart_agent.py backup create
python smart_agent.py backup create --include-captures --include-audit-metadata
python smart_agent.py backup list
python smart_agent.py backup inspect <backup_id>
python smart_agent.py backup verify <backup_id>
python smart_agent.py backup roundtrip --dry-run
python smart_agent.py backup policy-check
python smart_agent.py backup restore-check <backup_id>
python smart_agent.py backup export --redacted
python smart_agent.py backup restore <backup_id>
```

## Scope

Included by default:

- config files under `config/`, with secret-like values redacted
- `.env.example`, redacted
- governance and tracking docs
- feature registry, maturity, roadmap, prompt, command, risk, threat, release, and completion docs
- native skill manifests and native-skill docs
- redacted memory export, when `data/memory.sqlite3` exists
- redacted Action Center metadata, when `data/actions.json` exists

Optional:

- captures via `--include-captures`
- audit metadata via `--include-audit-metadata`

Excluded:

- `.env`
- private key/certificate files
- raw API keys, tokens, passwords, and authorization values
- calendar/contact/email/message/task provider data
- browser cookies, sessions, history, passwords, or private app databases

## Restore Safety

`backup.roundtrip --dry-run`, `backup.policy-check`, and `backup.restore-check` are read-only guard commands. `backup.restore` is HIGH risk and approval-gated. Restore verifies the manifest integrity hash and stored file hashes before applying changes. It rejects backed-up capability manifests that fail current startup validation, enable personal connectors by default, weaken HIGH approval requirements, allow CRITICAL approval reuse, include bypass-style flags, expose unredacted secret-looking material, or traverse paths. Restore creates pre-restore file copies under `.agent_restore_backups/<backup_id>` when replacing existing files.

V1 restores redacted memory/action/capture/audit exports as JSON artifacts. It does not silently reconstruct raw personal memory, provider data, or private app state.

## Storage

Default backup directory:

```text
workspace/backups
```

Override with:

```bash
export BACKUP_DIR="./workspace/backups"
python smart_agent.py backup create
```

or:

```bash
python smart_agent.py backup create --backup-dir ./workspace/backups
```

Configured backup paths are checked against denied private macOS paths. The default stays inside the approved workspace.
