# Decision: Agent Gateway / Runtime Kernel Boundary

Date: 2026-05-25
Status: Accepted for CANON-03 scaffolding

## Context

Future local app, mobile, web dashboard, and channel frontends need a stable boundary that does not duplicate runtime logic or bypass safety systems.

## Decision

Define an Agent Gateway as the request-normalization boundary and a Runtime Kernel as the owner of execution truth. The CLI remains the first frontend. CANON-03 adds metadata contracts and read-only status commands only.

## Consequences

- Future frontends have a contract to consume.
- Gateway previews can never execute tools directly or approve their own actions.
- Runtime Kernel ownership is documented before any server or native UI exists.
- Future implementation must still route real effects through ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger.
