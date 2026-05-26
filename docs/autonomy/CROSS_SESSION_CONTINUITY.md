# Cross-Session Continuity

Last updated: 2026-05-25

## Scope

Cross-session continuity is opt-in groundwork. The current implementation exposes status, redacted export metadata, and clear/no-op behavior. It does not store or carry personal data across sessions by default.

## Policy

- Continuity is disabled unless explicitly configured.
- Personal data is not carried by default.
- Redaction is always required for exported summaries.
- Continuity cannot bypass memory policy.
- Tool-call compatibility must be checked before a model switch that depends on tools.
- Cloud/paid model switching remains blocked unless future policy explicitly allows it.

## CLI

```bash
python smart_agent.py session continuity status
python smart_agent.py session continuity export --redacted
python smart_agent.py session continuity clear
```

`export --redacted` returns a structured redacted payload and writes no file by default. `clear` reports zero deleted entries while no persistent continuity store exists.

## Export Shape

Continuity exports include:

- redacted context summary;
- source session id, if provided;
- generated timestamp;
- included/excluded field lists;
- `memory_written=false`.

Excluded fields include raw messages, personal data, tool outputs, secrets, and unredacted session logs.

## Forbidden In v1

- raw session transcript migration;
- personal-data carryover by default;
- memory-policy bypass;
- hidden background continuity persistence;
- provider switch persistence;
- model calls or tool calls during continuity inspection;
- paid/cloud provider switching by default.

## Future Approval Gates

Any future persistent continuity store must add tests and approval review for:

- retention and deletion;
- redaction quality;
- personal-data classification;
- user-visible export/clear behavior;
- audit evidence;
- no-tools mode preservation;
- rollback after failed provider/model switches.
