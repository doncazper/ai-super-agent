from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from agent.native_skills.precedence import duplicate_skill_ids, resolve_skill
from agent.native_skills.roots import SkillRoot, default_skill_roots, scan_skill_roots
from smart_agent import _run_skills_command


def _root(roots: list[SkillRoot], root_id: str) -> SkillRoot:
    for root in roots:
        if root.root_id == root_id:
            return root
    raise AssertionError(f"missing root {root_id}")


def _write_skill(root_path: Path, folder: str, skill_id: str, script: bool = False) -> None:
    skill_dir = root_path / folder
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(f"skill_id: {skill_id}\n# {skill_id}\n", encoding="utf-8")
    if script:
        (skill_dir / "run.sh").write_text("exit 99\n", encoding="utf-8")


def test_default_roots_exist(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    root_ids = [root.root_id for root in roots]

    assert root_ids == [
        "workspace_skills",
        "project_skills",
        "personal_skills",
        "managed_skills",
        "bundled_native_skills",
        "reconstructed_skills",
        "experimental_skills",
    ]
    assert _root(roots, "experimental_skills").enabled is False
    assert _root(roots, "personal_skills").allow_shadowing is False


def test_missing_roots_handled_without_scan_failure(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)

    assert scan_skill_roots(roots) == []
    assert any(not Path(root.path).exists() for root in roots)


def test_disabled_roots_skipped(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    experimental = _root(roots, "experimental_skills")
    _write_skill(Path(experimental.path), "candidate", "experimental_demo")

    assert all(candidate.skill_id != "experimental_demo" for candidate in scan_skill_roots(roots))


def test_precedence_order_deterministic(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)

    assert [root.root_id for root in sorted(roots, key=lambda root: root.default_precedence)][:3] == [
        "workspace_skills",
        "project_skills",
        "personal_skills",
    ]


def test_duplicate_skill_ids_detected(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    _write_skill(Path(_root(roots, "workspace_skills").path), "demo", "shared_skill")
    _write_skill(Path(_root(roots, "project_skills").path), "demo", "shared_skill")

    duplicates = duplicate_skill_ids(scan_skill_roots(roots))

    assert "shared_skill" in duplicates
    assert len(duplicates["shared_skill"]) == 2


def test_experimental_root_does_not_shadow_trusted_native_by_default(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    experimental = _root(roots, "experimental_skills")
    enabled_experimental = replace(experimental, enabled=True)
    roots = [enabled_experimental if root.root_id == "experimental_skills" else root for root in roots]
    _write_skill(Path(_root(roots, "experimental_skills").path), "demo", "shared_skill")
    _write_skill(Path(_root(roots, "project_skills").path), "demo", "shared_skill")

    resolution = resolve_skill("shared_skill", scan_skill_roots(roots), roots)

    assert resolution.winning_skill is not None
    assert resolution.winning_skill.root_id == "project_skills"
    assert any("cannot shadow" in item or "untrusted" in item for item in resolution.diagnostics)


def test_explicit_shadowing_works_only_if_configured(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    workspace = _root(roots, "workspace_skills")
    _write_skill(Path(workspace.path), "demo", "shared_skill")
    _write_skill(Path(_root(roots, "project_skills").path), "demo", "shared_skill")

    blocked = resolve_skill("shared_skill", scan_skill_roots(roots), roots)
    assert blocked.winning_skill is not None
    assert blocked.winning_skill.root_id == "project_skills"

    allowed_workspace = replace(workspace, allow_shadowing=True, trusted=True)
    configured = [allowed_workspace if root.root_id == "workspace_skills" else root for root in roots]
    allowed = resolve_skill("shared_skill", scan_skill_roots(configured), configured)

    assert allowed.winning_skill is not None
    assert allowed.winning_skill.root_id == "workspace_skills"


def test_root_scan_does_not_execute_scripts(tmp_path: Path) -> None:
    roots = default_skill_roots(tmp_path)
    _write_skill(Path(_root(roots, "workspace_skills").path), "demo", "scripted_skill", script=True)

    candidates = scan_skill_roots(roots)

    assert candidates[0].skill_id == "scripted_skill"
    assert candidates[0].text_trust_level == "UNTRUSTED_DOCUMENT"


def test_skill_root_commands(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config").mkdir()
    (tmp_path / "config/capabilities.yaml").write_text("tools: {}\n", encoding="utf-8")

    assert _run_skills_command(["roots"], broker=None) == 0  # type: ignore[arg-type]
    roots = json.loads(capsys.readouterr().out)
    assert roots["text_trust_level"] == "UNTRUSTED_DOCUMENT"

    assert _run_skills_command(["precedence"], broker=None) == 0  # type: ignore[arg-type]
    precedence = json.loads(capsys.readouterr().out)
    assert precedence["scan_behavior"].startswith("metadata_only")

    assert _run_skills_command(["registry"], broker=None) == 0  # type: ignore[arg-type]
    registry = json.loads(capsys.readouterr().out)
    assert registry["status"] == "ok"

    assert _run_skills_command(["explain-root", "experimental_skills"], broker=None) == 0  # type: ignore[arg-type]
    explained = json.loads(capsys.readouterr().out)
    assert explained["root"]["enabled"] is False
