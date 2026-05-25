# Runtime Orchestration Strategy

The runtime orchestrator is the shared control plane for the local agent. It helps CLI, future app frontends, PromptOps, dogfood, evals, and workflow surfaces understand what exists and what is safe to run.

## Goals

- One source of runtime status for CLI and future app frontends.
- Lazy services so startup stays fast.
- Clear feature flags for risky and personal-data capabilities.
- Workflow and job metadata that can stop at approval gates.
- Event records that are data, not authority.
- Frontend bridge contracts that cannot approve or execute actions directly.

## Non-Goals

- No direct tool execution.
- No LM Studio call in status or runtime doctor.
- No personal-data connector access.
- No background daemon, cron, launch agent, or app bridge in v1.
- No email/text send or calendar/contact write capability.
- No replacement for security audit logs.

## Safety Invariant

All real side effects stay behind the existing safety stack:

`User request -> Router/workflow -> ToolBroker -> PolicyEngine -> PermissionManager/ApprovalManager -> AuditLogger -> Tool`

Runtime orchestration can describe or queue work, but it cannot skip that chain.

## Startup Policy

Runtime imports should remain light. Importing `agent.runtime` must not import model clients, native app bridges, web providers, personal connector adapters, or ToolBroker.

