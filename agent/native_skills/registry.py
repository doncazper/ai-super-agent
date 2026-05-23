from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from agent.native_skills.loader import default_manifest_dirs, discover_manifest_files, load_manifests
from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.validator import known_capabilities_from_config, validate_manifest


class NativeSkillRegistry:
    def __init__(self, project_root: str | Path = ".", manifest_dirs: list[str | Path] | None = None) -> None:
        self.project_root = Path(project_root)
        self.manifest_dirs = manifest_dirs
        self._manifests: list[NativeSkillManifest] | None = None

    def manifests(self) -> list[NativeSkillManifest]:
        if self._manifests is None:
            self._manifests = load_manifests(self.project_root, self.manifest_dirs)
        return list(self._manifests)

    def list(self) -> list[dict[str, Any]]:
        return [
            {
                "skill_id": manifest.skill_id,
                "name": manifest.name,
                "category": manifest.category,
                "version": manifest.version,
                "status": manifest.status,
                "maturity_level": manifest.maturity_level,
                "risk_level": manifest.risk_level,
                "trust_level": manifest.trust_level,
                "approval_required": manifest.approval_required,
                "docs_path": manifest.docs_path,
            }
            for manifest in sorted(self.manifests(), key=lambda item: item.skill_id)
        ]

    def show(self, skill_id: str) -> dict[str, Any] | None:
        for manifest in self.manifests():
            if manifest.skill_id == skill_id:
                data = manifest.to_dict()
                data.pop("raw", None)
                return data
        return None

    def validate_all(self, capability_path: str | Path = "config/capabilities.yaml") -> dict[str, Any]:
        known = known_capabilities_from_config(self.project_root / capability_path)
        results = [validate_manifest(manifest, known).to_dict() for manifest in self.manifests()]
        return {
            "status": "ok" if all(result["valid"] for result in results) else "error",
            "manifest_count": len(results),
            "results": results,
        }

    def doctor(self, capability_path: str | Path = "config/capabilities.yaml") -> dict[str, Any]:
        files = discover_manifest_files(self.project_root, self.manifest_dirs)
        validation = self.validate_all(capability_path)
        manifests = self.manifests()
        personal_disabled = [
            manifest.skill_id
            for manifest in manifests
            if manifest.trust_level in {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"} and manifest.status == "disabled"
        ]
        return {
            "status": validation["status"],
            "manifest_dirs": [str(path) for path in (self.manifest_dirs or default_manifest_dirs(self.project_root))],
            "manifest_files": [str(path) for path in files],
            "manifest_count": len(manifests),
            "available_count": sum(1 for manifest in manifests if manifest.status == "available"),
            "disabled_count": sum(1 for manifest in manifests if manifest.status == "disabled"),
            "personal_disabled": personal_disabled,
            "validation": validation,
            "execution_model": "metadata_only; native skill tools must execute through ToolBroker",
        }


def registry_report(project_root: str | Path = ".") -> dict[str, Any]:
    registry = NativeSkillRegistry(project_root)
    return {"skills": registry.list(), "validation": registry.validate_all()}
