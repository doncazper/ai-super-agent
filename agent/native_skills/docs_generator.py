from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.profiles import default_skill_profiles
from agent.native_skills.registry import NativeSkillRegistry
from agent.ui.command_registry import COMMANDS


CATALOG_PATH = Path("docs/native_skills/SKILL_CATALOG.md")
GENERATED_START = "<!-- BEGIN GENERATED NATIVE SKILL CATALOG -->"
GENERATED_END = "<!-- END GENERATED NATIVE SKILL CATALOG -->"
MANUAL_START = "<!-- BEGIN MANUAL NOTES -->"
MANUAL_END = "<!-- END MANUAL NOTES -->"
DEFAULT_MANUAL_NOTES = "Add reviewed manual notes here. Do not edit the generated section by hand."


@dataclass(frozen=True)
class SkillCatalogRecord:
    skill_id: str
    name: str
    description: str
    category: str
    status: str
    maturity: str
    risk_level: str
    trust_level: str
    profile_visibility: str
    dependencies: str
    setup_hints: str
    compatibility: str
    test_status: str
    dogfood_status: str
    provenance_trust: str
    lock_status: str
    docs_path: str
    commands: str
    known_limitations: str

    def to_dict(self) -> dict[str, str]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "maturity": self.maturity,
            "risk_level": self.risk_level,
            "trust_level": self.trust_level,
            "profile_visibility": self.profile_visibility,
            "dependencies": self.dependencies,
            "setup_hints": self.setup_hints,
            "compatibility": self.compatibility,
            "test_status": self.test_status,
            "dogfood_status": self.dogfood_status,
            "provenance_trust": self.provenance_trust,
            "lock_status": self.lock_status,
            "docs_path": self.docs_path,
            "commands": self.commands,
            "known_limitations": self.known_limitations,
        }


def generate_skill_catalog(project_root: str | Path = ".", *, dry_run: bool = True) -> dict[str, Any]:
    root = Path(project_root)
    registry = NativeSkillRegistry(root)
    rendered = render_catalog(root, registry)
    target = root / CATALOG_PATH
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    changed = existing != rendered
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    check = docs_check(project_root, rendered_catalog=rendered)
    return {
        "status": "ok",
        "dry_run": dry_run,
        "catalog_path": str(CATALOG_PATH),
        "skill_count": len(registry.manifests()),
        "changed": changed,
        "would_write": changed if dry_run else False,
        "wrote": False if dry_run else changed,
        "missing_docs": check["missing_docs"],
        "stale": check["stale"],
        "execution_model": "metadata_only; no skills, external scripts, package managers, providers, connectors, or plugin runtimes executed",
    }


def read_skill_catalog(project_root: str | Path = ".") -> dict[str, Any]:
    root = Path(project_root)
    target = root / CATALOG_PATH
    if not target.exists():
        return {
            "status": "requires_setup",
            "catalog_path": str(CATALOG_PATH),
            "error": "native skill catalog has not been generated",
            "setup_hint": "Run `python smart_agent.py skills docs-generate --write` after reviewing the dry-run output.",
        }
    return {
        "status": "ok",
        "catalog_path": str(CATALOG_PATH),
        "content": target.read_text(encoding="utf-8"),
        "execution_model": "read-only catalog display; no skill execution",
    }


def docs_check(project_root: str | Path = ".", *, rendered_catalog: str | None = None) -> dict[str, Any]:
    root = Path(project_root)
    registry = NativeSkillRegistry(root)
    rendered = rendered_catalog if rendered_catalog is not None else render_catalog(root, registry)
    target = root / CATALOG_PATH
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    missing_docs = _missing_docs(root, registry.manifests())
    stale = not target.exists() or existing != rendered
    problems: list[str] = []
    if stale:
        problems.append("catalog is missing or out of date")
    if missing_docs:
        problems.append("one or more skills reference missing docs")
    return {
        "status": "ok" if not problems else "requires_update",
        "catalog_path": str(CATALOG_PATH),
        "skill_count": len(registry.manifests()),
        "stale": stale,
        "missing_docs": missing_docs,
        "problems": problems,
        "execution_model": "metadata_only; docs check does not execute skills or write files",
    }


