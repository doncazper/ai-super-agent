from __future__ import annotations

from dataclasses import dataclass, field

from agent.safety.policy import RiskLevel


@dataclass(frozen=True)
class RouteDecision:
    name: str
    use_tools: bool
    tool_names: set[str] = field(default_factory=set)
    risk_level: RiskLevel = RiskLevel.SAFE


class Router:
    """Deterministic M2 router.

    It selects whether tool schemas are attached, but never rewrites the user's
    message and never adds hidden reasoning to the model prompt.
    """

    TIME_PATTERNS = (
        "what time",
        "current time",
        "time is it",
        "date and time",
    )
    WEB_SEARCH_PATTERNS = (
        "search the web",
        "web search",
        "look up",
        "find online",
        "internet search",
    )
    MEMORY_PATTERNS = (
        "remember that",
        "remember this",
        "save this preference",
        "store this memory",
        "what do you remember",
        "search memory",
        "forget memory",
    )

    def route(self, user_message: str, *, force_no_tools: bool = False) -> RouteDecision:
        if force_no_tools:
            return RouteDecision(name="chat.no_tools", use_tools=False)
        normalized = user_message.casefold()
        if any(pattern in normalized for pattern in self.TIME_PATTERNS):
            return RouteDecision(
                name="tool.time",
                use_tools=True,
                tool_names={"time.get_current_time"},
                risk_level=RiskLevel.SAFE,
            )
        if normalized.startswith(("http://", "https://")) or "fetch url" in normalized or "read this url" in normalized:
            return RouteDecision(
                name="tool.web_fetch",
                use_tools=True,
                tool_names={"web.fetch_url"},
                risk_level=RiskLevel.MEDIUM,
            )
        if any(pattern in normalized for pattern in self.WEB_SEARCH_PATTERNS):
            return RouteDecision(
                name="tool.web_search",
                use_tools=True,
                tool_names={"web.search"},
                risk_level=RiskLevel.LOW,
            )
        if any(pattern in normalized for pattern in self.MEMORY_PATTERNS):
            return RouteDecision(
                name="tool.memory",
                use_tools=True,
                tool_names={"memory.store", "memory.search", "memory.delete", "memory.export"},
                risk_level=RiskLevel.LOW,
            )
        return RouteDecision(name="chat.default", use_tools=False)
