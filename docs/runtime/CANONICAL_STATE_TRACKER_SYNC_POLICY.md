# Canonical State Tracker Sync Policy

Status: Plan-only policy implemented.

Canonical state may summarize active work, but it must not silently overwrite trackers.

## Policy

- Use conflict reports before edits.
- Prefer small anchored edits.
- Preserve prompt history and completion evidence.
- Keep at most one active prompt.
- Do not mark prompts complete without tests/docs/evidence.
- Do not delete historical detail unless moved to an archive with evidence links.
- If trackers disagree, report the disagreement instead of guessing.
- Summary dashboards are navigation aids, not primary truth.

## Conflict Command

```bash
python smart_agent.py runtime tracker-conflicts
```

The command reports canonical tracker conflicts and exits without mutation.

## Approved Fix Style

Allowed:

- update one stale `active_prompt_id`
- correct one queued/completed prompt row when evidence exists
- add missing docs links
- add a completion-report evidence pointer

Not allowed:

- rewrite entire dense trackers
- auto-run queued prompts
- overwrite prompt ledgers from generated state
- claim live validation without live evidence
- hide unresolved conflicts
