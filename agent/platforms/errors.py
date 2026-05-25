from __future__ import annotations


class PlatformError(RuntimeError):
    """Base error for platform metadata and future bridge work."""


class PlatformUnsupportedError(PlatformError):
    """Raised by future bridge execution paths when a platform is unsupported."""


class PlatformCapabilityNotFoundError(PlatformError):
    """Raised only by strict registry lookups; normal lookups return metadata."""
