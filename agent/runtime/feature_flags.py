from __future__ import annotations

from dataclasses import replace

from .errors import RuntimePolicyBlockedError, RuntimeUnavailableError
from .models import RuntimeFeatureInfo, RuntimeFeatureStatus


DEFAULT_FEATURES: tuple[RuntimeFeatureInfo, ...] = (
    RuntimeFeatureInfo("runtime.status", "Runtime status", RuntimeFeatureStatus.ENABLED, enabled_by_default=True),
    RuntimeFeatureInfo("runtime.doctor", "Runtime doctor", RuntimeFeatureStatus.ENABLED, enabled_by_default=True),
    RuntimeFeatureInfo("runtime.events", "Runtime events", RuntimeFeatureStatus.ENABLED, enabled_by_default=True),
    RuntimeFeatureInfo("runtime.jobs", "Runtime job metadata", RuntimeFeatureStatus.ENABLED, enabled_by_default=True),
    RuntimeFeatureInfo("runtime.workflows", "Runtime workflow metadata", RuntimeFeatureStatus.ENABLED, enabled_by_default=True),
    RuntimeFeatureInfo("calendar.write", "Calendar writes", RuntimeFeatureStatus.DISABLED, "CRITICAL", approval_required=True, critical_action=True),
    RuntimeFeatureInfo("contacts.write", "Contacts writes", RuntimeFeatureStatus.DISABLED, "CRITICAL", approval_required=True, personal_data=True, critical_action=True),
    RuntimeFeatureInfo("email.send", "Email send", RuntimeFeatureStatus.DISABLED, "CRITICAL", approval_required=True, personal_data=True, critical_action=True),
    RuntimeFeatureInfo("messages.send", "Message send", RuntimeFeatureStatus.DISABLED, "CRITICAL", approval_required=True, personal_data=True, critical_action=True),
    RuntimeFeatureInfo("personal.read", "Personal data reads", RuntimeFeatureStatus.DISABLED, "HIGH", approval_required=True, personal_data=True),
    RuntimeFeatureInfo("scheduler.background", "Background scheduler", RuntimeFeatureStatus.BLOCKED, "HIGH", approval_required=True, reason="No hidden persistence in v1."),
    RuntimeFeatureInfo("app_bridge.native", "Native app bridge", RuntimeFeatureStatus.PLANNED, "HIGH", approval_required=True, reason="Contract-only until separately approved."),
)


class FeatureFlagRegistry:
    def __init__(self, features: tuple[RuntimeFeatureInfo, ...] = DEFAULT_FEATURES) -> None:
        self._features = {feature.feature_id: feature for feature in features}

    def list_features(self) -> tuple[RuntimeFeatureInfo, ...]:
        return tuple(self._features[key] for key in sorted(self._features))

    def get(self, feature_id: str) -> RuntimeFeatureInfo:
        try:
            return self._features[feature_id]
        except KeyError as exc:
            raise RuntimeUnavailableError(f"unknown feature: {feature_id}") from exc

    def is_enabled(self, feature_id: str) -> bool:
        return self.get(feature_id).status == RuntimeFeatureStatus.ENABLED

    def set_status(self, feature_id: str, status: RuntimeFeatureStatus, reason: str = "", allow_risky_enable: bool = False) -> RuntimeFeatureInfo:
        current = self.get(feature_id)
        if status == RuntimeFeatureStatus.ENABLED and (current.personal_data or current.critical_action) and not allow_risky_enable:
            raise RuntimePolicyBlockedError(f"cannot enable risky feature without explicit policy path: {feature_id}")
        updated = replace(current, status=status, reason=reason or current.reason)
        self._features[feature_id] = updated
        return updated

