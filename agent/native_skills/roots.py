from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from agent.native_skills.scopes import SkillRootType, SkillTextTrust


@dataclass(frozen=True)
class SkillRoot:
    root_id: str
    root_type: str
    path: str
    enabled: bool
    trusted: bool
    default_precedence: int
    allow_shadowing: bool
    writable: bool
    source: str
    setup_hint: str
    docs_path: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["exists"] = Path(self.path).exists()
        return data


@dataclass(frozen=True)
class SkillCandidate:
    skill_id: str
    root_id: str
    path: str
    source_type: str
    trusted: bool
    status: str
    text_trust_level: str = SkillTextTrust.UNTRUSTED_DOCUMENT.value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def default_skill_roots(project_root: str | Path = ".") -> list[SkillRoot]:
    root = Path(project_root).resolve()
    home = Path.home()
    return [
        SkillRoot(
            root_id="workspace_skills",
            root_type=SkillRootType.WORKSPACE.value,
            path=str(root / "workspace" / "skills"),
            enabled=True,
            trusted=False,
            default_precedence=1,
            allow_shadowing=False,
            writable=True,
            source="workspace",
            setup_hint="Create workspace-local candidate skills under workspace/skills for review; they cannot shadow trusted native skills unless explicitly configured.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="project_skills",
            root_type=SkillRootType.PROJECT.value,
            path=str(root / "native_skills"),
            enabled=True,
            trusted=True,
            default_precedence=2,
            allow_shadowing=True,
            writable=True,
            source="project",
            setup_hint="Project-owned reviewed native skill manifests live under native_skills/.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="personal_skills",
            root_type=SkillRootType.PERSONAL.value,
            path=str(home / ".ai-super-agent" / "skills"),
            enabled=True,
            trusted=False,
            default_precedence=3,
            allow_shadowing=False,
            writable=True,
            source="user",
            setup_hint="Personal skills are candidate metadata only and cannot override bundled/project skills by default.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="managed_skills",
            root_type=SkillRootType.MANAGED.value,
            path=str(root / "managed_skills"),
            enabled=True,
            trusted=True,
            default_precedence=4,
            allow_shadowing=True,
            writable=False,
            source="managed",
            setup_hint="Managed skills require review/provenance before use; missing managed root is expected in local development.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="bundled_native_skills",
            root_type=SkillRootType.BUNDLED_NATIVE.value,
            path=str(root / "agent" / "native_skills" / "bundled"),
            enabled=True,
            trusted=True,
            default_precedence=5,
            allow_shadowing=False,
            writable=False,
            source="bundled",
            setup_hint="Bundled native skills are project-controlled and should not be silently shadowed by unreviewed roots.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="reconstructed_skills",
            root_type=SkillRootType.RECONSTRUCTED.value,
            path=str(root / "docs" / "native_skills" / "reconstructed"),
            enabled=True,
            trusted=False,
            default_precedence=6,
            allow_shadowing=False,
            writable=False,
            source="reconstructed",
            setup_hint="Reconstructed skills are historical/speculative records and are not exact originals unless evidence says so.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
        SkillRoot(
            root_id="experimental_skills",
            root_type=SkillRootType.EXPERIMENTAL.value,
            path=str(root / "experimental_skills"),
            enabled=False,
            trusted=False,
            default_precedence=7,
            allow_shadowing=False,
            writable=True,
            source="experimental",
            setup_hint="Experimental skills are disabled by default and cannot shadow trusted native skills.",
            docs_path="docs/native_skills/SKILL_ROOTS_AND_SCOPES.md",
        ),
    ]


def enabled_roots(roots: list[SkillRoot]) -> list[SkillRoot]:
    return [root for root in sorted(roots, key=lambda item: item.default_precedence) if root.enabled]


def explain_root(root_id: str, project_root: str | Path = ".") -> dict[str, Any] | None:
    for root in default_skill_roots(project_root):
        if root.root_id == root_id:
            return root.to_dict()
    return None


def scan_skill_root(root: SkillRoot) -> list[SkillCandidate]:
    if not root.enabled:
        return []
    path = Path(root.path)
    if not path.exists() or not path.is_dir():
        return []
    candidates: list[SkillCandidate] = []
    for child in sorted(path.iterdir()):
        if child.is_dir():
            skill_file = child / "SKILL.md"
            if skill_file.exists():
                candidates.append(
                    SkillCandidate(
                        skill_id=_skill_id_from_skill_file(skill_file, child.name),
                        root_id=root.root_id,
                        path=str(skill_file),
                        source_type="skill_md",
                        trusted=root.trusted,
                        status="candidate" if not root.trusted else "available",
                    )
                )
        elif child.is_file() and child.suffix.lower() in {".yaml", ".yml"}:
            data = _safe_yaml(child)
            skill_id = str(data.get("skill_id") or child.stem) if isinstance(data, dict) else child.stem
            status = str(data.get("status") or ("available" if root.trusted else "candidate")) if isinstance(data, dict) else "candidate"
            candidates.append(
                SkillCandidate(
                    skill_id=skill_id,
                    root_id=root.root_id,
                    path=str(child),
                    source_type="manifest",
                    trusted=root.trusted,
                    status=status,
                )
            )
    return candidates


def scan_skill_roots(roots: list[SkillRoot]) -> list[SkillCandidate]:
    candidates: list[SkillCandidate] = []
    for root in enabled_roots(roots):
        candidates.extend(scan_skill_root(root))
    return candidates


def _skill_id_from_skill_file(path: Path, fallback: str) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[:40]:
        stripped = line.strip()
        if stripped.startswith("skill_id:"):
            return stripped.split(":", 1)[1].strip() or fallback
    return fallback


def _safe_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return dict(data) if isinstance(data, dict) else {}
