from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from agent.native_skills.compatibility import compatibility_record, detect_current_platform
from agent.native_skills.models import NativeSkillManifest


CONFLICT_TYPES = {
    "duplicate_skill_id",
    "same_command",
    "same_capability_claim",
    "unsafe_shadowing",
    "experimental_overrides_native",
    "unreviewed_overrides_reviewed",
    "dependency_missing",
    "provider_disabled",
    "platform_incompatible",
    "risk_policy_mismatch",
    "approval_policy_mismatch",
    "memory_policy_mismatch",
    "docs_missing",
    "tests_missing",
}

PERSONAL_TRUST_LEVELS = {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"}
HIGH_RISK_LEVELS = {"HIGH", "CRITICAL"}
SAFE_MEMORY_BEHAVIORS = {"no_store", "redacted_only", "metadata_only", "none", "disabled"}
PROVIDER_ENV_FLAGS = {
    "reddit": "REDDIT_ENABLED",
    "v2ex": "V2EX_ENABLED",
    "news": "NEWS_ENABLED",
    "web": "WEB_ENABLED",
    "searxng": "SEARXNG_ENABLED",
    "brave": "BRAVE_SEARCH_ENABLED",
    "serpapi": "SERPAPI_ENABLED",
}


@dataclass(frozen=True)
class SkillConflict:
    conflict_id: str
    conflict_type: str
    severity: str
    affected_skills: list[str]
    winning_skill: str
    shadowed_skills: list[str]
    risk_level: str
    reason: str
    suggested_resolution: str
    requires_human_review: bool
    safe_to_continue: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_skill_conflicts(
    manifests: list[NativeSkillManifest],
    *,
    precedence: Mapping[str, Any] | None = None,
    current_platform: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    platform_id = current_platform or detect_current_platform()
    environment = os.environ if env is None else env
    conflicts: list[SkillConflict] = []
    conflicts.extend(_duplicate_skill_id_conflicts(manifests))
    conflicts.extend(_same_command_conflicts(manifests))
    conflicts.extend(_same_capability_claim_conflicts(manifests))
    conflicts.extend(_precedence_conflicts(precedence or {}))
    conflicts.extend(_dependency_conflicts(manifests, platform_id=platform_id, env=environment))
    conflicts.extend(_policy_conflicts(manifests))
    conflicts = _dedupe_conflicts(conflicts)
    return {
        "status": "ok",
        "conflict_count": len(conflicts),
        "conflicts": [conflict.to_dict() for conflict in conflicts],
        "safe_to_continue": all(conflict.safe_to_continue for conflict in conflicts),
        "conflict_types": sorted(CONFLICT_TYPES),
        "execution_model": "metadata_only; conflict detection reads manifests/precedence diagnostics only and never executes skills, scripts, providers, or plugin runtimes",
    }


def explain_skill_conflict(
    manifests: list[NativeSkillManifest],
    conflict_id: str,
    *,
    precedence: Mapping[str, Any] | None = None,
    current_platform: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    report = detect_skill_conflicts(manifests, precedence=precedence, current_platform=current_platform, env=env)
    for conflict in report["conflicts"]:
        if conflict["conflict_id"] == conflict_id:
            return {
                "status": "ok",
                "conflict": conflict,
                "execution_model": report["execution_model"],
            }
    return {
        "status": "error",
        "error": "native skill conflict not found",
        "conflict_id": conflict_id,
        "available_conflict_ids": [conflict["conflict_id"] for conflict in report["conflicts"]],
        "execution_model": report["execution_model"],
    }


def _duplicate_skill_id_conflicts(manifests: list[NativeSkillManifest]) -> list[SkillConflict]:
    grouped: dict[str, list[NativeSkillManifest]] = {}
    for manifest in manifests:
        grouped.setdefault(manifest.skill_id, []).append(manifest)
    conflicts = []
    for skill_id, items in grouped.items():
        if len(items) < 2:
            continue
        winner = _choose_winner(items)
        shadowed = [item for item in items if item is not winner]
        conflicts.append(
            _conflict(
                "duplicate_skill_id",
                [item.skill_id for item in items],
                severity="high",
                winning_skill=_skill_label(winner),
                shadowed_skills=[_skill_label(item) for item in shadowed],
                risk_level=_max_risk(item.risk_level for item in items),
                reason=f"Multiple native skill records declare skill_id {skill_id}.",
                suggested_resolution="Review the duplicate records, keep one reviewed source of truth, and archive or rename shadowed candidates.",
                requires_human_review=True,
                safe_to_continue=False,
                qualifier=skill_id,
            )
        )
    return conflicts


def _same_command_conflicts(manifests: list[NativeSkillManifest]) -> list[SkillConflict]:
    by_command: dict[str, list[NativeSkillManifest]] = {}
    for manifest in manifests:
        for command in _commands(manifest):
            by_command.setdefault(command, []).append(manifest)
    conflicts: list[SkillConflict] = []
    for command, items in by_command.items():
        unique = _unique_manifests(items)
        if len(unique) < 2:
            continue
        conflicts.append(
            _conflict(
                "same_command",
                [item.skill_id for item in unique],
                severity="medium",
                winning_skill="",
                shadowed_skills=[],
                risk_level=_max_risk(item.risk_level for item in unique),
                reason=f"Multiple skills declare the same command surface: {command}.",
                suggested_resolution="Rename or scope one command before exposing either skill as user-ready.",
                requires_human_review=True,
                safe_to_continue=True,
                qualifier=command,
            )
        )
    return conflicts


def _same_capability_claim_conflicts(manifests: list[NativeSkillManifest]) -> list[SkillConflict]:
    by_capability: dict[str, list[NativeSkillManifest]] = {}
    for manifest in manifests:
        for capability in manifest.required_capabilities:
            by_capability.setdefault(capability, []).append(manifest)
    conflicts: list[SkillConflict] = []
    for capability, items in by_capability.items():
        unique = _unique_manifests(items)
        if len(unique) < 2:
            continue
        conflicts.append(
            _conflict(
                "same_capability_claim",
                [item.skill_id for item in unique],
                severity="low",
                winning_skill="",
                shadowed_skills=[],
                risk_level=_max_risk(item.risk_level for item in unique),
                reason=f"Multiple skills claim capability {capability}.",
                suggested_resolution="Confirm that the overlap is intentional and that ToolBroker routing remains explicit for each executable path.",
                requires_human_review=False,
                safe_to_continue=True,
                qualifier=capability,
            )
        )
    return conflicts


def _precedence_conflicts(precedence: Mapping[str, Any]) -> list[SkillConflict]:
    conflicts: list[SkillConflict] = []
    duplicate_records = precedence.get("duplicate_skill_ids", {})
    if isinstance(duplicate_records, Mapping):
        for skill_id, raw_items in duplicate_records.items():
            items = [item for item in raw_items if isinstance(item, Mapping)] if isinstance(raw_items, list) else []
            if len(items) < 2:
                continue
            winner, shadowed = _precedence_winner_and_shadowed(skill_id, precedence)
            conflicts.append(
                _conflict(
                    "duplicate_skill_id",
                    [_candidate_label(item) for item in items],
                    severity="high",
                    winning_skill=winner,
                    shadowed_skills=shadowed,
                    risk_level="HIGH",
                    reason=f"Skill root scan found duplicate candidate skill_id {skill_id}.",
                    suggested_resolution="Use skills precedence, then vet and rename/archive candidates before enabling any conflicting skill.",
                    requires_human_review=True,
                    safe_to_continue=False,
                    qualifier=f"precedence:{skill_id}",
                )
            )
            conflicts.extend(_unsafe_shadowing_conflicts(skill_id, items, winner, shadowed))
    return conflicts


def _dependency_conflicts(
    manifests: list[NativeSkillManifest],
    *,
    platform_id: str,
    env: Mapping[str, str],
) -> list[SkillConflict]:
    conflicts: list[SkillConflict] = []
    for manifest in manifests:
        record = compatibility_record(manifest, current_platform=platform_id)
        missing = sorted(set(record.missing_binaries + record.missing_env_vars))
        if missing:
            conflicts.append(
                _conflict(
                    "dependency_missing",
                    [manifest.skill_id],
                    severity="medium",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=manifest.risk_level or "UNKNOWN",
                    reason=f"Skill has missing setup dependencies: {', '.join(missing)}.",
                    suggested_resolution="Keep the skill disabled or requires_setup until dependencies are configured through approved setup docs.",
                    requires_human_review=False,
                    safe_to_continue=True,
                    qualifier=",".join(missing),
                )
            )
        if record.status == "unsupported":
            conflicts.append(
                _conflict(
                    "platform_incompatible",
                    [manifest.skill_id],
                    severity="medium",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=manifest.risk_level or "UNKNOWN",
                    reason=f"Skill is not compatible with current platform {platform_id}.",
                    suggested_resolution="Report unsupported/requires_setup instead of attempting fallback native behavior.",
                    requires_human_review=False,
                    safe_to_continue=True,
                    qualifier=platform_id,
                )
            )
        for provider in record.required_providers:
            flag = PROVIDER_ENV_FLAGS.get(provider)
            if flag and not _env_truthy(env.get(flag)):
                conflicts.append(
                    _conflict(
                        "provider_disabled",
                        [manifest.skill_id],
                        severity="medium",
                        winning_skill=manifest.skill_id,
                        shadowed_skills=[],
                        risk_level=manifest.risk_level or "UNKNOWN",
                        reason=f"Skill requires provider {provider}, but {flag} is not enabled.",
                        suggested_resolution="Return setup hints; do not call disabled providers or paid APIs by default.",
                        requires_human_review=False,
                        safe_to_continue=True,
                        qualifier=provider,
                    )
                )
    return conflicts


def _policy_conflicts(manifests: list[NativeSkillManifest]) -> list[SkillConflict]:
    conflicts: list[SkillConflict] = []
    for manifest in manifests:
        risk = (manifest.risk_level or "").upper()
        approval_required = _approval_required(manifest.approval_required)
        if risk in HIGH_RISK_LEVELS and not approval_required:
            conflicts.append(
                _conflict(
                    "approval_policy_mismatch",
                    [manifest.skill_id],
                    severity="high",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=risk,
                    reason=f"{risk} skill does not require approval.",
                    suggested_resolution="Require ApprovalManager approval before the skill can be considered executable.",
                    requires_human_review=True,
                    safe_to_continue=False,
                    qualifier="approval",
                )
            )
        if risk == "CRITICAL" and _approval_reuse_allowed(manifest.approval_reuse_allowed):
            conflicts.append(
                _conflict(
                    "risk_policy_mismatch",
                    [manifest.skill_id],
                    severity="high",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=risk,
                    reason="CRITICAL skill allows approval reuse.",
                    suggested_resolution="Require exact per-action approval with no approval reuse.",
                    requires_human_review=True,
                    safe_to_continue=False,
                    qualifier="critical_reuse",
                )
            )
        if _personal_data_required(manifest) and manifest.memory_behavior not in SAFE_MEMORY_BEHAVIORS:
            conflicts.append(
                _conflict(
                    "memory_policy_mismatch",
                    [manifest.skill_id],
                    severity="high",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=risk or manifest.risk_level or "UNKNOWN",
                    reason="Personal-data skill has memory behavior that is not no-store or redacted-only.",
                    suggested_resolution="Set memory behavior to no_store/redacted_only or keep the skill disabled.",
                    requires_human_review=True,
                    safe_to_continue=False,
                    qualifier="memory",
                )
            )
        if not manifest.docs_path:
            conflicts.append(
                _conflict(
                    "docs_missing",
                    [manifest.skill_id],
                    severity="low",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=manifest.risk_level or "UNKNOWN",
                    reason="Skill manifest does not reference documentation.",
                    suggested_resolution="Add docs_path before marking the skill user-ready.",
                    requires_human_review=False,
                    safe_to_continue=True,
                    qualifier="docs",
                )
            )
        if not manifest.tests_path:
            conflicts.append(
                _conflict(
                    "tests_missing",
                    [manifest.skill_id],
                    severity="medium",
                    winning_skill=manifest.skill_id,
                    shadowed_skills=[],
                    risk_level=manifest.risk_level or "UNKNOWN",
                    reason="Skill manifest does not reference tests.",
                    suggested_resolution="Add test evidence before marking the skill tested or user-ready.",
                    requires_human_review=False,
                    safe_to_continue=True,
                    qualifier="tests",
                )
            )
    return conflicts


def _unsafe_shadowing_conflicts(
    skill_id: str,
    items: list[Mapping[str, Any]],
    winner: str,
    shadowed: list[str],
) -> list[SkillConflict]:
    conflicts: list[SkillConflict] = []
    winning_item = next((item for item in items if _candidate_label(item) == winner), items[0])
    trusted_items = [item for item in items if bool(item.get("trusted"))]
    untrusted_items = [item for item in items if not bool(item.get("trusted"))]
    if not trusted_items or not untrusted_items:
        return conflicts
    risky_item = winning_item if not bool(winning_item.get("trusted")) else untrusted_items[0]
    root_id = str(risky_item.get("root_id") or "")
    source_type = str(risky_item.get("source_type") or "")
    conflict_type = "unsafe_shadowing"
    if root_id == "experimental_skills":
        conflict_type = "experimental_overrides_native"
    elif not bool(risky_item.get("trusted")):
        conflict_type = "unreviewed_overrides_reviewed"
    conflicts.append(
        _conflict(
            conflict_type,
            [_candidate_label(item) for item in items],
            severity="high",
            winning_skill=winner,
            shadowed_skills=shadowed,
            risk_level="HIGH",
            reason=f"Untrusted or experimental candidate from {root_id or source_type} would shadow a trusted native skill.",
            suggested_resolution="Block the override until a human review verifies provenance, docs, tests, policy, and explicit shadowing approval.",
            requires_human_review=True,
            safe_to_continue=False,
            qualifier=skill_id,
        )
    )
    return conflicts


def _precedence_winner_and_shadowed(skill_id: str, precedence: Mapping[str, Any]) -> tuple[str, list[str]]:
    for resolution in precedence.get("resolutions", []):
        if not isinstance(resolution, Mapping) or resolution.get("skill_id") != skill_id:
            continue
        winner = resolution.get("winning_skill")
        shadowed = resolution.get("shadowed_candidates", [])
        return (
            _candidate_label(winner) if isinstance(winner, Mapping) else "",
            [_candidate_label(item) for item in shadowed if isinstance(item, Mapping)],
        )
    return "", []


def _conflict(
    conflict_type: str,
    affected_skills: list[str],
    *,
    severity: str,
    winning_skill: str,
    shadowed_skills: list[str],
    risk_level: str,
    reason: str,
    suggested_resolution: str,
    requires_human_review: bool,
    safe_to_continue: bool,
    qualifier: str,
) -> SkillConflict:
    affected = sorted(dict.fromkeys(str(item) for item in affected_skills if item))
    return SkillConflict(
        conflict_id=_conflict_id(conflict_type, affected, qualifier),
        conflict_type=conflict_type,
        severity=severity,
        affected_skills=affected,
        winning_skill=winning_skill,
        shadowed_skills=sorted(dict.fromkeys(shadowed_skills)),
        risk_level=risk_level,
        reason=reason,
        suggested_resolution=suggested_resolution,
        requires_human_review=requires_human_review,
        safe_to_continue=safe_to_continue,
    )


def _conflict_id(conflict_type: str, affected_skills: list[str], qualifier: str) -> str:
    basis = "|".join([conflict_type, qualifier, *affected_skills])
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:10]
    slug = "_".join(_slug(item) for item in affected_skills[:2]) or _slug(qualifier) or "global"
    return f"{conflict_type}:{slug}:{digest}"


def _dedupe_conflicts(conflicts: list[SkillConflict]) -> list[SkillConflict]:
    by_id: dict[str, SkillConflict] = {}
    for conflict in conflicts:
        by_id.setdefault(conflict.conflict_id, conflict)
    return sorted(by_id.values(), key=lambda item: (item.severity, item.conflict_type, item.conflict_id))


def _commands(manifest: NativeSkillManifest) -> list[str]:
    raw_commands = manifest.raw.get("commands", [])
    if isinstance(raw_commands, str):
        return [raw_commands]
    if isinstance(raw_commands, list):
        return [str(command) for command in raw_commands if str(command).strip()]
    return []


def _unique_manifests(manifests: list[NativeSkillManifest]) -> list[NativeSkillManifest]:
    seen: set[tuple[str, str]] = set()
    unique = []
    for manifest in manifests:
        key = (manifest.skill_id, manifest.source_path)
        if key not in seen:
            unique.append(manifest)
            seen.add(key)
    return unique


def _choose_winner(items: list[NativeSkillManifest]) -> NativeSkillManifest:
    return sorted(items, key=lambda item: (_root_rank(item.root_id), item.skill_id, item.source_path))[0]


def _root_rank(root_id: str) -> int:
    order = {
        "workspace_skills": 1,
        "project_skills": 2,
        "personal_skills": 3,
        "managed_skills": 4,
        "bundled_native_skills": 5,
        "reconstructed_skills": 6,
        "experimental_skills": 7,
    }
    return order.get(root_id, 99)


def _candidate_label(candidate: Mapping[str, Any]) -> str:
    root_id = str(candidate.get("root_id") or "unknown_root")
    skill_id = str(candidate.get("skill_id") or "unknown_skill")
    return f"{skill_id}@{root_id}"


def _skill_label(manifest: NativeSkillManifest) -> str:
    return f"{manifest.skill_id}@{manifest.root_id or 'unknown_root'}"


def _max_risk(risks: Iterable[str]) -> str:
    rank = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}
    normalized = [str(risk or "SAFE").upper() for risk in risks]
    return max(normalized, key=lambda item: rank.get(item, 0), default="SAFE")


def _approval_required(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "required", "per_action", "per-action", "exact_per_action"}


def _approval_reuse_allowed(value: bool | str) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() not in {"false", "no", "never", "per_action", "per-action", "exact_per_action"}


def _personal_data_required(manifest: NativeSkillManifest) -> bool:
    if manifest.trust_level in PERSONAL_TRUST_LEVELS:
        return True
    text = " ".join([manifest.category, manifest.description, " ".join(manifest.required_capabilities)]).casefold()
    return any(token in text for token in ("contact", "calendar", "email", "message", "inbox", "personal"))


def _env_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _slug(value: str) -> str:
    return "".join(character if character.isalnum() else "_" for character in value.strip().lower()).strip("_")[:48]
