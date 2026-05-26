from __future__ import annotations


class SecretsError(Exception):
    """Base error for safe secret metadata helpers."""


class UnknownSecretError(SecretsError):
    """Raised when a requested secret id or env name is not registered."""
