from __future__ import annotations

import json
from pathlib import Path


class PermissionStore:
    def __init__(self, path: str | Path = "data/permissions.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def show(self) -> list[str]:
        return sorted(self._load())

    def grant(self, capability: str) -> list[str]:
        grants = self._load()
        grants.add(capability)
        self._save(grants)
        return self.show()

    def revoke(self, capability: str) -> list[str]:
        grants = self._load()
        grants.discard(capability)
        self._save(grants)
        return self.show()

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        return set(json.loads(self.path.read_text(encoding="utf-8")).get("grants", []))

    def _save(self, grants: set[str]) -> None:
        self.path.write_text(json.dumps({"grants": sorted(grants)}, indent=2) + "\n", encoding="utf-8")
