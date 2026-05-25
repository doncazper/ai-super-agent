from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class RedditConnectorError(Exception):
    """Base class for normalized Reddit connector failures."""

    code = "reddit_error"
    retryable = False

    def to_error(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "retryable": self.retryable,
        }


class RedditSetupError(RedditConnectorError):
    code = "reddit_setup_required"


class RedditApiError(RedditConnectorError):
    code = "reddit_api_error"


class RedditRateLimitError(RedditConnectorError):
    code = "reddit_rate_limit_exceeded"
    retryable = True


class RedditNotFoundError(RedditConnectorError):
    code = "reddit_not_found"


@dataclass(frozen=True)
class RedditErrorPayload:
    code: str
    message: str
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


def normalize_error(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, RedditConnectorError):
        return exc.to_error()
    return RedditErrorPayload(
        code="reddit_unexpected_error",
        message=type(exc).__name__,
        retryable=False,
    ).to_dict()
