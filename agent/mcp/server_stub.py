from __future__ import annotations

from agent.mcp.adapter import MCPAdapterBoundary
from agent.mcp.models import MCPConfig


class MCPServerStub:
    def __init__(self, config: MCPConfig | None = None) -> None:
        self.config = config or MCPConfig()
        self.boundary = MCPAdapterBoundary(self.config)

    def is_enabled(self) -> bool:
        return self.config.enabled and self.config.server_enabled

    def start(self) -> dict[str, object]:
        return {
            "status": "blocked",
            "reason": "mcp_server_not_implemented",
            "server_running": False,
            "network_listener_started": False,
            "tools_exposed": 0,
        }

    def expose_tool(self, tool_name: str) -> dict[str, object]:
        return self.boundary.require_toolbroker_route(tool_name)
