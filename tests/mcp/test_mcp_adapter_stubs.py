from __future__ import annotations

import sys

from agent.mcp.adapter import MCPAdapterBoundary, mcp_clients, mcp_doctor, mcp_server_dry_run, mcp_status
from agent.mcp.client_stub import MCPClientStub
from agent.mcp.models import MCPConfig
from agent.mcp.server_stub import MCPServerStub
from agent.ui import cli_commands
from agent.ui.command_registry import COMMANDS


def test_mcp_stubs_disabled_by_default() -> None:
    status = mcp_status({})

    assert status["status"] == "disabled"
    assert status["server_running"] is False
    assert status["tools_exposed"] == 0
    assert status["personal_tools_exposed"] is False


def test_mcp_server_not_started() -> None:
    server = MCPServerStub(MCPConfig(enabled=True, server_enabled=True))

    result = server.start()

    assert result["status"] == "blocked"
    assert result["network_listener_started"] is False
    assert result["tools_exposed"] == 0


def test_external_tool_call_stub_requires_toolbroker_route() -> None:
    boundary = MCPAdapterBoundary()
    server_result = boundary.require_toolbroker_route("filesystem.read")
    client_result = MCPClientStub(MCPConfig(enabled=True, client_enabled=True)).call_external_tool("external.search")

    assert server_result["toolbroker_required"] is True
    assert server_result["executed"] is False
    assert client_result["policy_required"] is True
    assert client_result["audit_required"] is True


def test_personal_tools_not_exposed_even_when_env_requests_them() -> None:
    status = mcp_doctor({"MCP_ENABLED": "true", "MCP_EXPOSE_PERSONAL_TOOLS": "true"})

    assert status["personal_tools_exposed"] is False
    assert any("ignored" in warning for warning in status["warnings"])


def test_config_defaults_safe() -> None:
    config = MCPConfig.from_env({})

    assert config.enabled is False
    assert config.server_enabled is False
    assert config.client_enabled is False
    assert config.allow_external_clients is False
    assert config.require_pairing is True
    assert config.expose_personal_tools is False


def test_mcp_import_does_not_start_server_or_import_packages() -> None:
    assert "mcp" not in {name for name in sys.modules if name == "mcp"}
    assert mcp_server_dry_run({})["network_listener_started"] is False
    assert mcp_clients({})["external_connections"] == []


def test_mcp_cli_commands(capsys) -> None:
    assert cli_commands.dispatch_cli(["brain", "mcp-decision"]) == 0
    assert cli_commands.dispatch_cli(["mcp", "status"]) == 0
    assert cli_commands.dispatch_cli(["mcp", "doctor"]) == 0
    assert cli_commands.dispatch_cli(["mcp", "server", "--dry-run"]) == 0
    assert cli_commands.dispatch_cli(["mcp", "clients"]) == 0
    output = capsys.readouterr().out
    assert "server_running" in output
    assert "network_listener_started" in output


def test_command_registry_updated_for_mcp_commands() -> None:
    commands = {record.command_id: record for record in COMMANDS}

    assert commands["CMD-BRAIN-009"].status == "active"
    assert commands["CMD-MCP-001"].command == "python smart_agent.py mcp status"
    assert commands["CMD-MCP-004"].command == "python smart_agent.py mcp clients"
