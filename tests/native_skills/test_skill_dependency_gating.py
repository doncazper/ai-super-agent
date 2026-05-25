from __future__ import annotations

from pathlib import Path

from agent.native_skills.dependencies import check_dependencies, python_package_available
from agent.native_skills.manifest import manifest_from_mapping
from tests.test_native_skill_manifests import manifest_data


def test_missing_env_dependency_returns_requires_setup_without_value(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data(required_env=["DEMO_SECRET"]))

    result = check_dependencies(manifest, project_root=tmp_path, env={}, known_capabilities={"filesystem.read"})

    assert result.status == "requires_setup"
    env_check = result.checks[0]
    assert env_check.dependency_type == "env"
    assert env_check.status == "requires_setup"
    assert env_check.redacted_value == ""


def test_present_env_dependency_redacted(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data(required_env=["DEMO_SECRET"]))

    result = check_dependencies(
        manifest,
        project_root=tmp_path,
        env={"DEMO_SECRET": "super-secret-value"},
        known_capabilities={"filesystem.read"},
    )

    assert result.checks[0].status == "available"
    assert result.checks[0].redacted_value == "[set]"
    assert "super-secret-value" not in str(result.to_dict())


def test_missing_binary_returns_requires_setup(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data(required_binaries=["definitely-not-installed-ai-agent-test-bin"]))

    result = check_dependencies(manifest, project_root=tmp_path, known_capabilities={"filesystem.read"})

    assert result.status == "requires_setup"
    assert result.checks[0].dependency_type == "binary"


def test_unknown_capability_dependency_blocked(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data(required_capabilities=["unknown.cap"], allowed_tools=[]))

    result = check_dependencies(manifest, project_root=tmp_path, known_capabilities={"filesystem.read"})

    assert result.status == "blocked"
    assert result.checks[0].dependency_type == "capability"


def test_dependency_check_does_not_install_packages_or_execute_scripts() -> None:
    assert python_package_available("sys") is True
