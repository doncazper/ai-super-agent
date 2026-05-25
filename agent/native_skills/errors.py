from __future__ import annotations


class NativeSkillError(Exception):
    """Base error for metadata-only native skill operations."""


class SkillRootNotFoundError(NativeSkillError):
    """Raised when a requested configured skill root does not exist."""


class SkillPrecedenceError(NativeSkillError):
    """Raised when skill precedence cannot be resolved safely."""
