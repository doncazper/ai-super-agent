"""Read-only V2EX connector package."""

from agent.forums.v2ex.provider import V2EXReadOnlyProvider, default_v2ex_provider

__all__ = ["V2EXReadOnlyProvider", "default_v2ex_provider"]
