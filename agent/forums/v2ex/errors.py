from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class V2EXConnectorError(Exception):
    code = "v2ex_error"
    retryable = False

    def to_error(self) -> dict[str, Any]:
        return {"code": self.code, "message": str(self), "retryable": self.retryable}


class V2EXSetupError(V2EXConnectorError):
    code = "v2ex_setup_required"


class V2EXApiError(V2EXConnectorError):
    code = "v2ex_api_error"


class V2EXRateLimitError(V2EXConnectorError):
    code = "v2ex_rate_limit_exceeded"
    retryable = True


@dataclass(frozen=True)
class V2EXErrorPayload:
    code: str
    message: str
    retryable: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload


def normalize_error(exc: Exception) -> dict[str, Any]:
    if isinstance(exc, V2EXConnectorError):
        return exc.to_error()
    return V2EXErrorPayload(code="v2ex_unexpected_error", message=type(exc).__name__).to_dict()
