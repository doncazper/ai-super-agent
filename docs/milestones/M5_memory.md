# M5 Memory

## Scope

Add useful memory without storing private data automatically.

## Non-Goals

No automatic storage of email, messages, contacts, calendar content, secrets, or private documents.

## Requirements

- Session memory.
- Persistent memory.
- Memory search.
- Memory permissions.
- Memory lifecycle manager.
- Memory export/delete.
- SQLite storage.
- Local embeddings only if straightforward.

## Risks

- Secrets stored accidentally.
- Personal data retained without approval.
- Deletion incomplete.

## Tests

- Preference memory stored.
- Secret memory rejected or redacted.
- Email/message body not stored by default.
- Personal data requires approval.
- Memory search respects scope.
- Memory delete removes records and embeddings.
- Memory operations audited.

## Approval Gate

Personal-data memory requires explicit approval.
