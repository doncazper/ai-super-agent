# Tracker To Canonical State Migration

Status: Plan-only preview implemented.

Commands:

```bash
python smart_agent.py runtime tracker-sync-preview
python smart_agent.py runtime tracker-conflicts
```

The migration goal is to make canonical runtime state the machine-readable active-work view while preserving the dense markdown trackers as human-readable evidence records.

## Future Roles

- Canonical runtime state: machine-readable active-work truth.
- `docs/PROMPT_LEDGER.md`: historical prompt evidence.
- `docs/PROMPT_QUEUE.md`: planned order, active, and queued prompt view.
- `docs/PROMPT_AUDIT.md`: reconciliation/audit view.
- `docs/PROJECT_STATE.md`: durable human-readable resume summary.
- `docs/COMPLETION_REPORT.md`: release and validation evidence.
- `docs/TRACKER_DASHBOARD.md`: summary only.
- `docs/HANDOFF_TO_CHATGPT.md`: external communication summary.

## Migration Phases

1. Keep all existing markdown trackers in place.
2. Use canonical state for dashboards, handoffs, and active-work status.
3. Report tracker conflicts before edits.
4. Make small anchored tracker edits only when evidence is clear.
5. Add generated summary views only after release-gate validation.

## Non-Goals

- No broad tracker rewrites.
- No historical detail deletion.
- No automatic tracker overwrite.
- No prompt completion without evidence.
- No runtime execution or provider calls.

The preview command is read-only and writes no files.
