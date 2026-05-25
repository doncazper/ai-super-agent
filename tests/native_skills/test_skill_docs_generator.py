from __future__ import annotations

import json
from pathlib import Path

from agent.native_skills.docs_generator import CATALOG_PATH, docs_check, generate_skill_catalog
from agent.ui.command_registry import COMMANDS
from smart_agent import _run_skills_command
from tests.test_native_skill_manifests import manifest_data, write_project


def test_docs_generate_dry_run_writes_no_files(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="catalog_skill"))

    report = generate_skill_catalog(tmp_path, dry_run=True)

    assert report["status"] == "ok"
    assert report["dry_run"] is True
    assert not (tmp_path / CATALOG_PATH).exists()


def test_docs_generate_writes_catalog_from_fixture_manifest(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/demo.md").write_text("# Demo\n", encoding="utf-8")
    write_project(tmp_path, manifest_data(skill_id="catalog_skill", name="Catalog Skill"))

    report = generate_skill_catalog(tmp_path, dry_run=False)

    catalog = (tmp_path / CATALOG_PATH).read_text(encoding="utf-8")
    assert report["status"] == "ok"
    assert report["wrote"] is True
    assert "catalog_skill" in catalog
    assert "Catalog Skill" in catalog
    assert "<!-- BEGIN GENERATED NATIVE SKILL CATALOG -->" in catalog


def test_docs_generator_preserves_manual_notes(tmp_path: Path) -> None:
    (tmp_path / "docs/native_skills").mkdir(parents=True)
    (tmp_path / "docs/demo.md").write_text("# Demo\n", encoding="utf-8")
    (tmp_path / CATALOG_PATH).write_text(
        "\n".join(
            [
                "# Native Skill Catalog",
                "<!-- BEGIN MANUAL NOTES -->",
                "Reviewed caveat that must stay.",
                "<!-- END MANUAL NOTES -->",
            ]
        ),
        encoding="utf-8",
    )
    write_project(tmp_path, manifest_data(skill_id="manual_skill"))

    generate_skill_catalog(tmp_path, dry_run=False)

    catalog = (tmp_path / CATALOG_PATH).read_text(encoding="utf-8")
    assert "Reviewed caveat that must stay." in catalog
    assert "manual_skill" in catalog


def test_docs_check_reports_missing_docs(tmp_path: Path) -> None:
    write_project(tmp_path, manifest_data(skill_id="missing_docs_skill", docs_path="docs/missing.md"))

    report = docs_check(tmp_path)

    assert report["status"] == "requires_update"
    assert report["missing_docs"] == [{"skill_id": "missing_docs_skill", "docs_path": "docs/missing.md"}]


def test_deprecated_skill_is_included(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/demo.md").write_text("# Demo\n", encoding="utf-8")
    write_project(tmp_path, manifest_data(skill_id="old_skill", status="deprecated"))

    generate_skill_catalog(tmp_path, dry_run=False)

    catalog = (tmp_path / CATALOG_PATH).read_text(encoding="utf-8")
    assert "old_skill" in catalog
    assert "| deprecated |" in catalog


def test_maturity_is_copied_conservatively(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/demo.md").write_text("# Demo\n", encoding="utf-8")
    write_project(tmp_path, manifest_data(skill_id="maturity_skill", maturity_level="specified"))

    generate_skill_catalog(tmp_path, dry_run=False)

    catalog = (tmp_path / CATALOG_PATH).read_text(encoding="utf-8")
    assert "maturity_skill" in catalog
    assert "| specified |" in catalog
    assert "User-Ready" not in catalog


def test_docs_generator_cli_commands(tmp_path: Path, monkeypatch, capsys) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/demo.md").write_text("# Demo\n", encoding="utf-8")
    write_project(tmp_path, manifest_data(skill_id="cli_catalog_skill"))
    monkeypatch.chdir(tmp_path)

    assert _run_skills_command(["docs-generate", "--dry-run"], broker=None) == 0  # type: ignore[arg-type]
    dry_run = json.loads(capsys.readouterr().out)
    assert dry_run["dry_run"] is True
    assert not (tmp_path / CATALOG_PATH).exists()

    assert _run_skills_command(["docs-generate", "--write"], broker=None) == 0  # type: ignore[arg-type]
    written = json.loads(capsys.readouterr().out)
    assert written["dry_run"] is False
    assert (tmp_path / CATALOG_PATH).exists()

    assert _run_skills_command(["catalog"], broker=None) == 0  # type: ignore[arg-type]
    catalog = json.loads(capsys.readouterr().out)
    assert catalog["status"] == "ok"
    assert "cli_catalog_skill" in catalog["content"]

    assert _run_skills_command(["docs-check"], broker=None) == 0  # type: ignore[arg-type]
    check = json.loads(capsys.readouterr().out)
    assert check["status"] == "ok"


def test_command_registry_updated_for_skill_docs_generator() -> None:
    commands = {record.command for record in COMMANDS}

    assert "python smart_agent.py skills docs-generate --dry-run" in commands
    assert "python smart_agent.py skills docs-generate" in commands
    assert "python smart_agent.py skills catalog" in commands
    assert "python smart_agent.py skills docs-check" in commands
