# Secret Registry

The secret registry is a static metadata inventory. It describes expected env names, providers, setup hints, storage recommendations, and rotation notes. It does not store secret values.

Runtime helpers live under `agent/secrets/`:

- `models.py`: `SecretDefinition`.
- `registry.py`: known secret definitions and provider lookup.
- `redaction.py`: recursive redaction for text, dicts, lists, and fake/test token patterns.
- `errors.py`: registry error types.

The registry is safe to load on any OS. It performs no provider calls, Keychain access, file reads, memory writes, or secret value resolution.
