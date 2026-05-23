from __future__ import annotations

from pathlib import Path

from agent.native_skills.manifest import load_manifest_file
from agent.native_skills.models import NativeSkillManifest


MANIFEST_SUFFIXES = {".yaml", ".yml", ".json"}


def default_manifest_dirs(project_root: str | Path = ".") -> list[Path]:
    root = Path(project_root)
    return [root / "native_skills", root / "docs/native_skills/manifests"]


def discover_manifest_files(project_root: str | Path = ".", manifest_dirs: list[str | Path] | None = None) -> list[Path]:
    dirs = [Path(path) for path in manifest_dirs] if manifest_dirs is not None else default_manifest_dirs(project_root)
    files: list[Path] = []
    for directory in dirs:
        if not directory.exists() or not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in MANIFEST_SUFFIXES:
                files.append(path)
    return files


def load_manifests(project_root: str | Path = ".", manifest_dirs: list[str | Path] | None = None) -> list[NativeSkillManifest]:
    return [load_manifest_file(path) for path in discover_manifest_files(project_root, manifest_dirs)]
