from __future__ import annotations

import json
from pathlib import Path

import yaml

from agent.native_skills.lockfile import generate_lockfile_payload, verify_lockfile
from agent.native_skills.manifest import manifest_from_mapping
from agent.native_skills.provenance import provenance_record
from agent.native_skills.trust import trust_status_for_manifest
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


def test_provenance_record_validates() -> None:
    manifest = manifest_from_mapping(manifest_data())

    record = provenance_record(manifest)

    assert record.skill_id == "demo_skill"
    assert record.source_type == "native"
    assert record.license == "project-internal"


def test_unknown_source_warns() -> None:
    manifest = manifest_from_mapping(manifest_data(source="", provenance={}))

    record = provenance_record(manifest)

    assert "unknown source" in record.caveats
    assert trust_status_for_manifest(manifest) == "unknown"


def test_missing_license_warns() -> None:
    manifest = manifest_from_mapping(manifest_data(license=""))

    record = provenance_record(manifest)

    assert "missing license" in record.caveats


def test_lockfile_generated_from_fixture_manifests() -> None:
    manifest = manifest_from_mapping(manifest_data())

    payload = generate_lockfile_payload([manifest])

    assert payload["records"][0]["skill_id"] == "demo_skill"
    assert payload["records"][0]["manifest_hash"]
    assert payload["records"][0]["dependencies_hash"]


def test_lockfile_verify_passes_unchanged_fixture(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data())
    payload = generate_lockfile_payload([manifest])
    (tmp_path / "native_skills.lock").write_text(yaml.safe_dump(payload), encoding="utf-8")

    result = verify_lockfile(tmp_path, [manifest])

    assert result["status"] == "ok"
    assert result["changed"] == []


def test_lockfile_verify_detects_changed_manifest(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data())
    payload = generate_lockfile_payload([manifest])
    (tmp_path / "native_skills.lock").write_text(yaml.safe_dump(payload), encoding="utf-8")
    changed = manifest_from_mapping(manifest_data(description="Changed"))

    result = verify_lockfile(tmp_path, [changed])

    assert result["status"] == "changed"
    assert result["changed"] == ["demo_skill"]


def test_pinned_skill_cannot_be_silently_updated(tmp_path: Path) -> None:
    manifest = manifest_from_mapping(manifest_data(provenance={"source_type": "native", "review_status": "reviewed_local", "pinned": True}))
    payload = generate_lockfile_payload([manifest])
    (tmp_path / "native_skills.lock").write_text(yaml.safe_dump(payload), encoding="utf-8")
    changed = manifest_from_mapping(
        manifest_data(description="Changed", provenance={"source_type": "native", "review_status": "reviewed_local", "pinned": True})
    )

    result = verify_lockfile(tmp_path, [changed])

    assert result["status"] == "changed"
    assert "demo_skill" in result["changed"]


def test_candidate_skill_disabled_by_default() -> None:
    manifest = manifest_from_mapping(manifest_data(status="candidate", provenance={"source_type": "external"}))

    report = trust_status_for_manifest(manifest)

    assert report == "unreviewed_external"


def test_reconstructed_skill_labeled_correctly() -> None:
    manifest = manifest_from_mapping(manifest_data(source="reconstructed", provenance={"source_type": "reconstructed"}))

    record = provenance_record(manifest)

    assert "reconstructed skill is not claimed as exact original" in record.caveats


def test_provenance_lock_cli_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    write_project(tmp_path, manifest_data())
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["provenance", "demo_skill"], broker=None) == 0  # type: ignore[arg-type]
    provenance = json.loads(capsys.readouterr().out)
    assert provenance["provenance"]["skill_id"] == "demo_skill"

    assert _run_skills_command(["trust", "demo_skill"], broker=None) == 0  # type: ignore[arg-type]
    trust = json.loads(capsys.readouterr().out)
    assert trust["trust"]["trust_status"] == "trusted_native"

    assert _run_skills_command(["lock", "status"], broker=None) == 0  # type: ignore[arg-type]
    lock_status = json.loads(capsys.readouterr().out)
    assert lock_status["record_count"] == 1

    assert _run_skills_command(["lock", "verify"], broker=None) == 0  # type: ignore[arg-type]
    verify = json.loads(capsys.readouterr().out)
    assert verify["verification"]["status"] == "requires_setup"
