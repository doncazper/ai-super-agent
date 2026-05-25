from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping


Environment = Mapping[str, str]
CapabilitiesConfig = Mapping[str, Any]
ConfigurationProbe = Callable[[Environment], "ConnectorConfiguration"]
CacheProbe = Callable[[Environment], str | dict[str, Any]]
HealthProbe = Callable[[Environment], "ConnectorHealth"]


@dataclass(frozen=True)
class ConnectorConfiguration:
    configured: bool
    provider_name: str
    setup_hint: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectorHealth:
    status: str
    message: str
    checked: bool = True
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ConnectorDefinition:
    name: str
    capability_prefixes: tuple[str, ...]
    configuration_probe: ConfigurationProbe
    setup_docs: str = ""
    cache_probe: CacheProbe | None = None
    health_probe: HealthProbe | None = None
    personal_data: bool = False
    health_accesses_personal_data: bool = False
    excluded_capabilities: tuple[str, ...] = ()

    def capability_entries(self, config: CapabilitiesConfig) -> dict[str, Mapping[str, Any]]:
        tools = config.get("tools", {})
        if not isinstance(tools, Mapping):
            return {}
        return {
            name: entry
            for name, entry in tools.items()
            if isinstance(name, str)
            and name.startswith(self.capability_prefixes)
            and name not in self.excluded_capabilities
            and isinstance(entry, Mapping)
        }


@dataclass(frozen=True)
class ConnectorStatus:
    name: str
    configured: bool
    enabled: bool
    default_provider: str
    risk_level: str
    approval_required: bool | str
    last_successful_call: str | None
    last_error: str | None
    rate_limit_state: dict[str, Any]
    cache_state: str | dict[str, Any]
    docs_setup_hint: str
    status: str
    health: ConnectorHealth | None = None
    capabilities: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "configured": self.configured,
            "enabled": self.enabled,
            "default_provider": self.default_provider,
            "risk_level": self.risk_level,
            "approval_required": self.approval_required,
            "last_successful_call": self.last_successful_call,
            "last_error": self.last_error,
            "rate_limit_state": self.rate_limit_state,
            "cache_state": self.cache_state,
            "docs_setup_hint": self.docs_setup_hint,
            "setup_hint": self.docs_setup_hint,
            "capabilities": self.capabilities,
            "status": self.status,
        }
        if self.health is not None:
            payload["health"] = {
                "status": self.health.status,
                "message": self.health.message,
                "checked": self.health.checked,
                "details": self.health.details,
            }
        payload.update(self.metadata)
        return payload
