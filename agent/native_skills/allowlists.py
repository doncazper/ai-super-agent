from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from agent.native_skills.models import NativeSkillManifest
from agent.native_skills.profiles import SkillProfile, default_skill_profiles, profile_by_id


RISK_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}
PERSONAL_TRUST_LEVELS = {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"}


@dataclass(frozen=True)
class SkillVisibility:
    skill_id: str
    visible: bool
    reason: str
    profile_id: str
    risk_level: str
    category: str
    status: str
    trust_level: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SkillProfileValidation:
    profile_id: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def profiles_report() -> dict[str, Any]:
    return {
        "status": "ok",
        "profiles": [profile.to_dict() for profile in default_skill_profiles()],
        "execution_model": "profile visibility is advisory metadata only; ToolBroker and PolicyEngine remain final authority",
    }


def profile_report(profile_id: str) -> dict[str, Any]:
    profile = profile_by_id(profile_id)
    if profile is None:
        return {"status": "error", "error": "skill profile not found", "profile_id": profile_id}
    return {"status": "ok", "profile": profile.to_dict()}


def allowed_skills_report(profile_id: str, manifests: list[NativeSkillManifest]) -> dict[str, Any]:
    profile = profile_by_id(profile_id)
    if profile is None:
        return {"status": "error", "error": "skill profile not found", "profile_id": profile_id}
    visibility = [skill_visibility(profile, manifest).to_dict() for manifest in sorted(manifests, key=lambda item: item.skill_id)]
    return {
        "status": "ok",
        "profile": profile.to_dict(),
        "visible_skills": [item for item in visibility if item["visible"]],
        "hidden_skills": [item for item in visibility if not item["visible"]],
        "policy_note": "profile selection does not enable skills, grant capabilities, or bypass ToolBroker/PolicyEngine",
    }


def validate_profile_report(profile_id: str, manifests: list[NativeSkillManifest]) -> dict[str, Any]:
    profile = profile_by_id(profile_id)
    if profile is None:
        return {"status": "error", "error": "skill profile not found", "profile_id": profile_id}
    validation = validate_profile(profile, manifests)
    return {
        "status": "ok" if validation.valid else "error",
        "validation": validation.to_dict(),
        "policy_note": "PolicyEngine and capability manifest validation remain final authority for execution",
    }


def skill_visibility(profile: SkillProfile, manifest: NativeSkillManifest) -> SkillVisibility:
    reason = _hidden_reason(profile, manifest)
    return SkillVisibility(
        skill_id=manifest.skill_id,
        visible=reason is None,
        reason=reason or "visible by profile metadata; execution still requires ToolBroker and PolicyEngine",
        profile_id=profile.profile_id,
        risk_level=manifest.risk_level,
        category=manifest.category,
        status=manifest.status,
        trust_level=manifest.trust_level,
    )


def validate_profile(profile: SkillProfile, manifests: list[NativeSkillManifest]) -> SkillProfileValidation:
    skill_ids = {manifest.skill_id for manifest in manifests}
    errors: list[str] = []
    warnings: list[str] = []
    if profile.risk_ceiling not in RISK_ORDER:
        errors.append(f"unknown risk ceiling: {profile.risk_ceiling}")
    for skill_id in profile.allowed_skills + profile.blocked_skills:
        if skill_id not in skill_ids:
            warnings.append(f"profile references unknown skill: {skill_id}")
    if profile.profile_id == "experimental" and profile.enabled_by_default:
        errors.append("experimental profile must be disabled by default")
    if profile.allow_critical_actions and profile.approval_policy != "policy_engine_final":
        errors.append("critical-capable profiles must keep policy_engine_final approval policy")
    return SkillProfileValidation(profile.profile_id, valid=not errors, errors=errors, warnings=warnings)


def _hidden_reason(profile: SkillProfile, manifest: NativeSkillManifest) -> str | None:
    if not profile.enabled_by_default:
        return "profile disabled by default"
    if manifest.skill_id in profile.blocked_skills:
        return "blocked by profile skill blocklist"
    if manifest.category in profile.blocked_categories:
        return "blocked by profile category blocklist"
    if _risk_value(manifest.risk_level) > _risk_value(profile.risk_ceiling):
        return f"risk level {manifest.risk_level} exceeds profile ceiling {profile.risk_ceiling}"
    if _is_personal_data(manifest) and not profile.allow_personal_data:
        return "personal-data skill hidden by profile"
    if manifest.risk_level == "CRITICAL":
        if not profile.allow_critical_actions:
            return "CRITICAL skill hidden unless profile explicitly allows critical actions"
        if str(manifest.approval_required).lower() not in {"true", "per_action"}:
            return "CRITICAL skill missing approval requirement"
    if _uses_network(manifest) and not profile.allow_network:
        return "network skill hidden by profile"
    if _uses_writes(manifest) and not profile.allow_writes:
        return "write-capable skill hidden by profile"
    if profile.allowed_skills and manifest.skill_id not in profile.allowed_skills:
        return "not listed in profile skill allowlist"
    if profile.allowed_categories and manifest.category not in profile.allowed_categories:
        return "not listed in profile category allowlist"
    return None


def _risk_value(risk_level: str) -> int:
    return RISK_ORDER.get(str(risk_level).upper(), RISK_ORDER["FORBIDDEN"])


def _is_personal_data(manifest: NativeSkillManifest) -> bool:
    if manifest.trust_level in PERSONAL_TRUST_LEVELS:
        return True
    text = " ".join([manifest.category, manifest.description, " ".join(manifest.required_capabilities)]).casefold()
    return any(token in text for token in ("contacts", "calendar", "email", "messages", "inbox", "personal"))


def _uses_network(manifest: NativeSkillManifest) -> bool:
    if manifest.network_behavior not in {"", "none", "disabled"}:
        return True
    return any(capability.startswith(("web.", "news.", "reddit.", "v2ex.")) for capability in manifest.required_capabilities)


def _uses_writes(manifest: NativeSkillManifest) -> bool:
    text = " ".join([manifest.filesystem_behavior, " ".join(manifest.required_capabilities)]).casefold()
    return any(token in text for token in ("write", "send", "create", "update", "delete"))
