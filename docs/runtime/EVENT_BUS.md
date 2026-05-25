# Runtime Event Bus

The event bus is an in-process event stream for runtime metadata.

## Rules

- Events are redacted before storage.
- Untrusted events cannot approve actions, change policy, grant permissions, execute tools, or send messages.
- Events do not replace the hash-chained security audit log.
- Events are not persisted in v1.

## Event Examples

- `runtime.started`
- `service.registered`
- `feature.updated`
- `workflow.registered`
- `job.created`
- `scheduler.evaluated`
- `frontend.request`
- `frontend.response`

## CLI

```bash
python smart_agent.py events tail --limit 10
```

