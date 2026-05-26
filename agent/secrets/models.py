from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SecretDefinition:
    secret_id: str
    env_name: str
    provider: str
    description: str
    required_for: str
    sensitivity: str
    storage_recommendation: str
    docs_path: str
    rotation_url_or_note: str
    placeholder_value: str = ""
    status: str = "active"

    def to_dict(self) -> dict[str, str]:
        return {
            "secret_id": self.secret_id,
            "env_name": self.env_name,
            "provider": self.provider,
            "description": self.description,
            "required_for": self.required_for,
            "sensitivity": self.sensitivity,
            "storage_recommendation": self.storage_recommendation,
            "docs_path": self.docs_path,
            "rotation_url_or_note": self.rotation_url_or_note,
            "placeholder_value": self.placeholder_value,
            "status": self.status,
        }
