from __future__ import annotations

import platform
from dataclasses import dataclass

from .errors import UnknownSecretError
from .registry import SecretRegistry, default_secret_registry


@dataclass(frozen=True)
class KeychainStatus:
    platform: str
    supported: bool
    enabled: bool
    real_access_enabled: bool
    setup_hint: str

    def to_dict(self) -> dict[str, object]:
        return {
            "platform": self.platform,
            "supported": self.supported,
            "enabled": self.enabled,
            "real_access_enabled": self.real_access_enabled,
            "setup_hint": self.setup_hint,
        }


class KeychainAdapter:
    def __init__(self, *, registry: SecretRegistry | None = None, platform_name: str | None = None) -> None:
        self.registry = registry or default_secret_registry()
        self.platform_name = platform_name or platform.system()

    def status(self) -> dict[str, object]:
        supported = self.platform_name == "Darwin"
        return KeychainStatus(
            platform=self.platform_name,
            supported=supported,
            enabled=False,
            real_access_enabled=False,
            setup_hint=(
                "macOS Keychain adapter is optional and dry-run/mock-only in v1; "
                "store secrets manually in Keychain or a password manager, then expose them via env when needed."
                if supported
                else "macOS Keychain is unsupported on this platform; use environment variables or a password manager."
            ),
        ).to_dict()

    def dry_run_get(self, secret_id: str) -> dict[str, object]:
        definition = self._definition(secret_id)
        status = self.status()
        return {
            "status": "requires_setup" if status["supported"] else "unsupported",
            "secret_id": definition.secret_id,
            "env_name": definition.env_name,
            "dry_run": True,
            "value_returned": False,
            "keychain_accessed": False,
            "setup_hint": status["setup_hint"],
        }

    def dry_run_set(self, secret_id: str) -> dict[str, object]:
        definition = self._definition(secret_id)
        status = self.status()
        return {
            "status": "requires_setup" if status["supported"] else "unsupported",
            "secret_id": definition.secret_id,
            "env_name": definition.env_name,
            "dry_run": True,
            "value_written": False,
            "keychain_accessed": False,
            "setup_hint": "Use the macOS Keychain UI/password manager manually; this command writes nothing.",
        }

    def _definition(self, secret_id: str):
        try:
            return self.registry.get(secret_id)
        except UnknownSecretError:
            raise
