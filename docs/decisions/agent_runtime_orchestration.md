# Decision: Agent Runtime Orchestration

Status: accepted for v1 scaffold.

## Context

The project has grown from a single CLI into a shared codebase with tools, approvals, prompts, dogfood, evals, connectors, and future app frontends. Those pieces need one runtime control plane that can describe status, services, features, workflows, jobs, and events without becoming an unsafe executor.

## Decision

Create a lightweight Python runtime orchestration layer under `agent/runtime/`.

The runtime orchestrator is metadata and coordination first:

- It owns runtime state, service registry, feature flags, workflow metadata, job metadata, event metadata, scheduler policy, and frontend bridge contracts.
- It does not replace `ToolBroker`, `PolicyEngine`, `PermissionManager`, `ApprovalManager`, or `AuditLogger`.
- It does not execute tools directly.
- It does not call LM Studio during status or doctor checks.
- It does not enable personal-data tools by default.
- It does not create background persistence in v1.

## Runtime Boundary

The orchestrator may:

- report runtime status and health;
- list registered lazy services;
- list disabled/enabled feature flags;
- register workflow metadata;
- create in-process job records for safe manual workflow requests;
- publish redacted in-process events;
- provide frontend-safe status/snapshot responses.

The orchestrator may not:

- call connectors directly;
- execute tools outside `ToolBroker`;
- grant permissions;
- approve actions;
- weaken policy;
- reuse CRITICAL approvals;
- read personal connector data;
- start background services;
- send email or messages;
- write calendar/contact/task data.

## Consequences

This gives the future Mac/iOS/frontend layers a common control-plane vocabulary while keeping execution in the existing safety stack. Runtime v1 is intentionally conservative: it improves observability and structure before adding any autonomy.

