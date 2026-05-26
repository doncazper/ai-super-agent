# Secret Redaction Policy

Redaction is mandatory anywhere secret-like values may appear.

## Must Redact

- Known secret env var values.
- Values under keys containing `api_key`, `token`, `secret`, `password`, `authorization`, or `credential`.
- Common token patterns including OpenAI-style keys, GitHub PATs, Google OAuth tokens, Telegram bot tokens, private key blocks, and provider API keys.
- Nested dict/list/report structures.

## Output Rules

- Prefer `[REDACTED]` or `[REDACTED_SECRET]`.
- Preserve last-four characters only when a specific command explicitly documents that it is safe.
- Never log or print raw values to prove redaction works.
- Tests must use fake representative values only.

## Prompt And Report Handling

Prompt text, docs, logs, bug reports, QA reports, and eval reports may contain fake examples. If they contain likely real values, stop and clean them before continuing.
