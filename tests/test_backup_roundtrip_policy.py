from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from agent.tools.backup.backup_tools import BackupManager
from tests.test_backup_restore import call, make_broker, payload, seed_project


def _rewrite_manifest(archive: Path, manifest: dict[str, object]) -> None:
    copied = dict(manifest)
    copied.pop("integrity_hash", None)
    encoded = json.dumps(copied, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["integrity_hash"] = sha256(encoded).hexdigest()
    (archive / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_backup_roundtrip_dry_run_is_brokered_and_read_only(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("backup.roundtrip", {"backup_dir": str(tmp_path / "backups"), "dry_run": True}))
    data = payload(result)

    assert result.allowed is True
    assert data["dry_run"] is True
    assert data["would_create_backup"] is False
    assert data["would_restore"] is False
    assert data["disposable_workspace_required"] is True
    assert not any((tmp_path / "backups").iterdir())


def test_backup_policy_check_lists_restore_guards(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")

    result = broker.execute(call("backup.policy_check"))
    data = payload(result)

    assert result.allowed is True
    assert data["valid"] is True
    assert any("CRITICAL approval reuse" in guard for guard in data["guards"])
    assert data["approval_gated_restore"] is True


def test_restore_check_verifies_hashes_before_restore(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))
    archive = Path(str(created["path"]))
    target = next((archive / "files").rglob("README.md"))
    target.write_text("tampered\n", encoding="utf-8")

    result = broker.execute(call("backup.restore_check", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is True
    assert data["valid"] is False
    assert data["would_restore"] is False
    assert any("hash mismatch" in problem for problem in data["problems"])


def test_restore_creates_pre_restore_copy_inside_disposable_workspace(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    seed_project(source)
    seed_project(target)
    created = BackupManager(source).create(backup_dir=str(tmp_path / "backups"))
    (target / "README.md").write_text("local changes before restore\n", encoding="utf-8")
    broker = make_broker(target, tmp_path / "audit.jsonl", auto_approve={"backup.restore"})

    result = broker.execute(call("backup.restore", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is True
    assert data["restored"] is True
    assert (target / "README.md").read_text(encoding="utf-8") == "Project README\n"
    assert (target / ".agent_restore_backups" / str(created["backup_id"]) / "README.md").read_text(encoding="utf-8") == "local changes before restore\n"


def test_restore_check_refuses_critical_approval_reuse(tmp_path: Path) -> None:
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    current_capabilities = Path("config/capabilities.yaml").read_text(encoding="utf-8")
    bad_capabilities = current_capabilities.replace("    approval_reuse_allowed: false\n", "    approval_reuse_allowed: true\n", 1)
    seed_project(source, capabilities_text=bad_capabilities)
    seed_project(target)
    created = BackupManager(source).create(backup_dir=str(tmp_path / "backups"))
    broker = make_broker(target, tmp_path / "audit.jsonl")

    result = broker.execute(call("backup.restore_check", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert result.allowed is True
    assert data["valid"] is False
    assert any("policy" in problem and "approval" in problem for problem in data["problems"])


def test_restore_check_refuses_unredacted_secret_material(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))
    archive = Path(str(created["path"]))
    target = next((archive / "files").rglob("README.md"))
    target.write_text("OPENAI_API_KEY=sk-thislooksrealenough123456\n", encoding="utf-8")
    manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        if entry["stored_path"].endswith("README.md"):
            entry["sha256"] = _sha256_file(target)
    _rewrite_manifest(archive, manifest)

    result = broker.execute(call("backup.restore_check", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert data["valid"] is False
    assert any("unredacted secret material" in problem for problem in data["problems"])


def test_restore_check_refuses_path_traversal(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    seed_project(project)
    broker = make_broker(project, tmp_path / "audit.jsonl")
    created = payload(broker.execute(call("backup.create", {"backup_dir": str(tmp_path / "backups")})))
    archive = Path(str(created["path"]))
    manifest = json.loads((archive / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"][0]["source_path"] = "../escape.md"
    _rewrite_manifest(archive, manifest)

    result = broker.execute(call("backup.restore_check", {"backup_id": created["backup_id"], "backup_dir": str(tmp_path / "backups")}))
    data = payload(result)

    assert data["valid"] is False
    assert any("path traversal" in problem for problem in data["problems"])
