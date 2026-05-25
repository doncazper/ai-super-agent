from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NativeSkillManifest:
    skill_id: str
    name: str
    description: str
    category: str
    version: str
    status: str
    maturity_level: str
    risk_level: str
    trust_level: str
    allowed_tools: list[str]
    required_capabilities: list[str]
    approval_required: bool | str
    memory_behavior: str
    audit_required: bool
    inputs_schema: dict[str, Any]
    outputs_schema: dict[str, Any]
    docs_path: str
    tests_path: str
    owner: str
    last_reviewed: str
    root_id: str = ""
    source: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    required_connectors: list[str] = field(default_factory=list)
    required_env: list[str] = field(default_factory=list)
    required_config: list[str] = field(default_factory=list)
    required_binaries: list[str] = field(default_factory=list)
    required_files: list[str] = field(default_factory=list)
    required_platforms: list[str] = field(default_factory=list)
    required_python: str = ""
    required_model_features: list[str] = field(default_factory=list)
    approval_reuse_allowed: bool | str = True
    network_behavior: str = "none"
    filesystem_behavior: str = "none"
    dogfood_suite: str = ""
    license: str = ""
    setup_hint: str = ""
    known_limitations: list[str] = field(default_factory=list)
    source_path: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data.get("raw"):
            data.pop("raw", None)
        return data


@dataclass(frozen=True)
class ManifestValidationResult:
    skill_id: str
    valid: bool
    errors: list[str]
    warnings: list[str]
    source_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def manifest_path_label(path: str | Path) -> str:
    try:
        return str(Path(path).resolve())
    except OSError:
        return str(path)
