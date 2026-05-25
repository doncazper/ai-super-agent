from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.provenance import file_sha256, provenance_record
from agent.native_skills.trust import trust_status_for_manifest


LOCKFILE_NAME = "native_skills.lock"


@dataclass(frozen=True)
class SkillLockRecord:
    skill_id: str
    version: str
    source_type: str
    source_path: str
    source_url: str
    hash: str
    pinned: bool
    reviewed_at: str
    trust_status: str
    manifest_hash: str
    dependencies_hash: str
    effective_root: str
    winning_precedence: int | str
    shadowed_by: str
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def lock_record_for_manifest(manifest: NativeSkillManifest, *, generated_at: str | None = None) -> SkillLockRecord:
    provenance = provenance_record(manifest)
    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    return SkillLockRecord(
        skill_id=manifest.skill_id,
        version=manifest.version,
        source_type=provenance.source_type,
        source_path=provenance.source_path,
        source_url=provenance.source_url,
        hash=file_sha256(provenance.source_path),
        pinned=provenance.pinned,
        reviewed_at=provenance.reviewed_at,
        trust_status=trust_status_for_manifest(manifest),
        manifest_hash=_stable_hash(manifest.raw),
        dependencies_hash=_stable_hash(_dependency_payload(manifest)),
        effective_root=manifest.root_id,
        winning_precedence=manifest.root_id,
        shadowed_by="",
        generated_at=timestamp,
    )


def generate_lockfile_payload(manifests: list[NativeSkillManifest]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": generated_at,
        "records": [lock_record_for_manifest(manifest, generated_at=generated_at).to_dict() for manifest in sorted(manifests, key=lambda item: item.skill_id)],
    }


def verify_lockfile(project_root: str | Path, manifests: list[NativeSkillManifest], *, lockfile_name: str = LOCKFILE_NAME) -> dict[str, Any]:
    root = Path(project_root)
    lock_path = root / lockfile_name
    expected = generate_lockfile_payload(manifests)
    if not lock_path.exists():
        return {
            "status": "requires_setup",
            "lockfile": str(lock_path),
            "record_count": len(expected["records"]),
            "changed": [],
            "missing": [record["skill_id"] for record in expected["records"]],
            "setup_hint": "Create a reviewed native_skills.lock in a future approval step; verification does not write it automatically.",
        }
    existing = yaml.safe_load(lock_path.read_text(encoding="utf-8")) or {}
    existing_records = {str(record.get("skill_id")): record for record in existing.get("records", []) if isinstance(record, dict)}
    changed: list[str] = []
    missing: list[str] = []
    for record in expected["records"]:
        prior = existing_records.get(record["skill_id"])
        if prior is None:
            missing.append(record["skill_id"])
        elif prior.get("manifest_hash") != record["manifest_hash"] or prior.get("hash") != record["hash"]:
            changed.append(record["skill_id"])
    status = "ok" if not changed and not missing else "changed"
    return {
        "status": status,
        "lockfile": str(lock_path),
        "record_count": len(expected["records"]),
        "changed": changed,
        "missing": missing,
        "setup_hint": "Review changed/missing records before trusting updated skills.",
    }


def _dependency_payload(manifest: NativeSkillManifest) -> dict[str, Any]:
    return {
        "required_capabilities": manifest.required_capabilities,
        "required_connectors": manifest.required_connectors,
        "required_env": manifest.required_env,
        "required_config": manifest.required_config,
        "required_binaries": manifest.required_binaries,
        "required_files": manifest.required_files,
        "required_platforms": manifest.required_platforms,
        "required_python": manifest.required_python,
        "required_model_features": manifest.required_model_features,
    }


def _stable_hash(payload: Any) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
