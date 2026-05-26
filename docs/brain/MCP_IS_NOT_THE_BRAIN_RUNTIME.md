# MCP Is Not The Brain Runtime

The Brain Runtime Gateway is the model-facing boundary. MCP is not required for chat, routing, provider health checks, benchmark/eval reports, or local ToolBroker execution.

## Non-Negotiables

- MCP must not load models.
- MCP must not replace LM Studio, Qwopus, or the provider-neutral BrainProvider interface.
- MCP must not be required for no-tools chat.
- MCP must not start a server or listener by default.
- MCP must not grant tool access, approvals, permissions, connector access, memory access, or policy exemptions.

## Current State

`agent.mcp` contains metadata-only stubs:

- `MCPAdapterBoundary`
- `MCPServerStub`
- `MCPClientStub`

These stubs return disabled/blocked status and prove the boundary shape. They do not make external MCP calls or expose local tools.
