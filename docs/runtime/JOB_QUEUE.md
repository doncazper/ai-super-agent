# Runtime Job Queue

The runtime job queue is in-process metadata in v1. It is not a background worker and it is not persisted across processes.

## Job States

- `queued`
- `approval_required`
- `blocked`
- `running`
- `completed`
- `failed`
- `cancelled`

## Rules

- Creating a job does not execute tools.
- HIGH jobs become `approval_required`.
- CRITICAL jobs become `blocked`.
- The queue cannot retry CRITICAL jobs into running state.
- The queue does not store secrets or personal content.

## CLI

```bash
python smart_agent.py jobs list
python smart_agent.py jobs show job_000001
```

