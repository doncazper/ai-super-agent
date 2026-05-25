from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from agent.native_skills.models import NativeSkillManifest, manifest_path_label


REQUIRED_FIELDS = (
    "skill_id",
    "name",
    "description",
    "category",
    "version",
    "status",
    "maturity_level",
    "root_id",
    "source",
    "provenance",
    "risk_level",
    "trust_level",
    "allowed_tools",
    "required_capabilities",
    "required_connectors",
    "required_env",
    "required_config",
    "required_binaries",
    "required_files",
    "required_platforms",
    "required_python",
    "required_model_features",
    "approval_required",
    "approval_reuse_allowed",
    "memory_behavior",
    "audit_required",
    "network_behavior",
    "filesystem_behavior",
    "inputs_schema",
    "outputs_schema",
    "docs_path",
    "tests_path",
    "dogfood_suite",
    "owner",
    "license",
    "last_reviewed",
    "setup_hint",
    "known_limitations",
)


def load_manifest_file(path: str | Path) -> NativeSkillManifest:
    source = Path(path)
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
        raise ValueError("native skill manifest root must be an object")
    return manifest_from_mapping(data, source_path=source)


def manifest_from_mapping(data: Mapping[str, Any], *, source_path: str | Path = "") -> NativeSkillManifest:
    return NativeSkillManifest(
        skill_id=str(data.get("skill_id") or "<unknown>"),
        name=str(data.get("name") or data.get("skill_id") or "<unknown>"),
        description=str(data.get("description") or ""),
        category=str(data.get("category") or ""),
        version=str(data.get("version") or ""),
        status=str(data.get("status") or ""),
        maturity_level=str(data.get("maturity_level") or ""),
        root_id=str(data.get("root_id") or ""),
        source=str(data.get("source") or ""),
        provenance=_dict(data.get("provenance")),
        risk_level=str(data.get("risk_level") or ""),
        trust_level=str(data.get("trust_level") or ""),
        allowed_tools=_string_list(data.get("allowed_tools")),
        required_capabilities=_string_list(data.get("required_capabilities")),
        required_connectors=_string_list(data.get("required_connectors")),
        required_env=_string_list(data.get("required_env")),
        required_config=_string_list(data.get("required_config")),
        required_binaries=_string_list(data.get("required_binaries")),
        required_files=_string_list(data.get("required_files")),
        required_platforms=_string_list(data.get("required_platforms")),
        required_python=str(data.get("required_python") or ""),
        required_model_features=_string_list(data.get("required_model_features")),
        approval_required=data.get("approval_required", ""),
        approval_reuse_allowed=data.get("approval_reuse_allowed", True),
        memory_behavior=str(data.get("memory_behavior") or ""),
        audit_required=data.get("audit_required", False),
        network_behavior=str(data.get("network_behavior") or ""),
        filesystem_behavior=str(data.get("filesystem_behavior") or ""),
        inputs_schema=_dict(data.get("inputs_schema")),
        outputs_schema=_dict(data.get("outputs_schema")),
        docs_path=str(data.get("docs_path") or ""),
        tests_path=str(data.get("tests_path") or ""),
        dogfood_suite=str(data.get("dogfood_suite") or ""),
        owner=str(data.get("owner") or ""),
        license=str(data.get("license") or ""),
        last_reviewed=str(data.get("last_reviewed") or ""),
        setup_hint=str(data.get("setup_hint") or ""),
        known_limitations=_string_list(data.get("known_limitations")),
        source_path=manifest_path_label(source_path),
        raw=dict(data),
    )


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}
