from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class Session:
    id: str = field(default_factory=lambda: str(uuid4()))
    messages: list[dict[str, Any]] = field(default_factory=list)

    def append(self, message: dict[str, Any]) -> None:
        self.messages.append(message)
