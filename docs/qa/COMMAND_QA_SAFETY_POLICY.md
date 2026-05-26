# Command QA Safety Policy

Command QA is safe-only by default.

## Default Denials

The QA sandbox must deny automatic execution of commands that:

- Have `HIGH`, `CRITICAL`, or `FORBIDDEN` risk.
- Require personal-data connector access.
- Send, post, publish, message, email, vote, comment, upload, delete, or modify external state.
- Write real user files outside the disposable QA workspace.
- Require provider credentials, paid APIs, live browser sessions, private app databases, or background services.
- Require package installation, model download, native runtime startup, or unreviewed plugin/skill execution.

## Allowed Automatic Scope

Automatic runs are limited to:

- Tier 0 registry/docs validation.
- Tier 1 help/status/doctor/read-only local commands.
- Tier 2 mocked provider commands.
- Tier 3 commands writing only inside a disposable QA workspace.

Tier 4 through Tier 7 are dry-run, opt-in, or manual-review only.

## Redaction

All stdout, stderr, bug reports, regression stubs, and reports must redact:

- API keys, tokens, passwords, private keys, OAuth secrets, and provider credentials.
- Email addresses, phone numbers, and obvious personal identifiers.
- Session logs, audit details, and command arguments that look sensitive.

Reports may include file paths and line numbers when useful, but not raw secrets.

## Approval And Audit

The QA sandbox cannot approve actions. HIGH/CRITICAL commands remain subject to existing ApprovalManager rules, and CRITICAL actions require exact per-action approval with no reuse.

The sandbox records its own run metadata. It must not disable or replace command-level audit logging.
