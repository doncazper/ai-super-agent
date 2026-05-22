from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class RuntimeConfigError(ValueError):
    pass


def load_dotenv(path: str | Path = ".env") -> None:
    dotenv = Path(path)
    if not dotenv.exists():
        return
    for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_value(primary: str, *fallbacks: str, default: str = "") -> str:
    for key in (primary, *fallbacks):
        value = os.getenv(key)
        if value is not None and value != "":
            return value
    return default


def env_bool(primary: str, *, default: bool = False) -> bool:
    value = os.getenv(primary)
    if value is None or value == "":
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def parse_float(name: str, value: str, *, minimum: float, maximum: float) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise RuntimeConfigError(f"{name} must be a number.") from exc
    if parsed < minimum or parsed > maximum:
        raise RuntimeConfigError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def parse_int(name: str, value: str, *, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeConfigError(f"{name} must be an integer.") from exc
    if parsed < minimum or parsed > maximum:
        raise RuntimeConfigError(f"{name} must be between {minimum} and {maximum}.")
    return parsed


def validate_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeConfigError(
            "LMSTUDIO_BASE_URL must be a valid http(s) URL, for example http://localhost:1234/v1."
        )
    return base_url.rstrip("/")


@dataclass(frozen=True)
class RuntimeConfig:
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_model: str = ""
    temperature: float = 0.7
    top_p: float = 0.95
    max_tokens: int = 2048
    tool_mode: str = "auto"
    debug: bool = False
    audit_log_path: str = "logs/audit.jsonl"
    capabilities_path: str = "config/capabilities.yaml"

    @classmethod
    def from_env(cls, *, load_env_file: bool = True) -> "RuntimeConfig":
        if load_env_file:
            load_dotenv()
        base_url = validate_base_url(
            env_value("LMSTUDIO_BASE_URL", default=cls.lmstudio_base_url)
        )
        tool_mode = env_value("TOOL_MODE", default=cls.tool_mode).casefold()
        if tool_mode not in {"auto", "no-tools", "force-time"}:
            raise RuntimeConfigError("TOOL_MODE must be one of: auto, no-tools, force-time.")
        return cls(
            lmstudio_base_url=base_url,
            lmstudio_model=env_value("LMSTUDIO_MODEL", default=""),
            temperature=parse_float(
                "TEMPERATURE",
                env_value("LMSTUDIO_TEMPERATURE", "TEMPERATURE", default=str(cls.temperature)),
                minimum=0,
                maximum=2,
            ),
            top_p=parse_float(
                "TOP_P",
                env_value("LMSTUDIO_TOP_P", "TOP_P", default=str(cls.top_p)),
                minimum=0,
                maximum=1,
            ),
            max_tokens=parse_int(
                "MAX_TOKENS",
                env_value("LMSTUDIO_MAX_TOKENS", "MAX_TOKENS", default=str(cls.max_tokens)),
                minimum=1,
                maximum=262144,
            ),
            tool_mode=tool_mode,
            debug=env_bool("DEBUG", default=cls.debug),
            audit_log_path=env_value("AUDIT_LOG_PATH", "AGENT_AUDIT_LOG", default=cls.audit_log_path),
            capabilities_path=env_value("CAPABILITIES_CONFIG", default=cls.capabilities_path),
        )

    def generation_settings(self) -> dict[str, float | int]:
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
