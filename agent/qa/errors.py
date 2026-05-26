from __future__ import annotations


class CommandQAError(Exception):
    """Base error for command QA sandbox helpers."""


class CommandQAUnsafeError(CommandQAError):
    """Raised when a requested QA operation is outside the allowed tier."""
