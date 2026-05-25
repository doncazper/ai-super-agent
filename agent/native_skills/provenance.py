from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.trust import trust_status_for_manifest


@dataclass(frozen=True)
class SkillProvenanceRecord:
    skill_id: str
    source_type: str
    source_path: str
    source_url: str
    source_pack_id: str
    author: str
    license: str
    version: str
    hash: str
    reviewed_by: str
    reviewed_at: str
    review_status: str
    trust_level: str
    trust_status: str
    install_status: str
    pinned: bool
    pin_reason: str
    last_updated: str
    known_risks: list[str]
    caveats: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def provenance_record(manifest: NativeSkillManifest) -> SkillProvenanceRecord:
    provenance = manifest.provenance if isinstance(manifest.provenance, dict) else {}
    source_path = manifest.source_path or str(provenance.get("source_path") or "")
    return SkillProvenanceRecord(
        skill_id=manifest.skill_id,
        source_type=str(provenance.get("source_type") or manifest.source or "unknown"),
        source_path=source_path,
        source_url=str(provenance.get("source_url") or ""),
        source_pack_id=str(provenance.get("source_pack_id") or ""),
        author=str(provenance.get("author") or manifest.owner or ""),
        license=manifest.license or str(provenance.get("license") or ""),
        version=manifest.version,
        hash=file_sha256(source_path) if source_path else "",
        reviewed_by=str(provenance.get("reviewed_by") or manifest.owner or ""),
        reviewed_at=str(provenance.get("reviewed_at") or manifest.last_reviewed or ""),
        review_status=str(provenance.get("review_status") or "unknown"),
        trust_level=manifest.trust_level,
        trust_status=trust_status_for_manifest(manifest),
        install_status=manifest.status,
        pinned=bool(provenance.get("pinned", False)),
        pin_reason=str(provenance.get("pin_reason") or ""),
        last_updated=str(provenance.get("last_updated") or manifest.last_reviewed or ""),
        known_risks=list(manifest.known_limitations),
        caveats=_caveats(manifest),
    )


def file_sha256(path: str | Path) -> str:
    source = Path(path)
    if not source.exists() or not source.is_file():
        return ""
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _caveats(manifest: NativeSkillManifest) -> list[str]:
    caveats: list[str] = []
    record = manifest.provenance if isinstance(manifest.provenance, dict) else {}
    if not manifest.license:
        caveats.append("missing license")
    if not record.get("source_type"):
        caveats.append("unknown source")
    if record.get("source_type") == "reconstructed" and not record.get("exact_original"):
        caveats.append("reconstructed skill is not claimed as exact original")
    return caveats
