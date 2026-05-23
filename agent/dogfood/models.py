from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


RISK_VALUES = {"SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "FORBIDDEN"}


@dataclass(frozen=True)
class DogfoodCommand:
    id: str
    description: str
    command: str
    expected_behavior: str
    failure_signals: str
    tags: tuple[str, ...] = ()
    expected_exit_codes: tuple[int, ...] = (0,)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DogfoodCommand":
        required = ["id", "description", "command", "expected_behavior", "failure_signals", "tags"]
        missing = [field_name for field_name in required if field_name not in data]
        if missing:
            raise ValueError(f"dogfood command missing required fields: {', '.join(missing)}")
        tags = data.get("tags")
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise ValueError(f"dogfood command {data.get('id', '<unknown>')} tags must be a list of strings")
        expected = data.get("expected_exit_codes", [0])
        if not isinstance(expected, list) or not all(isinstance(code, int) for code in expected):
            raise ValueError(f"dogfood command {data.get('id', '<unknown>')} expected_exit_codes must be integers")
        return cls(
            id=str(data["id"]),
            description=str(data["description"]),
            command=str(data["command"]),
            expected_behavior=str(data["expected_behavior"]),
            failure_signals=str(data["failure_signals"]),
            tags=tuple(tags),
            expected_exit_codes=tuple(expected),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "command": self.command,
            "expected_behavior": self.expected_behavior,
            "failure_signals": self.failure_signals,
            "tags": list(self.tags),
            "expected_exit_codes": list(self.expected_exit_codes),
        }


@dataclass(frozen=True)
class DogfoodSuite:
    suite_id: str
    name: str
    description: str
    risk_level: str
    requires_live_lmstudio: bool
    requires_web: bool
    requires_personal_data: bool
    default_enabled: bool
    commands: tuple[DogfoodCommand, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DogfoodSuite":
        required = [
            "suite_id",
            "name",
            "description",
            "risk_level",
            "requires_live_lmstudio",
            "requires_web",
            "requires_personal_data",
            "default_enabled",
            "commands",
        ]
        missing = [field_name for field_name in required if field_name not in data]
        if missing:
            raise ValueError(f"dogfood suite missing required fields: {', '.join(missing)}")
        risk = str(data["risk_level"])
        if risk not in RISK_VALUES:
            raise ValueError(f"dogfood suite {data.get('suite_id', '<unknown>')} has invalid risk_level {risk}")
        commands = data.get("commands")
        if not isinstance(commands, list) or not commands:
            raise ValueError(f"dogfood suite {data.get('suite_id', '<unknown>')} must define commands")
        return cls(
            suite_id=str(data["suite_id"]),
            name=str(data["name"]),
            description=str(data["description"]),
            risk_level=risk,
            requires_live_lmstudio=bool(data["requires_live_lmstudio"]),
            requires_web=bool(data["requires_web"]),
            requires_personal_data=bool(data["requires_personal_data"]),
            default_enabled=bool(data["default_enabled"]),
            commands=tuple(DogfoodCommand.from_dict(command) for command in commands),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "requires_live_lmstudio": self.requires_live_lmstudio,
            "requires_web": self.requires_web,
            "requires_personal_data": self.requires_personal_data,
            "default_enabled": self.default_enabled,
            "commands": [command.to_dict() for command in self.commands],
        }
