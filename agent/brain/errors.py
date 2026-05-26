from __future__ import annotations


class BrainRuntimeError(RuntimeError):
    """Base error for provider-neutral brain runtime failures."""


class BrainProviderError(BrainRuntimeError):
    def __init__(
        self,
        message: str,
        *,
        provider_id: str = "unknown",
        error_code: str = "provider_error",
        retryable: bool = False,
        setup_hint: str = "",
    ) -> None:
        super().__init__(message)
        self.provider_id = provider_id
        self.error_code = error_code
        self.retryable = retryable
        self.setup_hint = setup_hint

    def to_dict(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "error_code": self.error_code,
            "message": str(self),
            "retryable": self.retryable,
            "setup_hint": self.setup_hint,
        }


class BrainProviderNotFoundError(BrainProviderError):
    def __init__(self, provider_id: str, *, known_provider_ids: tuple[str, ...] = ()) -> None:
        known = ", ".join(known_provider_ids) if known_provider_ids else "none"
        super().__init__(
            f"Unknown brain provider '{provider_id}'. Known providers: {known}.",
            provider_id=provider_id,
            error_code="provider_not_found",
            retryable=False,
            setup_hint="Run the future brain providers command or configure a supported provider.",
        )


def normalize_provider_error(exc: Exception, *, provider_id: str = "unknown") -> BrainProviderError:
    if isinstance(exc, BrainProviderError):
        return exc
    return BrainProviderError(str(exc), provider_id=provider_id, error_code=exc.__class__.__name__, retryable=False)

