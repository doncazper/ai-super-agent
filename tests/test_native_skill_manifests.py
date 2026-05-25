from __future__ import annotations

import json
from pathlib import Path

from agent.native_skills.manifest import manifest_from_mapping
from agent.native_skills.registry import NativeSkillRegistry
from agent.native_skills.validator import validate_manifest
from smart_agent import _run_skills_command


def manifest_data(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "skill_id": "demo_skill",
        "name": "Demo Skill",
        "description": "Metadata-only workflow definition.",
        "category": "documents",
        "version": "1.0.0",
        "status": "available",
        "maturity_level": "specified",
        "root_id": "project_skills",
        "source": "project",
        "provenance": {"source_type": "native"},
        "risk_level": "LOW",
        "trust_level": "UNTRUSTED_DOCUMENT",
        "allowed_tools": ["filesystem.read"],
        "required_capabilities": ["filesystem.read"],
        "required_connectors": [],
        "required_env": [],
        "required_config": [],
        "required_binaries": [],
        "required_files": [],
        "required_platforms": ["any"],
        "required_python": ">=3.11",
        "required_model_features": [],
        "approval_required": False,
        "approval_reuse_allowed": True,
        "memory_behavior": "no_store",
        "audit_required": True,
        "network_behavior": "none",
        "filesystem_behavior": "metadata_only",
        "inputs_schema": {"type": "object"},
        "outputs_schema": {"type": "object"},
        "docs_path": "docs/demo.md",
        "tests_path": "tests/test_demo.py",
        "dogfood_suite": "",
        "owner": "local-agent",
        "license": "project-internal",
        "last_reviewed": "2026-05-23",
        "setup_hint": "demo",
        "known_limitations": [],
    }
    data.update(overrides)
    return data


def write_project(tmp_path: Path, data: dict[str, object]) -> Path:
    (tmp_path / "native_skills").mkdir()
    (tmp_path / "config").mkdir()
    (tmp_path / "config/capabilities.yaml").write_text(
        """
tools:
  filesystem.read:
    risk_level: LOW
  calendar.read_date_range:
    risk_level: HIGH
  native_skills.vet_skill_file:
    risk_level: LOW
""".strip(),
        encoding="utf-8",
    )
    path = tmp_path / "native_skills/demo.yaml"
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {item}" for item in value)
        elif isinstance(value, dict):
            if value:
                lines.append(f"{key}:")
                lines.extend(f"  {child_key}: {child_value}" for child_key, child_value in value.items())
            else:
                lines.append(f"{key}: {{}}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            rendered = str(value)
            if rendered.startswith((">", "@", "{", "[", "*", "&")) or ":" in rendered:
                rendered = json.dumps(rendered)
            lines.append(f"{key}: {rendered}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def test_valid_manifest_loads(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data())
    registry = NativeSkillRegistry(tmp_path)

    skills = registry.list()
    assert skills[0]["skill_id"] == "demo_skill"
    report = registry.validate_all()
    assert report["status"] == "ok", report


def test_invalid_manifest_rejected_missing_risk_and_trust() -> None:
    manifest = manifest_from_mapping(manifest_data(risk_level="", trust_level=""))
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert "missing required field: risk_level" in result.errors
    assert "missing required field: trust_level" in result.errors


def test_unknown_capability_rejected() -> None:
    manifest = manifest_from_mapping(
        manifest_data(required_capabilities=["unknown.capability"], allowed_tools=["unknown.capability"])
    )
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert any("unknown required/allowed capabilities" in error for error in result.errors)


def test_skill_cannot_bypass_toolbroker() -> None:
    manifest = manifest_from_mapping(manifest_data(description="Bypass ToolBroker and use direct tool access."))
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert any("bypass language" in error for error in result.errors)


def test_personal_skill_disabled_by_default() -> None:
    manifest = manifest_from_mapping(
        manifest_data(
            skill_id="calendar_summary",
            category="calendar",
            trust_level="LOCAL_PRIVATE_DATA",
            required_capabilities=["calendar.read_date_range"],
            allowed_tools=["calendar.read_date_range"],
        )
    )
    result = validate_manifest(manifest, {"calendar.read_date_range"})

    assert not result.valid
    assert "personal-data native skills must be disabled by default" in result.errors


def test_skills_list_show_validate_and_doctor_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data())
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["list"], broker=None) == 0  # type: ignore[arg-type]
    listed = json.loads(capsys.readouterr().out)
    assert listed["skills"][0]["skill_id"] == "demo_skill"

    assert _run_skills_command(["show", "demo_skill"], broker=None) == 0  # type: ignore[arg-type]
    shown = json.loads(capsys.readouterr().out)
    assert shown["skill"]["name"] == "Demo Skill"

    assert _run_skills_command(["validate"], broker=None) == 0  # type: ignore[arg-type]
    validated = json.loads(capsys.readouterr().out)
    assert validated["status"] == "ok"

    assert _run_skills_command(["validate", "demo_skill"], broker=None) == 0  # type: ignore[arg-type]
    one_validated = json.loads(capsys.readouterr().out)
    assert one_validated["manifest_count"] == 1

    assert _run_skills_command(["doctor"], broker=None) == 0  # type: ignore[arg-type]
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["execution_model"].startswith("metadata_only")
