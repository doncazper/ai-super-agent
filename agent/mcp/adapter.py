from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from agent.mcp.models import MCPConfig, MCPStatus


@dataclass(frozen=True)
class MCPAdapterBoundary:
    config: MCPConfig = MCPConfig()

    def status(self) -> MCPStatus:
        return MCPStatus(
            status="disabled" if not self.config.enabled else "requires_setup",
            config=self.config,
            server_running=False,
            external_connections=0,
            tools_exposed=0,
            personal_tools_exposed=False,
            notes=(
                "MCP is optional interoperability, not the brain runtime.",
                "No MCP server starts in this milestone.",
                "Future MCP tools must route through ToolBroker, PolicyEngine, approvals, and audit.",
            ),
        )

    def require_toolbroker_route(self, tool_name: str) -> dict[str, object]:
        return {
            "status": "blocked",
            "tool_name": tool_name,
            "reason": "mcp_external_tool_calls_require_toolbroker_route",
            "toolbroker_required": True,
            "policy_required": True,
            "approval_required_for_high_or_critical": True,
            "audit_required": True,
            "executed": False,
        }

    def exposed_tools(self) -> tuple[str, ...]:
        return ()


def mcp_status(env: Mapping[str, str] | None = None) -> dict[str, object]:
    return MCPAdapterBoundary(MCPConfig.from_env(env)).status().to_dict()


def mcp_doctor(env: Mapping[str, str] | None = None) -> dict[str, object]:
    config = MCPConfig.from_env(env)
    return {
        "status": "ok",
        "config": config.to_dict(),
        "brain_runtime_required": False,
        "server_running": False,
        "network_listener_started": False,
        "external_connections": 0,
        "tools_exposed": 0,
        "personal_tools_exposed": False,
        "warnings": _warnings(config),
    }


def mcp_server_dry_run(env: Mapping[str, str] | None = None) -> dict[str, object]:
    config = MCPConfig.from_env(env)
    return {
        "status": "blocked" if not config.enabled or not config.server_enabled else "dry_run_only",
        "dry_run": True,
        "would_start_server": False,
        "network_listener_started": False,
        "tools_exposed": [],
        "toolbroker_required": True,
        "reason": "mcp_server_runtime_not_implemented",
    }


def mcp_clients(env: Mapping[str, str] | None = None) -> dict[str, object]:
    config = MCPConfig.from_env(env)
    return {
        "status": "ok",
        "client_enabled": config.client_enabled,
        "external_connections": [],
        "external_connections_allowed": False,
        "pairing_required": config.require_pairing,
    }


def _warnings(config: MCPConfig) -> list[str]:
    warnings: list[str] = []
    if not config.enabled:
        warnings.append("MCP_ENABLED=false; MCP interop is disabled.")
    if config.server_enabled:
        warnings.append("MCP server runtime is not implemented; no listener will start.")
    if config.expose_personal_tools:
        warnings.append("MCP_EXPOSE_PERSONAL_TOOLS is ignored in this milestone; personal tools are not exposed.")
    return warnings
