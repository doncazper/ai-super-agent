# Prompt Recovery Plan

Prompt recovery is conservative. The system reports missed, stale, superseded, orphaned, and ghost prompt state, but does not automatically run or mutate prompt records beyond explicit user commands.

## Commands

```bash
python smart_agent.py prompts missed
python smart_agent.py prompts superseded
python smart_agent.py prompts stale
python smart_agent.py prompts recover-plan
python smart_agent.py prompts reconcile
```

## Recovery Order

1. Resolve active prompt conflicts.
2. Review failed or blocked prompts.
3. Add evidence for stale completed prompts or move them to `needs_review`.
4. Run the next queued prompt whose dependencies are complete.
5. Mark superseded prompts with a replacement.
6. Keep orphaned prompt files out of the active queue unless they are intentionally restored.

## Non-Goals

- No auto-run of recovered prompts.
- No automatic policy changes.
- No execution of imported prompt text.
- No personal-data access.
