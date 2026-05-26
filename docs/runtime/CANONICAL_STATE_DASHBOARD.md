# Canonical State Dashboard

Status: Implemented as read-only metadata.

Command:

```bash
python smart_agent.py runtime canonical-dashboard
```

The dashboard aggregates canonical runtime metadata for handoff and release review. It reports:

- canonical state summary
- active prompt, job, workflow, and action IDs
- next prompt ID
- last validation evidence from completion records
- tracker conflict preview
- dirty worktree summary
- safety summary
- Agent Gateway and Runtime Kernel status
- recovery/resume hints
- recommended handoff files

The command is read-only. It does not execute tools, call providers, inspect personal connectors, write memory, mutate trackers, resume work, start services, or create a handoff file.

## Trust Boundary

The dashboard is a summary view. It is not the primary source of truth. When records disagree, prefer:

1. `SPEC.md`
2. `docs/SDLC.md`
3. `AGENTS.md`
4. `config/capabilities.yaml`
5. actual code/tests
6. canonical runtime state JSON/model
7. command, feature, maturity, and prompt trackers

Use `runtime reconcile-preview` when the dashboard reports tracker conflicts.
