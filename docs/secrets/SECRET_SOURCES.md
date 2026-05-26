# Secret Sources

Secrets are resolved in a safe order without printing or storing values:

1. Explicit runtime config supplied by a safe caller.
2. Process environment variables.
3. Local `.env` / `.env.local`, only when ignored and untracked.
4. macOS Keychain, future optional adapter.
5. Password manager manual entry.

`agent/secrets/env_loader.py` includes a small dependency-free `.env` parser. It reports invalid-line warnings without printing raw line contents. `agent/secrets/resolver.py` returns presence/source/setup metadata only.

Environment variables override `.env` values. Missing `.env` is normal. Keychain is not accessed by this milestone.
