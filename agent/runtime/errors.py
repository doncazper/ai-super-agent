from __future__ import annotations


class RuntimeErrorBase(Exception):
    """Base class for runtime orchestration errors."""


class RuntimeUnsupportedError(RuntimeErrorBase):
    """Raised when a requested runtime feature is intentionally unsupported."""


class RuntimeUnavailableError(RuntimeErrorBase):
    """Raised when a service or workflow is not registered or available."""


class RuntimePolicyBlockedError(RuntimeErrorBase):
    """Raised when runtime policy blocks an operation."""

