from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.qa.fixtures import DEFAULT_FIXTURES, ensure_fixture_source_tree
from agent.qa.models import utc_now_iso


DEFAULT_WORKSPACE_DIR = Path("reports/qa/workspaces/current")


class DisposableWorkspaceError(ValueError):
    pass


@dataclass(frozen=True)
class DisposableWorkspaceStatus:
    status: str
    workspace_path: str
    exists: bool
    fixture_count: int
    created_at: str
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _workspace_root(project_root: str | Path = ".", workspace_path: str | Path | None = None) -> Path:
    project = Path(project_root).resolve()
    requested = Path(workspace_path) if workspace_path else DEFAULT_WORKSPACE_DIR
    root = (project / requested).resolve() if not requested.is_absolute() else requested.resolve()
    allowed = (project / "reports/qa/workspaces").resolve()
    if root != allowed and allowed not in root.parents:
        raise DisposableWorkspaceError("Disposable QA workspaces must live under reports/qa/workspaces/.")
    return root


def _assert_inside(root: Path, candidate: Path) -> None:
    resolved = candidate.resolve()
    if resolved != root and root not in resolved.parents:
        raise DisposableWorkspaceError("Path traversal outside disposable QA workspace was blocked.")


def init_disposable_workspace(
    *,
    project_root: str | Path = ".",
    workspace_path: str | Path | None = None,
    reset: bool = False,
) -> DisposableWorkspaceStatus:
    project = Path(project_root).resolve()
    root = _workspace_root(project, workspace_path)
    if reset and root.exists():
        clean_disposable_workspace(project_root=project, workspace_path=root)
    root.mkdir(parents=True, exist_ok=True)
    ensure_fixture_source_tree(project)
    fixture_count = 0
    for fixture in DEFAULT_FIXTURES:
        destination = root / fixture.relative_path
        _assert_inside(root, destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(fixture.content, encoding="utf-8")
        fixture_count += 1
    manifest = {
        "created_at": utc_now_iso(),
        "workspace_path": root.relative_to(project).as_posix(),
        "fixture_count": fixture_count,
        "contains_personal_data": False,
        "notes": ["Synthetic QA fixtures only.", "Safe to delete via qa sandbox clean."],
    }
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return sandbox_status(project_root=project, workspace_path=root)


def sandbox_status(*, project_root: str | Path = ".", workspace_path: str | Path | None = None) -> DisposableWorkspaceStatus:
    project = Path(project_root).resolve()
    root = _workspace_root(project, workspace_path)
    manifest_path = root / "manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    fixture_count = sum(1 for path in root.rglob("*") if path.is_file()) if root.exists() else 0
    return DisposableWorkspaceStatus(
        status="ready" if root.exists() else "missing",
        workspace_path=root.relative_to(project).as_posix(),
        exists=root.exists(),
        fixture_count=fixture_count,
        created_at=str(manifest.get("created_at", "")),
        notes=[
            "Disposable QA workspace is repo-local under reports/qa/workspaces/.",
            "Fixture content is fake and non-personal.",
        ],
    )


def clean_disposable_workspace(*, project_root: str | Path = ".", workspace_path: str | Path | None = None) -> DisposableWorkspaceStatus:
    project = Path(project_root).resolve()
    root = _workspace_root(project, workspace_path)
    allowed = (project / "reports/qa/workspaces").resolve()
    if root == allowed:
        raise DisposableWorkspaceError("Refusing to delete the workspaces parent directory.")
    _assert_inside(allowed, root)
    if root.exists():
        shutil.rmtree(root)
    return sandbox_status(project_root=project, workspace_path=root)


def require_workspace_path_inside(project_root: str | Path, candidate: str | Path) -> Path:
    root = _workspace_root(project_root)
    path = (root / candidate).resolve()
    _assert_inside(root, path)
    return path

