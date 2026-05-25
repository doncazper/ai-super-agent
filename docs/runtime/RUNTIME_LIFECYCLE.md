# Runtime Lifecycle

Runtime v1 has a simple lifecycle:

1. `created`
2. `booting`
3. `ready`
4. `degraded`, if a metadata check fails
5. `stopped`
6. `error`, for unexpected runtime failures

Booting registers metadata only:

- default services;
- default feature flags;
- default workflow definitions;
- an in-process event bus;
- an in-process job queue.

Booting does not:

- call LM Studio;
- read personal data;
- start connector adapters;
- start app bridges;
- schedule background jobs;
- execute tools.

## Health Checks

Runtime health checks verify only local metadata boundaries:

- the kernel booted;
- personal-data features remain disabled by default;
- no background persistence is active.

Provider, connector, and model health checks remain in their existing doctor commands and must keep their own safety behavior.

