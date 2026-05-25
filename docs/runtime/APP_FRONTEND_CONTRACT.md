# App Frontend Contract

A future app frontend can display runtime status, services, features, workflows, jobs, events, and health.

The frontend must not:

- call tools directly;
- grant approvals directly;
- infer permission from UI state;
- read personal connector data for dashboard display;
- start background work silently;
- send messages or email.

All risky actions must become Action Center items and then execute through ToolBroker only after policy and approval checks pass.

