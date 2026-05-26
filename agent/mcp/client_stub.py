from __future__ import annotations

from agent.mcp.adapter import MCPAdapterBoundary
from agent.mcp.models import MCPConfig


class MCPClientStub:
    def __init__(self, config: MCPConfig | None = None) -> None:
        self.config = config or MCPConfig()
        self.boundary = MCPAdapterBoundary(self.config)

    def is_enabled(self) -> bool:
        return self.config.enabled and self.config.client_enabled

    def connect(self, server_id: str) -> dict[str, object]:
        return {
            "status": "blocked",
            "server_id": server_id,
            "reason": "external_mcp_connections_not_implemented",
            "connected": False,
            "pairing_required": self.config.require_pairing,
        }

    def call_external_tool(self, tool_name: str) -> dict[str, object]:
        return self.boundary.require_toolbroker_route(tool_name)
