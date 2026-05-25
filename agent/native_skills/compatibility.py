from __future__ import annotations

import os
import shutil
import sys
from dataclasses import asdict, dataclass, field
from typing import Any

from agent.native_skills.models import NativeSkillManifest


PLATFORM_DIMENSIONS = ("macos", "ios_companion", "windows", "linux")
RUNTIME_DIMENSIONS = ("cli_only", "mac_app_bridge", "local_web_dashboard")
PERSONAL_TRUST_LEVELS = {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"}


@dataclass(frozen=True)
class SkillCompatibilityRecord:
    skill_id: str
    status: str
    platforms: dict[str, str]
    runtimes: dict[str, str]
    python_version: str
    lm_studio_required: bool
    model_tool_call_support_required: bool
    required_binaries: list[str]
    missing_binaries: list[str]
    required_env_vars: list[str]
    missing_env_vars: list[str]
    required_connectors: list[str]
    required_providers: list[str]
    required_platform_capabilities: list[str]
    personal_data_required: bool
    approval_required: bool | str
    network_required: bool
    filesystem_required: bool
    native_app_bridge_required: bool
    setup_hint: str
    tests_available: bool
    dogfood_suite_available: bool
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compatibility_matrix(
    manifests: list[NativeSkillManifest],
    *,
    current_platform: str | None = None,
) -> dict[str, Any]:
    platform_id = current_platform or detect_current_platform()
    records = [compatibility_record(manifest, current_platform=platform_id).to_dict() for manifest in sorted(manifests, key=lambda item: item.skill_id)]
    return {
        "status": "ok",
        "current_platform": platform_id,
        "records": records,
        "execution_model": "metadata_only; compatibility checks do not import native modules or execute skills",
    }


def compatibility_for_skill(
    manifests: list[NativeSkillManifest],
    skill_id: str,
    *,
    current_platform: str | None = None,
) -> dict[str, Any]:
    matches = [manifest for manifest in manifests if manifest.skill_id == skill_id]
    if not matches:
        return {"status": "error", "error": "native skill not found", "skill_id": skill_id}
    record = compatibility_record(matches[0], current_platform=current_platform or detect_current_platform())
    return {
        "status": "ok",
        "current_platform": current_platform or detect_current_platform(),
        "record": record.to_dict(),
        "execution_model": "metadata_only; no skill execution or native module import",
    }


def platform_matrix(manifests: list[NativeSkillManifest]) -> dict[str, Any]:
    rows = []
    for manifest in sorted(manifests, key=lambda item: item.skill_id):
        record = compatibility_record(manifest)
        rows.append(
            {
                "skill_id": manifest.skill_id,
                "category": manifest.category,
                "macos": record.platforms["macos"],
                "ios_companion": record.platforms["ios_companion"],
                "windows": record.platforms["windows"],
                "linux": record.platforms["linux"],
                "cli_only": record.runtimes["cli_only"],
                "mac_app_bridge": record.runtimes["mac_app_bridge"],
                "local_web_dashboard": record.runtimes["local_web_dashboard"],
                "status": record.status,
                "setup_hint": record.setup_hint,
            }
        )
    return {
        "status": "ok",
        "rows": rows,
        "execution_model": "metadata_only; platform matrix does not execute platform bridges or native app code",
    }


def compatibility_record(
    manifest: NativeSkillManifest,
    *,
    current_platform: str | None = None,
) -> SkillCompatibilityRecord:
    platform_id = current_platform or detect_current_platform()
    required_platforms = {item for item in manifest.required_platforms if item and item != "any"} or set(PLATFORM_DIMENSIONS)
    platforms = {name: _platform_status(name, required_platforms) for name in PLATFORM_DIMENSIONS}
    runtimes = {
        "cli_only": "supported" if not _native_app_bridge_required(manifest) else "unsupported",
        "mac_app_bridge": "planned" if _native_app_bridge_required(manifest) else "supported",
        "local_web_dashboard": "planned" if any(cap.startswith("app_bridge.") for cap in manifest.required_capabilities) else "supported",
    }
    missing_binaries = [binary for binary in manifest.required_binaries if binary and shutil.which(binary) is None]
    missing_env = [name for name in manifest.required_env if name and not os.environ.get(name)]
    reasons: list[str] = []
    if platform_id not in required_platforms and required_platforms != set(PLATFORM_DIMENSIONS):
        reasons.append(f"current platform {platform_id} not in required platforms {sorted(required_platforms)}")
    if missing_binaries:
        reasons.append(f"missing required binaries: {', '.join(missing_binaries)}")
    if missing_env:
        reasons.append(f"missing required environment variables: {', '.join(missing_env)}")
    if _personal_data_required(manifest):
        reasons.append("personal-data capability requires explicit profile/policy approval and remains disabled unless policy allows")
    if _native_app_bridge_required(manifest):
        reasons.append("native app bridge capability is planned/stubbed and not enabled by default")

    status = _overall_status(manifest, platform_id, required_platforms, missing_binaries, missing_env)
    return SkillCompatibilityRecord(
        skill_id=manifest.skill_id,
        status=status,
        platforms=platforms,
        runtimes=runtimes,
        python_version=manifest.required_python or "unspecified",
        lm_studio_required="lmstudio" in " ".join(manifest.required_model_features).casefold(),
        model_tool_call_support_required=any("tool" in feature.casefold() for feature in manifest.required_model_features),
        required_binaries=list(manifest.required_binaries),
        missing_binaries=missing_binaries,
        required_env_vars=list(manifest.required_env),
        missing_env_vars=missing_env,
        required_connectors=list(manifest.required_connectors),
        required_providers=_required_providers(manifest),
        required_platform_capabilities=_platform_capabilities(manifest),
        personal_data_required=_personal_data_required(manifest),
        approval_required=manifest.approval_required,
        network_required=_network_required(manifest),
        filesystem_required=manifest.filesystem_behavior not in {"", "none", "metadata_only"},
        native_app_bridge_required=_native_app_bridge_required(manifest),
        setup_hint=manifest.setup_hint,
        tests_available=bool(manifest.tests_path),
        dogfood_suite_available=bool(manifest.dogfood_suite),
        reasons=reasons,
    )


def detect_current_platform() -> str:
    value = sys.platform
    if value == "darwin":
        return "macos"
    if value.startswith("win"):
        return "windows"
    if value.startswith("linux"):
        return "linux"
    return "unknown"


def _platform_status(platform_id: str, required_platforms: set[str]) -> str:
    if platform_id in required_platforms:
        return "supported"
    if platform_id == "ios_companion" and "ios" in required_platforms:
        return "planned"
    return "unsupported"


def _overall_status(
    manifest: NativeSkillManifest,
    current_platform: str,
    required_platforms: set[str],
    missing_binaries: list[str],
    missing_env: list[str],
) -> str:
    if manifest.status in {"blocked", "disabled"}:
        return manifest.status
    if current_platform not in required_platforms and required_platforms != set(PLATFORM_DIMENSIONS):
        return "unsupported"
    if missing_binaries or missing_env:
        return "requires_setup"
    if _native_app_bridge_required(manifest):
        return "planned"
    if _personal_data_required(manifest) and manifest.status != "available":
        return "blocked"
    return "supported"


def _required_providers(manifest: NativeSkillManifest) -> list[str]:
    providers: set[str] = set()
    for capability in manifest.required_capabilities:
        if capability.startswith("web."):
            providers.add("web")
        if capability.startswith("news."):
            providers.add("news")
        if capability.startswith("reddit."):
            providers.add("reddit")
        if capability.startswith("v2ex."):
            providers.add("v2ex")
    return sorted(providers)


def _platform_capabilities(manifest: NativeSkillManifest) -> list[str]:
    prefixes = ("macos.", "ios.", "windows.", "microsoft_graph.", "app_bridge.")
    return sorted(capability for capability in manifest.required_capabilities if capability.startswith(prefixes))


def _personal_data_required(manifest: NativeSkillManifest) -> bool:
    if manifest.trust_level in PERSONAL_TRUST_LEVELS:
        return True
    text = " ".join([manifest.category, manifest.description, " ".join(manifest.required_capabilities)]).casefold()
    return any(token in text for token in ("contacts", "calendar", "email", "messages", "inbox", "personal"))


def _network_required(manifest: NativeSkillManifest) -> bool:
    if manifest.network_behavior not in {"", "none", "disabled"}:
        return True
    return bool(_required_providers(manifest))


def _native_app_bridge_required(manifest: NativeSkillManifest) -> bool:
    if any(capability.startswith(("app_bridge.", "macos.", "ios.", "windows.", "microsoft_graph.")) for capability in manifest.required_capabilities):
        return True
    return any(platform_id in {"ios_companion"} for platform_id in manifest.required_platforms)
