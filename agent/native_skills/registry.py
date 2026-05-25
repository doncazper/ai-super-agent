from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from agent.native_skills.loader import default_manifest_dirs, discover_manifest_files, load_manifests
from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.allowlists import allowed_skills_report, profile_report, profiles_report, validate_profile_report
from agent.native_skills.compatibility import compatibility_for_skill, compatibility_matrix, platform_matrix
from agent.native_skills.conflicts import detect_skill_conflicts, explain_skill_conflict
from agent.native_skills.dependencies import check_dependencies
from agent.native_skills.lockfile import generate_lockfile_payload, verify_lockfile
from agent.native_skills.precedence import precedence_report, resolve_skill
from agent.native_skills.provenance import provenance_record
from agent.native_skills.roots import default_skill_roots, explain_root, scan_skill_roots
from agent.native_skills.trust import trust_report
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

    def roots(self) -> list[dict[str, Any]]:
        return [root.to_dict() for root in default_skill_roots(self.project_root)]

    def explain_root(self, root_id: str) -> dict[str, Any] | None:
        return explain_root(root_id, self.project_root)

    def root_registry(self) -> dict[str, Any]:
        roots = default_skill_roots(self.project_root)
        return {
            "status": "ok",
            "roots": [root.to_dict() for root in roots],
            "scan_behavior": "lazy; root contents are not scanned until registry/precedence diagnostics request candidates",
            "text_trust_level": "UNTRUSTED_DOCUMENT",
        }

    def precedence(self, skill_id: str | None = None) -> dict[str, Any]:
        roots = default_skill_roots(self.project_root)
        candidates = scan_skill_roots(roots)
        if skill_id:
            return {
                "status": "ok",
                "resolution": resolve_skill(skill_id, candidates, roots).to_dict(),
                "scan_behavior": "metadata_only; no skill scripts executed",
            }
        return precedence_report(str(self.project_root))

    def show(self, skill_id: str) -> dict[str, Any] | None:
        for manifest in self.manifests():
            if manifest.skill_id == skill_id:
                data = manifest.to_dict()
                data.pop("raw", None)
                return data
        return None

    def validate_all(self, capability_path: str | Path = "config/capabilities.yaml", skill_id: str | None = None) -> dict[str, Any]:
        known = known_capabilities_from_config(self.project_root / capability_path)
        manifests = [manifest for manifest in self.manifests() if skill_id is None or manifest.skill_id == skill_id]
        results = [validate_manifest(manifest, known).to_dict() for manifest in manifests]
        return {
            "status": "ok" if all(result["valid"] for result in results) else "error",
            "manifest_count": len(results),
            "results": results,
        }

    def dependency_report(self, skill_id: str | None = None, capability_path: str | Path = "config/capabilities.yaml") -> dict[str, Any]:
        known = known_capabilities_from_config(self.project_root / capability_path)
        manifests = [manifest for manifest in self.manifests() if skill_id is None or manifest.skill_id == skill_id]
        results = [check_dependencies(manifest, project_root=self.project_root, known_capabilities=known).to_dict() for manifest in manifests]
        status = "ok" if all(result["status"] in {"available", "requires_setup"} for result in results) else "error"
        return {
            "status": status,
            "skill_id": skill_id or "all",
            "results": results,
            "execution_model": "dependency checks are detection-only; no installs, scripts, provider calls, or connector calls",
        }

    def provenance(self, skill_id: str) -> dict[str, Any]:
        manifest = self._manifest_by_id(skill_id)
        if manifest is None:
            return {"status": "error", "error": "native skill not found", "skill_id": skill_id}
        return {"status": "ok", "provenance": provenance_record(manifest).to_dict()}

    def trust(self, skill_id: str) -> dict[str, Any]:
        manifest = self._manifest_by_id(skill_id)
        if manifest is None:
            return {"status": "error", "error": "native skill not found", "skill_id": skill_id}
        return {"status": "ok", "trust": trust_report(manifest)}

    def profiles(self) -> dict[str, Any]:
        return profiles_report()

    def profile(self, profile_id: str) -> dict[str, Any]:
        return profile_report(profile_id)

    def profile_allowed(self, profile_id: str) -> dict[str, Any]:
        return allowed_skills_report(profile_id, self.manifests())

    def profile_validate(self, profile_id: str) -> dict[str, Any]:
        return validate_profile_report(profile_id, self.manifests())

    def compatibility(self, skill_id: str | None = None) -> dict[str, Any]:
        if skill_id:
            return compatibility_for_skill(self.manifests(), skill_id)
        return compatibility_matrix(self.manifests())

    def skill_platform_matrix(self) -> dict[str, Any]:
        return platform_matrix(self.manifests())

    def conflicts(self) -> dict[str, Any]:
        return detect_skill_conflicts(self.manifests(), precedence=self.precedence())

    def explain_conflict(self, conflict_id: str) -> dict[str, Any]:
        return explain_skill_conflict(self.manifests(), conflict_id, precedence=self.precedence())

    def test(self, skill_id: str | None = None, *, all_safe: bool = False) -> dict[str, Any]:
        from agent.native_skills.test_harness import run_skill_test

        return run_skill_test(self.project_root, skill_id=skill_id, all_safe=all_safe)

    def dogfood(self, skill_id: str) -> dict[str, Any]:
        from agent.native_skills.dogfood import native_skill_dogfood_plan

        return native_skill_dogfood_plan(self.project_root, skill_id)

    def docs_generate(self, *, dry_run: bool = True) -> dict[str, Any]:
        from agent.native_skills.docs_generator import generate_skill_catalog

        return generate_skill_catalog(self.project_root, dry_run=dry_run)

    def catalog(self) -> dict[str, Any]:
        from agent.native_skills.docs_generator import read_skill_catalog

        return read_skill_catalog(self.project_root)

    def docs_check(self) -> dict[str, Any]:
        from agent.native_skills.docs_generator import docs_check

        return docs_check(self.project_root)

    def lock_status(self) -> dict[str, Any]:
        payload = generate_lockfile_payload(self.manifests())
        return {
            "status": "ok",
            "lockfile": "native_skills.lock",
            "example_lockfile": "native_skills.lock.example",
            "record_count": len(payload["records"]),
            "records": payload["records"],
            "write_behavior": "status is read-only; no lockfile is written by this command",
        }

    def lock_verify(self) -> dict[str, Any]:
        return {"status": "ok", "verification": verify_lockfile(self.project_root, self.manifests())}

    def doctor(self, capability_path: str | Path = "config/capabilities.yaml", skill_id: str | None = None) -> dict[str, Any]:
        files = discover_manifest_files(self.project_root, self.manifest_dirs)
        validation = self.validate_all(capability_path, skill_id)
        dependencies = self.dependency_report(skill_id, capability_path)
        manifests = [manifest for manifest in self.manifests() if skill_id is None or manifest.skill_id == skill_id]
        personal_disabled = [
            manifest.skill_id
            for manifest in manifests
            if manifest.trust_level in {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"} and manifest.status == "disabled"
        ]
        return {
            "status": validation["status"],
            "manifest_dirs": [str(path) for path in (self.manifest_dirs or default_manifest_dirs(self.project_root))],
            "skill_roots": self.roots(),
            "manifest_files": [str(path) for path in files],
            "manifest_count": len(manifests),
            "available_count": sum(1 for manifest in manifests if manifest.status == "available"),
            "disabled_count": sum(1 for manifest in manifests if manifest.status == "disabled"),
            "personal_disabled": personal_disabled,
            "validation": validation,
            "dependencies": dependencies,
            "execution_model": "metadata_only; native skill tools must execute through ToolBroker",
        }

    def _manifest_by_id(self, skill_id: str) -> NativeSkillManifest | None:
        for manifest in self.manifests():
            if manifest.skill_id == skill_id:
                return manifest
        return None


def registry_report(project_root: str | Path = ".") -> dict[str, Any]:
    registry = NativeSkillRegistry(project_root)
    return {"skills": registry.list(), "validation": registry.validate_all()}
