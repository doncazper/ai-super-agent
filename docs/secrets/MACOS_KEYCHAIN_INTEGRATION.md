# macOS Keychain Integration

Status: optional dry-run adapter, no real Keychain access in v1.

The secrets track prefers macOS Keychain or a password manager for local secret storage, but the Python agent does not require Keychain and does not read or write Keychain values by default.

## Current Behavior

- `python smart_agent.py secrets keychain status` reports platform/support metadata only.
- `python smart_agent.py secrets keychain get <secret_id> --dry-run` validates secret metadata and returns `value_returned=false`.
- `python smart_agent.py secrets keychain set <secret_id> --dry-run` validates secret metadata and returns `value_written=false`.
- Non-macOS platforms return unsupported/setup guidance.
- Real Keychain reads and writes are blocked in this milestone.
- The adapter does not call `security`, import native frameworks, prompt for access, or print secret values.

## Manual Storage Guidance

Store secrets manually with Keychain Access or a password manager, then expose the value to the agent through a process environment variable when needed. Do not paste values into tracked docs, prompt files, reports, or command history that will be committed.

Example environment-only launch pattern:

```bash
export GITHUB_TOKEN="<from-password-manager>"
./.venv/bin/python smart_agent.py secrets doctor github
```

Do not commit `.env`, token files, OAuth caches, private keys, credential files, or Keychain exports.

## Future Real Adapter Requirements

Any future real Keychain adapter must be implemented in a separate prompt and must:

- remain optional and disabled by default;
- require explicit user action before reading or writing;
- route through ToolBroker, PolicyEngine, ApprovalManager where risk requires it, and AuditLogger;
- never print or store secret values;
- use tests with mocks only;
- fail closed on unsupported platforms or denied permissions;
- update the capability manifest, command registry, threat model, and release checklist.