def render_catalog(project_root: str | Path, registry: NativeSkillRegistry | None = None) -> str:
    root = Path(project_root)
    registry = registry or NativeSkillRegistry(root)
    target = root / CATALOG_PATH
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    manual_notes = _extract_manual_notes(existing)
    records = catalog_records(root, registry)
    return "\n".join(
        [
            "# Native Skill Catalog",
            "",
            "This catalog is generated from reviewed native skill manifests, command registry metadata, compatibility diagnostics, profile visibility, provenance/trust metadata, lockfile verification, tests, dogfood declarations, and docs paths.",
            "",
            "The generated section is deterministic and should be refreshed with `python smart_agent.py skills docs-generate --write` after manifest or command-registry changes. It does not execute skills, external scripts, package managers, providers, connectors, or plugin runtimes.",
            "",
            MANUAL_START,
            manual_notes,
            MANUAL_END,
            "",
            GENERATED_START,
            "",
            "## Summary",
            "",
            f"- Skill count: {len(records)}",
            "- Source: native skill manifests plus local metadata only",
            "- Maturity behavior: copied from manifests; never inferred or upgraded by the generator",
            "- Safety behavior: generated docs are advisory metadata and do not enable, install, or execute skills",
            "",
            "## Skills",
            "",
            _render_records_table(records),
            "",
            "## Missing Docs",
            "",
            _render_missing_docs(_missing_docs(root, registry.manifests())),
            "",
            GENERATED_END,
            "",
        ]
    )


def catalog_records(project_root: str | Path, registry: NativeSkillRegistry | None = None) -> list[SkillCatalogRecord]:
    root = Path(project_root)
    registry = registry or NativeSkillRegistry(root)
    compatibility = registry.compatibility()
    compatibility_by_id = {record["skill_id"]: record for record in compatibility.get("records", [])}
    lock_verify = registry.lock_verify().get("verification", {})
    changed = set(lock_verify.get("changed", []))
    missing = set(lock_verify.get("missing", []))
    profile_visibility = _profile_visibility(registry)
    command_map = _command_map(registry.manifests())
    return [
        _catalog_record_for_manifest(
            root,
            manifest,
            compatibility_by_id.get(manifest.skill_id, {}),
            profile_visibility.get(manifest.skill_id, []),
            _lock_status(manifest.skill_id, changed, missing, lock_verify.get("status", "unknown")),
            command_map,
        )
        for manifest in sorted(registry.manifests(), key=lambda item: item.skill_id)
    ]


def _catalog_record_for_manifest(
    root: Path,
    manifest: NativeSkillManifest,
    compatibility: dict[str, Any],
    visible_profiles: list[str],
    lock_status: str,
    command_map: dict[str, list[str]],
) -> SkillCatalogRecord:
    dependencies = _join_or_none(
        [
            *[f"capability:{item}" for item in manifest.required_capabilities],
            *[f"connector:{item}" for item in manifest.required_connectors],
            *[f"env:{item}" for item in manifest.required_env],
            *[f"config:{item}" for item in manifest.required_config],
            *[f"binary:{item}" for item in manifest.required_binaries],
            *[f"file:{item}" for item in manifest.required_files],
            *[f"platform:{item}" for item in manifest.required_platforms],
        ]
    )
    compatibility_summary = _compatibility_summary(compatibility)
    provenance = manifest.provenance if isinstance(manifest.provenance, dict) else {}
    provenance_trust = _join_or_none(
        [
            f"source:{provenance.get('source_type') or manifest.source or 'unknown'}",
            f"review:{provenance.get('review_status') or 'unknown'}",
            f"trust:{manifest.trust_level}",
        ]
    )
    return SkillCatalogRecord(
        skill_id=manifest.skill_id,
        name=manifest.name,
        description=manifest.description,
        category=manifest.category,
        status=manifest.status,
        maturity=manifest.maturity_level or "unspecified",
        risk_level=manifest.risk_level,
        trust_level=manifest.trust_level,
        profile_visibility=_join_or_none(visible_profiles),
        dependencies=dependencies,
        setup_hints=manifest.setup_hint or "none",
        compatibility=compatibility_summary,
        test_status=_path_status(root, manifest.tests_path, "test"),
        dogfood_status=_dogfood_status(root, manifest.dogfood_suite),
        provenance_trust=provenance_trust,
        lock_status=lock_status,
        docs_path=manifest.docs_path or "missing",
        commands=_join_or_none(command_map.get(manifest.skill_id, [])),
        known_limitations=_join_or_none(manifest.known_limitations),
    )


