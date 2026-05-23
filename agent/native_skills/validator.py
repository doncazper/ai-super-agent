from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from agent.config.loader import load_capabilities_config
from agent.native_skills.manifest import REQUIRED_FIELDS
from agent.native_skills.models import ManifestValidationResult, NativeSkillManifest
from agent.safety.policy import RiskLevel
from agent.safety.trust import TrustLevel


VALID_STATUSES = {"candidate", "available", "disabled", "deprecated", "experimental"}
VALID_MEMORY_BEHAVIORS = {"no_store", "session_only", "store_preference", "store_project_fact", "approval_required"}
MATURITY_VALUES = {
    "candidate",
    "researched",
    "specified",
    "scaffolded",
    "implemented",
    "tested",
    "hardened",
    "live-validated",
    "native-pattern",
    "0 Idea",
    "1 Specified",
    "2 Scaffolded",
    "3 Implemented",
    "4 Tested",
    "5 Hardened",
    "6 Live-Validated",
    "7 User-Ready",
    "8 Mature Pattern",
}
PERSONAL_TRUST_LEVELS = {"LOCAL_PRIVATE_DATA", "UNTRUSTED_EMAIL", "UNTRUSTED_MESSAGE"}
FORBIDDEN_KEYS = {"script", "scripts", "entrypoint", "command", "commands", "module", "code_path", "install", "package_install"}
BYPASS_PHRASES = ("bypass toolbroker", "direct tool access", "disable audit", "ignore policy", "grant permissions")


def known_capabilities_from_config(path: str | Path = "config/capabilities.yaml") -> set[str]:
    config = load_capabilities_config(path)
    tools = config.get("tools", {})
    if not isinstance(tools, Mapping):
        return set()
    return {str(name) for name in tools}


def validate_manifest(manifest: NativeSkillManifest, known_capabilities: set[str]) -> ManifestValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        value = manifest.raw.get(field) if manifest.raw else getattr(manifest, field)
        if value in (None, "", []):
            errors.append(f"missing required field: {field}")

    if manifest.status and manifest.status not in VALID_STATUSES:
        errors.append(f"invalid status: {manifest.status}")
    if manifest.maturity_level and manifest.maturity_level not in MATURITY_VALUES:
        errors.append(f"invalid maturity_level: {manifest.maturity_level}")
    if manifest.risk_level:
        try:
            RiskLevel(manifest.risk_level)
        except ValueError:
            errors.append(f"invalid risk_level: {manifest.risk_level}")
    if manifest.trust_level:
        try:
            TrustLevel(manifest.trust_level)
        except ValueError:
            errors.append(f"invalid trust_level: {manifest.trust_level}")
    if manifest.memory_behavior and manifest.memory_behavior not in VALID_MEMORY_BEHAVIORS:
        errors.append(f"invalid memory_behavior: {manifest.memory_behavior}")
    if not isinstance(manifest.audit_required, bool):
        errors.append("audit_required must be boolean")
    if not isinstance(manifest.inputs_schema, dict):
        errors.append("inputs_schema must be an object")
    if not isinstance(manifest.outputs_schema, dict):
        errors.append("outputs_schema must be an object")

    unknown = sorted((set(manifest.required_capabilities) | set(manifest.allowed_tools)) - known_capabilities)
    if unknown:
        errors.append("unknown required/allowed capabilities: " + ", ".join(unknown))

    if set(manifest.allowed_tools) - set(manifest.required_capabilities):
        errors.append("allowed_tools must be a subset of required_capabilities")

    if _is_personal_skill(manifest) and manifest.status != "disabled":
        errors.append("personal-data native skills must be disabled by default")

    if manifest.risk_level == RiskLevel.CRITICAL.value:
        if manifest.approval_required != "per_action":
            errors.append("CRITICAL native skills require approval_required: per_action")
    elif manifest.risk_level in {RiskLevel.HIGH.value, RiskLevel.MEDIUM.value} and not manifest.approval_required:
        warnings.append("non-low native skill should document approval requirements")

    raw_keys = {str(key) for key in manifest.raw}
    forbidden_keys = sorted(raw_keys & FORBIDDEN_KEYS)
    if forbidden_keys:
        errors.append("manifest contains executable/bypass-oriented fields: " + ", ".join(forbidden_keys))

    text = _manifest_text(manifest)
    if any(phrase in text for phrase in BYPASS_PHRASES):
        errors.append("manifest contains bypass language; native skills cannot bypass ToolBroker, policy, approvals, or audit")

    if not manifest.docs_path:
        warnings.append("docs_path should point to setup or workflow docs")
    if not manifest.tests_path:
        warnings.append("tests_path should point to automated validation")

    return ManifestValidationResult(
        skill_id=manifest.skill_id or "<unknown>",
        valid=not errors,
        errors=errors,
        warnings=warnings,
        source_path=manifest.source_path,
    )


def _is_personal_skill(manifest: NativeSkillManifest) -> bool:
    if manifest.trust_level in PERSONAL_TRUST_LEVELS:
        return True
    personal_terms = ("calendar", "contacts", "email", "messages", "tasks", "personal")
    haystack = f"{manifest.skill_id} {manifest.category} {' '.join(manifest.required_capabilities)}".casefold()
    return any(term in haystack for term in personal_terms)


def _manifest_text(manifest: NativeSkillManifest) -> str:
    values: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for item in value.values():
                visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)
        else:
            values.append(str(value))

    visit(manifest.raw)
    return " ".join(values).casefold()
