from __future__ import annotations


class SandboxError(Exception):
    """Base class for sandbox abstraction errors."""


class UnknownSandboxBackendError(SandboxError):
    """Raised when a requested sandbox backend is not registered."""


class SandboxPolicyError(SandboxError):
    """Raised when a sandbox request violates safe defaults."""