def _render_records_table(records: list[SkillCatalogRecord]) -> str:
    headers = [
        "Skill ID",
        "Name",
        "Description",
        "Category",
        "Status",
        "Maturity",
        "Risk",
        "Trust",
        "Profile visibility",
        "Dependencies",
        "Setup hints",
        "Compatibility",
        "Test status",
        "Dogfood status",
        "Provenance/trust",
        "Lock status",
        "Docs path",
        "Commands",
        "Known limitations",
    ]
    rows = [
        [
            record.skill_id,
            record.name,
            record.description,
            record.category,
            record.status,
            record.maturity,
            record.risk_level,
            record.trust_level,
            record.profile_visibility,
            record.dependencies,
            record.setup_hints,
            record.compatibility,
            record.test_status,
            record.dogfood_status,
            record.provenance_trust,
            record.lock_status,
            record.docs_path,
            record.commands,
            record.known_limitations,
        ]
        for record in records
    ]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(_cell(value) for value in row) + " |" for row in rows)
    return "\n".join(lines)


def _render_missing_docs(missing_docs: list[dict[str, str]]) -> str:
    if not missing_docs:
        return "No missing docs detected."
    lines = ["| Skill ID | Docs path |", "|---|---|"]
    lines.extend(f"| {_cell(item['skill_id'])} | {_cell(item['docs_path'])} |" for item in missing_docs)
    return "\n".join(lines)


def _missing_docs(root: Path, manifests: list[NativeSkillManifest]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for manifest in sorted(manifests, key=lambda item: item.skill_id):
        if not manifest.docs_path or not (root / manifest.docs_path).exists():
            missing.append({"skill_id": manifest.skill_id, "docs_path": manifest.docs_path or "<missing>"})
    return missing


def _path_status(root: Path, path_value: str, label: str) -> str:
    if not path_value:
        return f"not_declared:{label}"
    return f"present:{path_value}" if (root / path_value).exists() else f"missing:{path_value}"


def _dogfood_status(root: Path, suite: str) -> str:
    if not suite:
        return "not_declared"
    path = root / "dogfood_suites" / f"{suite}.yaml"
    return f"present:{suite}" if path.exists() else f"missing:{suite}"


def _compatibility_summary(record: dict[str, Any]) -> str:
    if not record:
        return "unknown"
    parts = [f"status:{record.get('status', 'unknown')}"]
    if record.get("required_platform_capabilities"):
        parts.append("platform_caps:" + ",".join(record["required_platform_capabilities"]))
    if record.get("missing_binaries"):
        parts.append("missing_binaries:" + ",".join(record["missing_binaries"]))
    if record.get("missing_env_vars"):
        parts.append("missing_env:" + ",".join(record["missing_env_vars"]))
    return "; ".join(parts)


def _profile_visibility(registry: NativeSkillRegistry) -> dict[str, list[str]]:
    visibility: dict[str, list[str]] = {manifest.skill_id: [] for manifest in registry.manifests()}
    for profile in default_skill_profiles():
        report = registry.profile_allowed(profile.profile_id)
        for item in report.get("visible_skills", []):
            if item.get("visible"):
                visibility.setdefault(str(item["skill_id"]), []).append(profile.profile_id)
    return visibility


def _command_map(manifests: list[NativeSkillManifest]) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for command in COMMANDS:
        haystack = " ".join(
            [
                command.command,
                command.description,
                command.example,
                command.toolbroker_path,
                command.docs_link,
                command.notes,
            ]
        )
        for manifest in manifests:
            tokens = {manifest.skill_id, *manifest.required_capabilities, *manifest.allowed_tools}
            if any(token and token in haystack for token in tokens):
                mapping.setdefault(manifest.skill_id, []).append(command.command)
    return mapping


def _lock_status(skill_id: str, changed: set[str], missing: set[str], overall_status: str) -> str:
    if skill_id in changed:
        return "changed"
    if skill_id in missing:
        return "missing"
    return overall_status or "unknown"


def _extract_manual_notes(existing: str) -> str:
    start = existing.find(MANUAL_START)
    end = existing.find(MANUAL_END)
    if start == -1 or end == -1 or end < start:
        return DEFAULT_MANUAL_NOTES
    notes = existing[start + len(MANUAL_START) : end].strip()
    return notes or DEFAULT_MANUAL_NOTES


def _join_or_none(values: list[str]) -> str:
    cleaned = [value for value in values if value]
    return ", ".join(cleaned) if cleaned else "none"


def _cell(value: Any) -> str:
    text = str(value).replace("\n", "<br>")
    return text.replace("|", "\\|")
