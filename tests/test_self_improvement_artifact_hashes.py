from __future__ import annotations

import subprocess
from pathlib import Path

from agent.self_improvement.artifact_hashes import build_artifact_hash_report, file_hash_or_missing, sha256_text


def init_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    (path / "README.md").write_text("# Test\n", encoding="utf-8")
    (path / "docs").mkdir()
    (path / "docs/COMMAND_REGISTRY.md").write_text("# Commands\n", encoding="utf-8")
    (path / "config").mkdir()
    (path / "config/capabilities.yaml").write_text("tools: {}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "initial"],
        cwd=path,
        check=True,
        capture_output=True,
        text=True,
    )


def test_artifact_hash_report_is_deterministic_and_content_free(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)
    (project / "README.md").write_text("# Changed\napi_key=sk-testtoken1234567890\n", encoding="utf-8")

    first = build_artifact_hash_report(project, test_command_output="password=secret-value")
    second = build_artifact_hash_report(project, test_command_output="password=secret-value")

    assert first == second
    assert first["status"] == "ok"
    assert first["redacted"] is True
    assert first["git_diff_hash"] == second["git_diff_hash"]
    assert "README.md" in first["touched_file_hashes"]
    assert "secret-value" not in repr(first)
    assert "sk-testtoken" not in repr(first)


def test_file_hash_or_missing_handles_missing_files(tmp_path) -> None:
    assert file_hash_or_missing(tmp_path / "missing.txt") == "missing"
    path = tmp_path / "file.txt"
    path.write_text("hello", encoding="utf-8")
    assert file_hash_or_missing(path) == sha256_text("hello")


def test_report_hashes_command_registry_and_capability_manifest(tmp_path) -> None:
    project = tmp_path / "repo"
    init_repo(project)

    report = build_artifact_hash_report(project)

    assert report["command_registry_snapshot_hash"] != "missing"
    assert report["capability_manifest_hash"] != "missing"
    assert report["side_effects"] == "none; hash-only report"
