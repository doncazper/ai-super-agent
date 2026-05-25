from __future__ import annotations

from enum import StrEnum

from agent.native_skills.models import NativeSkillManifest


class SkillTrustStatus(StrEnum):
    TRUSTED_NATIVE = "trusted_native"
    REVIEWED_LOCAL = "reviewed_local"
    REVIEWED_EXTERNAL = "reviewed_external"
    CANDIDATE = "candidate"
    UNREVIEWED_EXTERNAL = "unreviewed_external"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


def trust_status_for_manifest(manifest: NativeSkillManifest) -> str:
    provenance = manifest.provenance if isinstance(manifest.provenance, dict) else {}
    review_status = str(provenance.get("review_status") or "").casefold()
    source_type = str(provenance.get("source_type") or manifest.source or "").casefold()
    status = manifest.status.casefold()
    if status == "blocked":
        return SkillTrustStatus.BLOCKED.value
    if source_type in {"native", "bundled"} and (status == "available" or review_status in {"reviewed_local", "trusted_native", "reviewed"}):
        return SkillTrustStatus.TRUSTED_NATIVE.value
    if source_type in {"project", "local"} and review_status in {"reviewed_local", "reviewed"}:
        return SkillTrustStatus.REVIEWED_LOCAL.value
    if source_type == "external" and review_status == "reviewed_external":
        return SkillTrustStatus.REVIEWED_EXTERNAL.value
    if source_type in {"external", "clawhub_candidate", "imported"}:
        return SkillTrustStatus.UNREVIEWED_EXTERNAL.value
    if status in {"candidate", "experimental"}:
        return SkillTrustStatus.CANDIDATE.value
    return SkillTrustStatus.UNKNOWN.value


def trust_report(manifest: NativeSkillManifest) -> dict[str, object]:
    status = trust_status_for_manifest(manifest)
    return {
        "skill_id": manifest.skill_id,
        "trust_status": status,
        "trust_level": manifest.trust_level,
        "source": manifest.source,
        "review_status": manifest.provenance.get("review_status") if isinstance(manifest.provenance, dict) else None,
        "enabled_by_default": manifest.status == "available" and status in {SkillTrustStatus.TRUSTED_NATIVE.value, SkillTrustStatus.REVIEWED_LOCAL.value},
        "setup_hint": manifest.setup_hint,
    }
