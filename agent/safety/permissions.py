from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PermissionManager:
    """In-memory capability permissions for M1."""

    grants: set[str] = field(default_factory=set)

    def grant(self, capability: str) -> None:
        self.grants.add(capability)

    def revoke(self, capability: str) -> None:
        self.grants.discard(capability)

    def is_granted(self, capability: str) -> bool:
        return capability in self.grants
