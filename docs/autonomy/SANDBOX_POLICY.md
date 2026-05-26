# Sandbox Policy

Status: HERMES-08 policy scaffold.

Sandbox execution is disabled in the current release track. The sandbox layer is a planning and dry-run boundary so future code execution, browser automation, subagents, and self-improvement work can share one reviewed safety model.

## Default Policy

- Default backend: `mock`
- Execution enabled: no
- Network enabled: no
- Personal data enabled: no
- Arbitrary commands enabled: no
- Filesystem scope: workspace roots only
- Memory writes: no
- Audit: required for sandbox commands

## Denied In V1

- arbitrary scripts or shell commands;
- networked sandbox execution;
- browser automation;
- Docker, VM, or cloud sandbox execution;
- broad filesystem mounts;
- private home-directory or app-data mounts;
- personal-data access;
- background persistence;
- plugin runtime execution.

## ToolBroker Boundary

CLI sandbox commands route through ToolBroker/PolicyEngine/AuditLogger. Future executable backends must use the same route and cannot be called directly by workflows, subagents, model output, or untrusted content.

## Approval Boundary

HIGH and CRITICAL sandbox requests are blocked in this scaffold. Future executable high-risk requests must require exact previews, per-action approval when CRITICAL, no approval reuse for CRITICAL, and audit evidence.

## Unsupported Backends

Planned or deferred backends return setup hints instead of attempting best-effort execution. Missing backend names are denied.
