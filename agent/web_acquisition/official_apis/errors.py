from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OfficialApiError(Exception):
    message: str
    code: str = "official_api_error"
    setup_hint: str = ""
    retryable: bool = False

    def __str__(self) -> str:
        return self.message


class OfficialApiNotFoundError(OfficialApiError):
    def __init__(self, provider_name: str) -> None:
        super().__init__(
            message=f"unknown official API provider: {provider_name}",
            code="unknown_provider",
            setup_hint="Run `python smart_agent.py web official-apis` to list known providers.",
        )


class OfficialApiSetupError(OfficialApiError):
    def __init__(self, message: str, *, setup_hint: str = "") -> None:
        super().__init__(message=message, code="setup_required", setup_hint=setup_hint or message)


class OfficialApiPolicyError(OfficialApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="policy_denied")


def normalize_official_api_error(exc: Exception) -> dict[str, object]:
    if isinstance(exc, OfficialApiError):
        payload: dict[str, object] = {
            "code": exc.code,
            "message": exc.message,
            "retryable": exc.retryable,
        }
        if exc.setup_hint:
            payload["setup_hint"] = exc.setup_hint
        return payload
    return {"code": "official_api_error", "message": str(exc), "retryable": False}
