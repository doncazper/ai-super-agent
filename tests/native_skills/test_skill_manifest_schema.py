from __future__ import annotations

from agent.native_skills.manifest import REQUIRED_FIELDS, manifest_from_mapping
from agent.native_skills.validator import validate_manifest
from tests.test_native_skill_manifests import manifest_data


def test_manifest_schema_includes_hardening_fields() -> None:
    expected = {
        "root_id",
        "source",
        "provenance",
        "required_connectors",
        "required_env",
        "required_config",
        "required_binaries",
        "required_files",
        "required_platforms",
        "required_python",
        "required_model_features",
        "approval_reuse_allowed",
        "network_behavior",
        "filesystem_behavior",
        "dogfood_suite",
        "license",
        "setup_hint",
        "known_limitations",
    }

    assert expected.issubset(set(REQUIRED_FIELDS))


def test_missing_memory_behavior_fails() -> None:
    data = manifest_data()
    data.pop("memory_behavior")
    manifest = manifest_from_mapping(data)
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert "missing required field: memory_behavior" in result.errors


def test_critical_skill_requires_per_action_approval_and_no_reuse() -> None:
    manifest = manifest_from_mapping(
        manifest_data(risk_level="CRITICAL", approval_required=True, approval_reuse_allowed=True)
    )
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert "CRITICAL native skills require approval_required: per_action" in result.errors
    assert "CRITICAL native skills must set approval_reuse_allowed: false" in result.errors


def test_personal_data_skill_disabled_by_default_with_new_schema() -> None:
    manifest = manifest_from_mapping(
        manifest_data(
            skill_id="contacts_helper",
            category="contacts",
            trust_level="LOCAL_PRIVATE_DATA",
            status="available",
            required_capabilities=["filesystem.read"],
            allowed_tools=["filesystem.read"],
        )
    )
    result = validate_manifest(manifest, {"filesystem.read"})

    assert not result.valid
    assert "personal-data native skills must be disabled by default" in result.errors
