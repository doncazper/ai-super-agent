from __future__ import annotations

from typing import Protocol

from agent.forums.models import ForumProvider


class ForumProviderAdapter(Protocol):
    """Metadata-first adapter contract for future read-only forum connectors."""

    def metadata(self) -> ForumProvider:
        """Return static/config metadata without network, login, or personal-data reads."""

    def is_configured(self) -> bool:
        """Return config readiness without validating credentials against live user content."""

    def list_read_capabilities(self) -> tuple[str, ...]:
        """Return read-only capability identifiers planned or implemented by this adapter."""

    def list_write_capabilities(self) -> tuple[str, ...]:
        """Return an empty tuple in the current read-only forum track."""
