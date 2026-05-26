# MCP Adapter Boundaries

MCP adapters are disabled-by-default stubs in this release track.

## Server Boundary

A future MCP server may expose only policy-gated tools through the existing control plane. It must not:

- start by default;
- expose tools directly;
- expose personal-data tools by default;
- accept unauthenticated external clients;
- bypass ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, or AuditLogger.

Current `MCPServerStub.start()` always returns blocked and confirms no listener starts.

## Client Boundary

A future MCP client may consume external tools only through ToolBroker-like policy wrappers. External tool descriptions, prompts, resources, and results are untrusted data until classified by future policy.

Current `MCPClientStub.connect()` and `call_external_tool()` return blocked.

## Commands

```bash
python smart_agent.py mcp status
python smart_agent.py mcp doctor
python smart_agent.py mcp server --dry-run
python smart_agent.py mcp clients
```

These commands are diagnostics only. They do not connect, listen, expose tools, or execute tools.
