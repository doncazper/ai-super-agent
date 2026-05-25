# Skill Lockfile

The native skill lockfile is intended to prevent silent skill changes from altering agent behavior.

`native_skills.lock.example` shows the expected schema. A future reviewed `native_skills.lock` can pin reviewed skill records with:

- `skill_id`
- `version`
- `source_type`
- `source_path` / `source_url`
- file `hash`
- `pinned`
- `reviewed_at`
- `trust_status`
- `manifest_hash`
- `dependencies_hash`
- `effective_root`
- `winning_precedence`
- `shadowed_by`
- `generated_at`

Read-only commands:

```bash
python smart_agent.py skills lock status
python smart_agent.py skills lock verify
```

`lock status` computes expected lock records without writing a lockfile. `lock verify` compares the current manifests with `native_skills.lock` when present. If no lockfile exists, it returns `requires_setup` inside the verification payload instead of creating one automatically.

Pinning and unpinning are deliberately deferred until a future approval-reviewed write path exists. There is no auto-update behavior in this milestone.
