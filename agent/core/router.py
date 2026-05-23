from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from agent.safety.policy import RiskLevel
from agent.tools.weather.preferences import configured_default_location


@dataclass(frozen=True)
class RouteDecision:
    name: str
    use_tools: bool
    tool_names: set[str] = field(default_factory=set)
    risk_level: RiskLevel = RiskLevel.SAFE
    metadata: dict[str, Any] = field(default_factory=dict)


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
    PERSONAL_DATA_ACTION_PATTERNS = (
        "read my email",
        "latest email",
        "my inbox",
        "send an email",
        "email to",
        "text ",
        "send a text",
        "send message",
        "my calendar",
        "my contacts",
        "my messages",
        "my tasks",
    )
    WEATHER_INTENT_PATTERNS = (
        "weather",
        "forecast",
        "rain",
        "raining",
        "umbrella",
        "temperature",
        "how hot",
        "how cold",
        "wear",
        "jacket",
        "coat",
        "alerts",
        "storm",
        "hurricane",
        "closures",
        "delayed",
        "delays",
    )
    WEATHER_WEB_CONTEXT_PATTERNS = (
        "flight",
        "flights",
        "airport",
        "delayed",
        "delay",
        "delays",
        "closures",
        "closure",
        "school",
        "schools",
        "latest",
        "update",
        "affecting",
        "impacting",
        "hurricane",
        "storm",
    )
    WEATHER_ALERT_CONTEXT_PATTERNS = (
        "alert",
        "alerts",
        "storm",
        "hurricane",
        "warning",
        "watch",
        "latest",
        "update",
    )
    WEATHER_NON_TOOL_PHRASES = (
        "how weather forecasting works",
        "difference between climate and weather",
        "poem about rain",
        "weather app architecture",
        "build a weather app",
    )
    WEATHER_NON_TOOL_PREFIXES = (
        "explain ",
        "write ",
        "build ",
        "design ",
        "architect ",
    )
    WEATHER_LOCATION_PATTERN = re.compile(
        r"\b(?:in|for|near|around|at)\s+([a-z][a-z .,'-]*?)(?:\s+(?:today|tomorrow|tonight|this weekend|weekend|this week|next week))?[?.!]*$",
        re.IGNORECASE,
    )
    WEATHER_PERSONAL_LOCATION_PHRASES = (
        r"\bnear me\b",
        r"\baround me\b",
        r"\bwhere i am\b",
        r"\bmy location\b",
        r"\bcurrent location\b",
        r"\bhere\b",
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
        weather_route = self._weather_route(user_message, normalized)
        if weather_route is not None:
            return weather_route
        if self._is_personal_data_request(normalized):
            return RouteDecision(
                name="chat.personal_data_approval_required",
                use_tools=False,
                risk_level=RiskLevel.HIGH,
                metadata={"personal_data_request": True, "approval_required": True},
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

    def _weather_route(self, user_message: str, normalized: str) -> RouteDecision | None:
        if not any(pattern in normalized for pattern in self.WEATHER_INTENT_PATTERNS):
            return None
        if self._is_non_tool_weather_topic(normalized):
            return None

        requested_period = self._weather_period(normalized)
        location = self._extract_weather_location(user_message)
        user_location_detected = bool(location)
        default_location_config = configured_default_location()
        default_location = default_location_config.location if default_location_config else ""
        uses_default_location = False

        if not location and default_location:
            location = default_location
            uses_default_location = True

        metadata: dict[str, Any] = {
            "weather_intent": True,
            "requested_period": requested_period,
            "location_detected": user_location_detected,
            "default_location_used": uses_default_location,
            "web_context_needed": self._weather_needs_web(normalized),
            "weather_alerts_needed": self._weather_needs_alerts(normalized),
        }

        if not location and not metadata["web_context_needed"]:
            return RouteDecision(
                name="chat.weather_missing_location",
                use_tools=False,
                risk_level=RiskLevel.SAFE,
                metadata={**metadata, "missing_location": True},
            )

        if metadata["web_context_needed"]:
            tool_names = {"web.search"}
            if location:
                tool_names.update({"weather.current", "weather.forecast"})
            if metadata["weather_alerts_needed"]:
                tool_names.add("weather.alerts")
            return RouteDecision(
                name="tool.weather_research",
                use_tools=True,
                tool_names=tool_names,
                risk_level=RiskLevel.LOW,
                metadata={**metadata, "location": location, "missing_location": not bool(location)},
            )

        return RouteDecision(
            name="tool.weather",
            use_tools=True,
            tool_names={"weather.current", "weather.forecast"},
            risk_level=RiskLevel.LOW,
            metadata={**metadata, "location": location},
        )

    def _is_non_tool_weather_topic(self, normalized: str) -> bool:
        if any(phrase in normalized for phrase in self.WEATHER_NON_TOOL_PHRASES):
            return True
        return any(normalized.startswith(prefix) for prefix in self.WEATHER_NON_TOOL_PREFIXES)

    def _weather_period(self, normalized: str) -> str:
        if "tomorrow" in normalized:
            return "tomorrow"
        if "weekend" in normalized:
            return "weekend"
        if "today" in normalized or "tonight" in normalized:
            return "today"
        return "unspecified"

    def _weather_needs_web(self, normalized: str) -> bool:
        return any(pattern in normalized for pattern in self.WEATHER_WEB_CONTEXT_PATTERNS)

    def _weather_needs_alerts(self, normalized: str) -> bool:
        return any(pattern in normalized for pattern in self.WEATHER_ALERT_CONTEXT_PATTERNS)

    def _extract_weather_location(self, user_message: str) -> str | None:
        normalized = user_message.casefold()
        if any(re.search(pattern, normalized) for pattern in self.WEATHER_PERSONAL_LOCATION_PHRASES):
            return None

        match = self.WEATHER_LOCATION_PATTERN.search(user_message.strip())
        if not match:
            return None

        location = match.group(1).strip(" \t\r\n.,!?")
        location = re.sub(
            r"\s+(today|tomorrow|tonight|this weekend|weekend|this week|next week)$",
            "",
            location,
            flags=re.IGNORECASE,
        ).strip(" \t\r\n.,!?")

        if not location or location.casefold() in {"me", "here", "my area", "current location"}:
            return None
        return location

    def _is_personal_data_request(self, normalized: str) -> bool:
        if normalized.startswith(("explain ", "what is ", "what are ", "write a poem", "build ")):
            return False
        return any(pattern in normalized for pattern in self.PERSONAL_DATA_ACTION_PATTERNS)
