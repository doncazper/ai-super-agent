from __future__ import annotations


class MediaError(Exception):
    """Base error for creative media scaffolding."""


class MediaProviderError(MediaError):
    """Raised when a media provider record or provider operation is invalid."""


class MediaAssetError(MediaError):
    """Raised when media asset metadata or paths are invalid."""


class MediaPathError(MediaAssetError):
    """Raised when an asset path escapes the controlled media workspace."""
