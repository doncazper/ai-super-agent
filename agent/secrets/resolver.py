from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .env_loader import EnvFileLoader, EnvLoadResult
from .registry import SecretRegistry, default_secret_registry
from .redaction import SecretRedactor


@dataclass(frozen=True)
class SecretResolution:
    secret_id: str
    env_name: str
    provider: str
    present: bool
    source: str | None
    setup_hint: str
    warnings: list[dict[str, str]]

    def to_dict(self) -> dict[str, object]:
        return {
            "secret_id": self.secret_id,
            "env_name": self.env_name,
            "provider": self.provider,
            "present": self.present,
            "source": self.source,
            "setup_hint": self.setup_hint,
            "warnings": self.warnings,
        }


class SecretResolver:
    def __init__(
        self,
        *,
        registry: SecretRegistry | None = None,
        environ: Mapping[str, str] | None = None,
        project_root: str | Path = ".",
        env_path: str | Path | None = None,
    ) -> None:
        self.registry = registry or default_secret_registry()
        self.environ = environ or os.environ
        self.project_root = Path(project_root).resolve()
        self.env_path = Path(env_path) if env_path is not None else self.project_root / ".env"
        self.env_result: EnvLoadResult = EnvFileLoader().load(self.env_path)

    def resolve(self, secret_id_or_env_name: str) -> SecretResolution:
        definition = self.registry.get(secret_id_or_env_name)
        env_value = self.environ.get(definition.env_name)
        dot_env_value = self.env_result.values.get(definition.env_name)
        if env_value:
            present = True
            source = "environment"
        elif dot_env_value:
            present = True
            source = "local_env"
        else:
            present = False
            source = None
        return SecretResolution(
            secret_id=definition.secret_id,
            env_name=definition.env_name,
            provider=definition.provider,
            present=present,
            source=source,
            setup_hint=f"Set {definition.env_name} via environment, Keychain/password manager, or ignored local .env.",
            warnings=SecretRedactor().redact(self.env_result.warnings),
        )

    def resolve_provider(self, provider: str) -> list[SecretResolution]:
        return [self.resolve(definition.env_name) for definition in self.registry.by_provider(provider)]

    def status(self) -> dict[str, object]:
        resolutions = [self.resolve(definition.env_name).to_dict() for definition in self.registry.list()]
        return SecretRedactor().redact(
            {
                "status": "ok",
                "secret_count": len(resolutions),
                "present_count": sum(1 for item in resolutions if item["present"]),
                "missing_count": sum(1 for item in resolutions if not item["present"]),
                "values_returned": False,
                "env_file": self.env_result.redacted_dict(),
                "resolutions": resolutions,
            }
        )
