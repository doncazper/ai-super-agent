from __future__ import annotations


class AppBridgeValidationError(ValueError):
    """Raised when an App Bridge payload fails schema validation."""


class AppBridgePairingRequiredError(AppBridgeValidationError):
    """Raised when a sensitive App Bridge request is submitted unpaired."""


class AppBridgeApprovalError(AppBridgeValidationError):
    """Raised when an approval payload attempts to bypass approval rules."""
