# Cross-Session Continuity

Cross-session continuity v1 builds redacted summaries and previews from already-approved local memory records. It is designed to help future sessions resume work without carrying secrets, raw transcripts, personal data, or unapproved memory into prompts.

## Commands

```bash
python smart_agent.py memory continuity status
python smart_agent.py memory continuity build-summary --query "release hardening"
python smart_agent.py memory continuity clear
```

## Behavior

- `status` reports local memory counts and policy state only.
- `build-summary` selects safe categories, redacts secrets/emails/phone-like values, enforces character limits, and returns selected memory IDs.
- `clear` is a safe no-op in v1 because no separate continuity profile is persisted.
- No cloud embeddings, background persistence, model calls, or automatic prompt injection are used.
- Personal categories and personal trust levels are excluded by default.

## Safe Categories

- `session_context`
- `user_preference`
- `project_fact`
- `workflow_lesson`

## Deferred

- Persistent continuity profiles.
- Semantic search/embeddings.
- Personal-data continuity.
- Automatic cross-session prompt injection.

Any future expansion must add capability manifest entries, ToolBroker routing, policy/audit coverage, approval gates for personal data, retention docs, and release-gate evidence first.
