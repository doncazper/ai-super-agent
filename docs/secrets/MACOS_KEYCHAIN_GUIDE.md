# macOS Keychain Guide

macOS Keychain is the preferred local storage for long-lived secrets when a future adapter is explicitly enabled. This project does not require Keychain and must remain portable without it.

## Current Status

- Keychain is recommended but optional.
- No Keychain reads or writes occur by default.
- Tests must use mocks only.
- Manual Keychain setup should never export secrets into the repo.
- `python smart_agent.py secrets keychain status` reports metadata only.
- `python smart_agent.py secrets keychain get <secret_id> --dry-run` and `set <secret_id> --dry-run` never read or write values.

## Manual Pattern

Store a secret manually with the macOS Passwords/Keychain UI or a password manager, then expose it to the agent only for a single shell session when needed:

```sh
export SERPAPI_API_KEY="<paste from password manager>"
```

Do not commit shell transcripts, exported Keychain files, or screenshots containing values.

## Future Adapter Boundary

A future adapter must be disabled by default, dry-run by default for writes, never print returned values, return unsupported on non-macOS, and route all executable behavior through the safety control plane.
