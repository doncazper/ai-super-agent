# MCP Interop Decision

Status: optional and deferred

MCP is not part of the brain runtime boundary. The agent must be able to chat, route, and run local brokered tools without requiring MCP.

## Decision

MCP may be considered later as optional tool interoperability, not as the model runtime. MCP servers must not be enabled by default, started implicitly, or required for LM Studio/Qwopus behavior.

## Rules

- No MCP server starts during import or normal startup.
- No MCP dependency is required for no-tools chat.
- MCP adapters, if added later, must route tool-like effects through ToolBroker-compatible safety boundaries.
- MCP cannot approve actions, weaken policy, grant permissions, or bypass audit.
- MCP prompt/tool content is untrusted unless explicitly classified otherwise by future policy.

## Current State

`BRAIN-10` adds disabled-by-default MCP adapter/server/client stubs and metadata-only `mcp` diagnostic commands. It still adds no MCP runtime server, no external MCP connection, no exposed tools, no network listener, and no MCP dependency requirement.

See `docs/decisions/mcp_interop_strategy.md`, `docs/brain/MCP_IS_NOT_THE_BRAIN_RUNTIME.md`, and `docs/mcp/MCP_ADAPTER_BOUNDARIES.md`.
