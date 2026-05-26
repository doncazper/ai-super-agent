from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Mapping


TRUE_VALUES = {"1", "true", "yes", "on"}


def _enabled(env: Mapping[str, str], key: str) -> bool:
    return (env.get(key) or "").strip().casefold() in TRUE_VALUES


@dataclass(frozen=True)
class MobileCompanionConfig:
    companion_enabled: bool
    mobile_approvals_enabled: bool

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MobileCompanionConfig":
        env = environ or os.environ
        return cls(
            companion_enabled=_enabled(env, "MOBILE_COMPANION_ENABLED"),
            mobile_approvals_enabled=_enabled(env, "MOBILE_APPROVALS_ENABLED"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def mobile_status(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    config = MobileCompanionConfig.from_env(environ)
    return {
        "connector": "mobile_companion",
        "status": "disabled" if not config.companion_enabled else "setup_required",
        "enabled": config.companion_enabled,
        "mobile_approvals_enabled": config.mobile_approvals_enabled,
        "paired": False,
        "pairing_status": "unpaired",
        "trust_level": "UNTRUSTED_MESSAGE",
        "approval_manager_required": True,
        "frontend_cannot_self_approve": True,
        "no_personal_data_accessed": True,
        "no_network_calls_made": True,
        "no_background_service": True,
        "no_messages_sent": True,
        "setup_hint": "Future mobile companion access requires explicit pairing and ApprovalManager-backed approvals; no companion app is enabled now.",
    }


def mobile_pairing_status(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    status = mobile_status(environ)
    return {
        "connector": status["connector"],
        "status": status["pairing_status"],
        "enabled": status["enabled"],
        "paired": False,
        "pairing_required_for_sensitive_actions": True,
        "mobile_approvals_enabled": status["mobile_approvals_enabled"],
        "approval_manager_required": True,
        "frontend_cannot_self_approve": True,
        "no_personal_data_accessed": True,
        "no_network_calls_made": True,
        "no_background_service": True,
        "setup_hint": status["setup_hint"],
    }
