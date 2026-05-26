# Decision: MCP Interop Strategy

Status: specified/scaffolded

MCP is optional interoperability for tools, resources, and prompts. It is not the brain runtime and does not replace the Brain Runtime Gateway.

## Decision

The agent may later add MCP server or client interoperability only behind the same safety control plane used by native tools:

- ToolBroker routes tool-like effects.
- PolicyEngine evaluates capability and risk.
- PermissionManager and ApprovalManager keep existing gates.
- AuditLogger records requests, denials, approvals, and executions.

This milestone adds disabled-by-default stubs only. It does not start an MCP server, connect to external MCP servers, expose tools externally, install MCP packages, or make MCP required for LM Studio/Qwopus behavior.

## Consequences

- Local CLI-only mode remains fully functional without MCP.
- External MCP clients cannot execute tools directly.
- External MCP tools are treated as untrusted until routed through future policy wrappers.
- Personal-data tools remain disabled by default and are not exposed.
- Future MCP network listeners require a separate approval-gated implementation prompt and release gate.
