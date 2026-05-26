# Secrets Management Policy

This repository must never track real API keys, OAuth tokens, private keys, client secrets, credential files, local Keychain exports, or raw secret scan reports.

## Rules

- Store real secrets in a password manager, macOS Keychain, shell environment, or local untracked `.env`.
- Keep `.env`, `.env.*`, token files, credential files, and private keys ignored by git.
- Keep `.env.example` and `docs/templates/env_template.example` as placeholders only.
- Doctors, status commands, QA reports, prompt tracking, session reports, and audit logs must report only present/missing/redacted metadata.
- Secret values must not be written to memory, session logs, reports, prompt files, bug records, eval fixtures, or command registry docs.
- Provider validity checks may be added only as explicit opt-in live doctors and must stay brokered, audited, redacted, and provider-policy gated.
- If a secret is exposed, rotate or revoke it before continuing release work.

## Approved Sources

1. Existing explicit runtime config, when the value is already safely supplied by the caller.
2. Process environment variables.
3. Local `.env` / `.env.local`, only when ignored and untracked.
4. macOS Keychain or another password manager through explicit future adapters.
5. Manual user entry outside the repo.

## Forbidden Sources

- Tracked files.
- Prompt packs or queued prompt files.
- Raw logs, session reports, QA reports, eval reports, or bug reports.
- Private OS app databases.
- Browser password stores, cookies, or session databases.

## Doctor Boundary

Secret doctors may inspect environment/config presence, git hygiene, token path placement, broad OAuth scopes, and paid-provider policy. They must not print values, call providers by default, enable paid providers, read personal data, or promote a provider to default just because a key exists.

## Rotation And Revocation

If a real key may have been committed or printed:

1. Stop before push.
2. Revoke or rotate the key at the provider.
3. Remove/redact the value and add ignore rules.
4. Re-scan tracked files and staged diffs.
5. Re-run tests and release gates.
6. If the commit was already pushed, follow provider incident response and repository history cleanup guidance.
