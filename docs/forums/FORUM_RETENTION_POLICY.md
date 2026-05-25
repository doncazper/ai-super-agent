# Forum Retention Policy

Status: planning policy

## Defaults

- Do not store Reddit/forum content permanently by default.
- Do not store forum search history by default.
- Do not store author-identifying metadata by default.
- Do not store deleted or removed content.
- Do not use forum content for model training.
- Keep cache TTLs explicit, bounded, and configurable.

## Cache Rules

Future forum cache entries may store public metadata needed for dedupe, source attribution, and refresh safety:

- source ID,
- URL/permalink,
- provider,
- retrieved timestamp,
- expiration timestamp,
- content hash,
- title or thread title,
- snippet or bounded excerpt,
- trust level,
- source status,
- retention policy version.

Full post/thread/comment body storage must be optional, disabled by default, and covered by separate tests and docs before release.

## Author Metadata

Author metadata can be identifying even when public. The default must be redacted or absent. If a future workflow needs author display names for source context, it must be explicitly configured, TTL-bounded, documented, and excluded from memory by default.

## Deletion And Removal

Deleted, removed, or unavailable content must not be retained as evidence. Retention sweepers must delete expired cached content and author-identifying fields. Privacy reports should show counts and policy status, not raw content.

## Training Boundary

Reddit/forum content must not be used for model training unless explicit rights, permission, and a separate governance decision exist. This project does not add that path in this track.
