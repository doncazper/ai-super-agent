from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from .errors import RuntimeUnavailableError
from .models import RuntimeServiceInfo, RuntimeServiceStatus


DEFAULT_SERVICE_IDS = (
    "core",
    "safety",
    "connectors",
    "memory",
    "promptops",
    "dogfood",
    "command_registry",
    "feature_maturity",
    "app_bridge",
    "platform_bridge",
    "scheduler",
    "self_improvement",
)


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, RuntimeServiceInfo] = {}
        self._loaders: dict[str, Callable[[], Any]] = {}

    def register(self, info: RuntimeServiceInfo, loader: Callable[[], Any] | None = None) -> None:
        self._services[info.service_id] = info
        if loader is not None:
            self._loaders[info.service_id] = loader

    def register_defaults(self) -> None:
        for service_id in DEFAULT_SERVICE_IDS:
            self.register(
                RuntimeServiceInfo(
                    service_id=service_id,
                    name=service_id.replace("_", " ").title(),
                    status=RuntimeServiceStatus.REGISTERED,
                    description="Runtime metadata registration; service is lazy-loaded only by explicit caller.",
                    enabled_by_default=service_id not in {"app_bridge", "platform_bridge", "scheduler"},
                    lazy_load=True,
                )
            )

    def list_services(self) -> tuple[RuntimeServiceInfo, ...]:
        return tuple(self._services[key] for key in sorted(self._services))

    def get(self, service_id: str) -> RuntimeServiceInfo:
        try:
            return self._services[service_id]
        except KeyError as exc:
            raise RuntimeUnavailableError(f"unknown service: {service_id}") from exc

    def set_status(self, service_id: str, status: RuntimeServiceStatus, notes: str = "") -> RuntimeServiceInfo:
        current = self.get(service_id)
        updated = replace(current, status=status, notes=notes or current.notes)
        self._services[service_id] = updated
        return updated

    def load(self, service_id: str) -> Any:
        info = self.get(service_id)
        if not info.enabled_by_default:
            raise RuntimeUnavailableError(f"service is disabled by default: {service_id}")
        loader = self._loaders.get(service_id)
        if loader is None:
            raise RuntimeUnavailableError(f"no loader registered for service: {service_id}")
        return loader()

