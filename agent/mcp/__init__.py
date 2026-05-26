"""Optional MCP interop stubs.

This package is intentionally metadata-only. Importing it must not start an MCP
server, connect to external MCP servers, or expose tools.
"""

from agent.mcp.adapter import MCPAdapterBoundary, mcp_status
from agent.mcp.client_stub import MCPClientStub
from agent.mcp.models import MCPConfig, MCPStatus
from agent.mcp.server_stub import MCPServerStub

__all__ = ["MCPAdapterBoundary", "MCPClientStub", "MCPConfig", "MCPServerStub", "MCPStatus", "mcp_status"]
