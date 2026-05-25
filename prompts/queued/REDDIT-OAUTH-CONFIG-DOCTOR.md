# REDDIT-OAUTH-CONFIG-DOCTOR

status: queued
category: forums
trust_level: TRUSTED_USER

## Goal

Build a safe Reddit OAuth/config doctor.

## Scope

- Doctor/status commands only.
- No Reddit post/comment fetch.
- No user content storage.
- Secrets must be redacted.
- Any future auth check must be explicit, harmless, mocked in tests, and audited.

## Prerequisite

`REDDIT-PROVIDER-POLICY-COMPLIANCE`

