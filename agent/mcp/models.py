from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from agent.config.runtime import env_bool


@dataclass(frozen=True)
class MCPConfig:
    enabled: bool = False
    server_enabled: bool = False
    client_enabled: bool = False
    allow_external_clients: bool = False
    require_pairing: bool = True
    expose_personal_tools: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "MCPConfig":
        if env is None:
            return cls(
                enabled=env_bool("MCP_ENABLED", default=cls.enabled),
                server_enabled=env_bool("MCP_SERVER_ENABLED", default=cls.server_enabled),
                client_enabled=env_bool("MCP_CLIENT_ENABLED", default=cls.client_enabled),
                allow_external_clients=env_bool("MCP_ALLOW_EXTERNAL_CLIENTS", default=cls.allow_external_clients),
                require_pairing=env_bool("MCP_REQUIRE_PAIRING", default=cls.require_pairing),
                expose_personal_tools=env_bool("MCP_EXPOSE_PERSONAL_TOOLS", default=cls.expose_personal_tools),
            )

        def flag(name: str, default: bool) -> bool:
            value = env.get(name)
            if value is None:
                return default
            return value.strip().casefold() in {"1", "true", "yes", "on"}

        return cls(
            enabled=flag("MCP_ENABLED", cls.enabled),
            server_enabled=flag("MCP_SERVER_ENABLED", cls.server_enabled),
            client_enabled=flag("MCP_CLIENT_ENABLED", cls.client_enabled),
            allow_external_clients=flag("MCP_ALLOW_EXTERNAL_CLIENTS", cls.allow_external_clients),
            require_pairing=flag("MCP_REQUIRE_PAIRING", cls.require_pairing),
            expose_personal_tools=flag("MCP_EXPOSE_PERSONAL_TOOLS", cls.expose_personal_tools),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "server_enabled": self.server_enabled,
            "client_enabled": self.client_enabled,
            "allow_external_clients": self.allow_external_clients,
            "require_pairing": self.require_pairing,
            "expose_personal_tools": self.expose_personal_tools,
        }


@dataclass(frozen=True)
class MCPStatus:
    status: str
    config: MCPConfig
    server_running: bool = False
    external_connections: int = 0
    tools_exposed: int = 0
    personal_tools_exposed: bool = False
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "config": self.config.to_dict(),
            "server_running": self.server_running,
            "external_connections": self.external_connections,
            "tools_exposed": self.tools_exposed,
            "personal_tools_exposed": self.personal_tools_exposed,
            "notes": list(self.notes),
        }
