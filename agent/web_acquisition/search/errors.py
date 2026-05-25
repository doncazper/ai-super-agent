from __future__ import annotations


class SearchProviderError(Exception):
    """Base error for normalized search-provider failures."""


class SearchProviderNotFoundError(SearchProviderError):
    """Raised when a requested provider is not registered."""


class SearchProviderSetupError(SearchProviderError):
    """Raised when a provider is known but not configured or enabled."""


class SearchProviderRateLimitError(SearchProviderError):
    """Raised when a provider-specific rate limit blocks a request."""


def normalize_provider_error(exc: Exception) -> dict[str, str]:
    if isinstance(exc, SearchProviderNotFoundError):
        code = "unknown_provider"
    elif isinstance(exc, SearchProviderSetupError):
        code = "setup_required"
    elif isinstance(exc, SearchProviderRateLimitError):
        code = "rate_limited"
    elif isinstance(exc, SearchProviderError):
        code = "provider_error"
    else:
        code = type(exc).__name__
    return {
        "code": code,
        "message": str(exc),
    }
