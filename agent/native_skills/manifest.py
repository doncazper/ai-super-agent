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
    "risk_level",
    "trust_level",
    "allowed_tools",
    "required_capabilities",
    "approval_required",
    "memory_behavior",
    "audit_required",
    "inputs_schema",
    "outputs_schema",
    "docs_path",
    "tests_path",
    "owner",
    "last_reviewed",
)


def load_manifest_file(path: str | Path) -> NativeSkillManifest:
    source = Path(path)
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    if not isinstance(data, Mapping):
        raise ValueError("native skill manifest root must be an object")
    return manifest_from_mapping(data, source_path=source)


def manifest_from_mapping(data: Mapping[str, Any], *, source_path: str | Path = "") -> NativeSkillManifest:
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        skill_id = str(data.get("skill_id") or "<unknown>")
        return NativeSkillManifest(
            skill_id=skill_id,
            name=str(data.get("name") or skill_id),
            description=str(data.get("description") or ""),
            category=str(data.get("category") or ""),
            version=str(data.get("version") or ""),
            status=str(data.get("status") or ""),
            maturity_level=str(data.get("maturity_level") or ""),
            risk_level=str(data.get("risk_level") or ""),
            trust_level=str(data.get("trust_level") or ""),
            allowed_tools=_string_list(data.get("allowed_tools")),
            required_capabilities=_string_list(data.get("required_capabilities")),
            approval_required=data.get("approval_required", ""),
            memory_behavior=str(data.get("memory_behavior") or ""),
            audit_required=bool(data.get("audit_required", False)),
            inputs_schema=_dict(data.get("inputs_schema")),
            outputs_schema=_dict(data.get("outputs_schema")),
            docs_path=str(data.get("docs_path") or ""),
            tests_path=str(data.get("tests_path") or ""),
            owner=str(data.get("owner") or ""),
            last_reviewed=str(data.get("last_reviewed") or ""),
            source_path=manifest_path_label(source_path),
            raw=dict(data),
        )
    return NativeSkillManifest(
        skill_id=str(data["skill_id"]),
        name=str(data["name"]),
        description=str(data["description"]),
        category=str(data["category"]),
        version=str(data["version"]),
        status=str(data["status"]),
        maturity_level=str(data["maturity_level"]),
        risk_level=str(data["risk_level"]),
        trust_level=str(data["trust_level"]),
        allowed_tools=_string_list(data["allowed_tools"]),
        required_capabilities=_string_list(data["required_capabilities"]),
        approval_required=data["approval_required"],
        memory_behavior=str(data["memory_behavior"]),
        audit_required=bool(data["audit_required"]),
        inputs_schema=_dict(data["inputs_schema"]),
        outputs_schema=_dict(data["outputs_schema"]),
        docs_path=str(data["docs_path"]),
        tests_path=str(data["tests_path"]),
        owner=str(data["owner"]),
        last_reviewed=str(data["last_reviewed"]),
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
