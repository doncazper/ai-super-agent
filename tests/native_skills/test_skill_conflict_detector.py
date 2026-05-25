from __future__ import annotations

import json
from pathlib import Path

from agent.native_skills.conflicts import detect_skill_conflicts, explain_skill_conflict
from agent.native_skills.manifest import manifest_from_mapping
from agent.native_skills.registry import NativeSkillRegistry
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


def manifest(**overrides: object):
    return manifest_from_mapping(manifest_data(**overrides))


def conflict_types(report: dict[str, object]) -> set[str]:
    return {str(item["conflict_type"]) for item in report["conflicts"]}  # type: ignore[index]


def test_duplicate_skill_id_conflict_detected() -> None:
    report = detect_skill_conflicts(
        [
            manifest(skill_id="dup", root_id="project_skills", source_path="native_skills/dup.yaml"),
            manifest(skill_id="dup", root_id="workspace_skills", source_path="workspace/skills/dup/SKILL.md"),
        ],
        precedence={},
    )

    assert "duplicate_skill_id" in conflict_types(report)
    assert report["safe_to_continue"] is False


def test_same_command_conflict_detected() -> None:
    report = detect_skill_conflicts(
        [
            manifest(skill_id="one", commands=["python smart_agent.py skills demo"]),
            manifest(skill_id="two", commands=["python smart_agent.py skills demo"]),
        ],
        precedence={},
    )

    assert "same_command" in conflict_types(report)


def test_same_capability_claim_conflict_detected() -> None:
    report = detect_skill_conflicts(
        [
            manifest(skill_id="one", required_capabilities=["filesystem.read"]),
            manifest(skill_id="two", required_capabilities=["filesystem.read"]),
        ],
        precedence={},
    )

    assert "same_capability_claim" in conflict_types(report)


def test_policy_conflicts_detected_for_critical_approval_reuse() -> None:
    report = detect_skill_conflicts(
        [
            manifest(
                skill_id="critical_skill",
                risk_level="CRITICAL",
                approval_required=True,
                approval_reuse_allowed=True,
            )
        ],
        precedence={},
    )

    assert "risk_policy_mismatch" in conflict_types(report)
    assert report["safe_to_continue"] is False


def test_high_risk_skill_without_approval_detected() -> None:
    report = detect_skill_conflicts(
        [manifest(skill_id="high_skill", risk_level="HIGH", approval_required=False)],
        precedence={},
    )

    assert "approval_policy_mismatch" in conflict_types(report)


def test_personal_data_memory_policy_mismatch_detected() -> None:
    report = detect_skill_conflicts(
        [
            manifest(
                skill_id="contact_skill",
                category="contacts",
                risk_level="HIGH",
                trust_level="LOCAL_PRIVATE_DATA",
                approval_required=True,
                memory_behavior="store_full_content",
                status="disabled",
            )
        ],
        precedence={},
    )

    assert "memory_policy_mismatch" in conflict_types(report)


def test_missing_docs_and_tests_are_reported() -> None:
    report = detect_skill_conflicts(
        [manifest(skill_id="undocumented", docs_path="", tests_path="")],
        precedence={},
    )

    assert {"docs_missing", "tests_missing"}.issubset(conflict_types(report))


def test_dependency_provider_and_platform_conflicts_are_metadata_only(monkeypatch) -> None:
    monkeypatch.setattr("agent.native_skills.compatibility.shutil.which", lambda name: None)
    report = detect_skill_conflicts(
        [
            manifest(
                skill_id="reddit_skill",
                required_binaries=["missing-binary"],
                required_platforms=["windows"],
                required_capabilities=["reddit.search"],
                network_behavior="public_web",
            )
        ],
        precedence={},
        current_platform="linux",
        env={"REDDIT_ENABLED": "false"},
    )

    types = conflict_types(report)
    assert "dependency_missing" in types
    assert "provider_disabled" in types
    assert "platform_incompatible" in types
    assert report["execution_model"].startswith("metadata_only")


def test_precedence_conflict_reports_unreviewed_shadowing(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="shadowed", root_id="project_skills"))
    skill_dir = tmp_path / "workspace" / "skills" / "shadowed"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("skill_id: shadowed\n# Candidate\n", encoding="utf-8")

    registry = NativeSkillRegistry(tmp_path)
    report = registry.conflicts()

    assert "duplicate_skill_id" in conflict_types(report)
    assert any(
        item["conflict_type"] in {"unsafe_shadowing", "unreviewed_overrides_reviewed"}
        for item in report["conflicts"]
    )


def test_explain_conflict_finds_existing_conflict() -> None:
    report = detect_skill_conflicts(
        [
            manifest(skill_id="one", commands=["python smart_agent.py demo"]),
            manifest(skill_id="two", commands=["python smart_agent.py demo"]),
        ],
        precedence={},
    )
    conflict_id = report["conflicts"][0]["conflict_id"]  # type: ignore[index]

    explained = explain_skill_conflict(
        [
            manifest(skill_id="one", commands=["python smart_agent.py demo"]),
            manifest(skill_id="two", commands=["python smart_agent.py demo"]),
        ],
        str(conflict_id),
        precedence={},
    )

    assert explained["status"] == "ok"
    assert explained["conflict"]["conflict_id"] == conflict_id  # type: ignore[index]


def test_explain_conflict_not_found_is_structured() -> None:
    explained = explain_skill_conflict([manifest(skill_id="one")], "missing", precedence={})

    assert explained["status"] == "error"
    assert explained["error"] == "native skill conflict not found"


def test_conflict_commands_emit_json(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data(skill_id="doc", category="documents", risk_level="LOW"))
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["conflicts"], broker=None) == 0  # type: ignore[arg-type]
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ok"

    assert _run_skills_command(["conflicts", "--json"], broker=None) == 0  # type: ignore[arg-type]
    json_report = json.loads(capsys.readouterr().out)
    assert json_report["execution_model"].startswith("metadata_only")

    assert _run_skills_command(["explain-conflict", "missing"], broker=None) == 2  # type: ignore[arg-type]
    missing = json.loads(capsys.readouterr().out)
    assert missing["status"] == "error"
