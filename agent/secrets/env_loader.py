from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .redaction import SecretRedactor


@dataclass(frozen=True)
class EnvLoadResult:
    path: str
    exists: bool
    values: dict[str, str]
    warnings: list[dict[str, str]]

    def redacted_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "exists": self.exists,
            "keys": sorted(self.values),
            "value_count": len(self.values),
            "warnings": self.warnings,
        }


class EnvFileLoader:
    def load(self, path: str | Path) -> EnvLoadResult:
        env_path = Path(path)
        if not env_path.exists():
            return EnvLoadResult(str(env_path), False, {}, [])

        values: dict[str, str] = {}
        warnings: list[dict[str, str]] = []
        for line_no, raw_line in enumerate(env_path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                warnings.append(
                    {
                        "code": "invalid_env_line",
                        "line": str(line_no),
                        "message": "Invalid .env line ignored without printing its contents.",
                    }
                )
                continue
            key, raw_value = stripped.split("=", 1)
            key = key.strip()
            if not key or any(char.isspace() for char in key):
                warnings.append(
                    {
                        "code": "invalid_env_key",
                        "line": str(line_no),
                        "message": "Invalid .env key ignored without printing its value.",
                    }
                )
                continue
            value = raw_value.strip().strip("'\"")
            values[key] = value
        return EnvLoadResult(str(env_path), True, values, SecretRedactor().redact(warnings))
