from __future__ import annotations

import sys
from pathlib import Path

from agent.native_skills.compatibility import compatibility_matrix, compatibility_record, platform_matrix
from agent.native_skills.manifest import manifest_from_mapping
from agent.native_skills.registry import NativeSkillRegistry
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


def manifest(**overrides: object):
    return manifest_from_mapping(manifest_data(**overrides))


def test_compatibility_computed_from_manifest_dependencies(monkeypatch) -> None:
    monkeypatch.setenv("DEMO_TOKEN", "set")
    record = compatibility_record(
        manifest(
            skill_id="researcher",
            category="research",
            required_platforms=["any"],
            required_env=["DEMO_TOKEN"],
            required_binaries=[],
            required_connectors=["web"],
            required_capabilities=["web.search"],
            network_behavior="public_web",
            required_model_features=["tool_calls"],
            dogfood_suite="native_skills",
        ),
        current_platform="linux",
    )

    assert record.status == "supported"
    assert record.network_required is True
    assert record.model_tool_call_support_required is True
    assert record.required_providers == ["web"]
    assert record.dogfood_suite_available is True


def test_macos_only_skill_unsupported_on_windows() -> None:
    record = compatibility_record(manifest(required_platforms=["macos"]), current_platform="windows")

    assert record.status == "unsupported"
    assert record.platforms["macos"] == "supported"
    assert record.platforms["windows"] == "unsupported"


def test_windows_only_skill_unsupported_on_macos() -> None:
    record = compatibility_record(manifest(required_platforms=["windows"]), current_platform="macos")

    assert record.status == "unsupported"
    assert record.platforms["windows"] == "supported"
    assert record.platforms["macos"] == "unsupported"


def test_missing_binary_returns_requires_setup(monkeypatch) -> None:
    monkeypatch.setattr("agent.native_skills.compatibility.shutil.which", lambda name: None)
    record = compatibility_record(manifest(required_binaries=["definitely-missing-tool"]), current_platform="linux")

    assert record.status == "requires_setup"
    assert record.missing_binaries == ["definitely-missing-tool"]


def test_personal_data_skill_flagged() -> None:
    record = compatibility_record(
        manifest(
            skill_id="contacts_search",
            category="contacts",
            trust_level="LOCAL_PRIVATE_DATA",
            required_capabilities=["contacts.search"],
            approval_required=True,
            status="disabled",
        ),
        current_platform="linux",
    )

    assert record.status == "disabled"
    assert record.personal_data_required is True
    assert record.approval_required is True


def test_matrix_safe_on_all_oses(monkeypatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    matrix = compatibility_matrix([manifest(skill_id="demo")])

    assert matrix["status"] == "ok"
    assert matrix["current_platform"] == "linux"
    assert matrix["records"][0]["status"] == "supported"


def test_native_app_bridge_capability_is_planned() -> None:
    record = compatibility_record(
        manifest(skill_id="bridge", required_capabilities=["app_bridge.status"], required_platforms=["any"]),
        current_platform="macos",
    )

    assert record.native_app_bridge_required is True
    assert record.status == "planned"
    assert record.runtimes["cli_only"] == "unsupported"


def test_platform_matrix_rows() -> None:
    matrix = platform_matrix([manifest(skill_id="demo", category="security")])

    assert matrix["status"] == "ok"
    assert matrix["rows"][0]["skill_id"] == "demo"
    assert "macos" in matrix["rows"][0]


def test_compatibility_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data(skill_id="doc", category="documents", risk_level="LOW"))
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["compatibility"], broker=None) == 0  # type: ignore[arg-type]
    assert _run_skills_command(["compatibility", "doc"], broker=None) == 0  # type: ignore[arg-type]
    assert _run_skills_command(["platform", "matrix"], broker=None) == 0  # type: ignore[arg-type]
    output = capsys.readouterr().out
    assert "metadata_only" in output


def test_registry_compatibility_methods(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="doc", category="documents", risk_level="LOW"))
    registry = NativeSkillRegistry(tmp_path)

    assert registry.compatibility()["status"] == "ok"
    assert registry.compatibility("doc")["record"]["skill_id"] == "doc"
    assert registry.skill_platform_matrix()["rows"][0]["skill_id"] == "doc"
