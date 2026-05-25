from __future__ import annotations

import os
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
        "look this up",
        "find online",
        "internet search",
        "search online",
        "browse",
        "verify",
        "source",
    )
    SOURCE_GROUNDED_PATTERNS = (
        "cite",
        "citation",
        "citations",
        "with sources",
        "source list",
        "source-grounded",
        "source grounded",
        "references",
        "no fabricated",
    )
    CURRENT_INFO_PATTERNS = (
        "latest",
        "current",
        "today",
        "recent",
        "newest",
        "breaking",
        "news",
        "current events",
        "price",
        "pricing",
        "availability",
        "available",
        "schedule",
        "schedules",
        "release notes",
        "changelog",
        "version",
        "api docs",
        "documentation",
        "provider docs",
        "law",
        "laws",
        "regulation",
        "regulations",
        "rules",
        "policy update",
        "who is the ceo",
    )
    URL_PATTERN = re.compile(r"https?://[^\s<>'\")]+", re.IGNORECASE)
    PROMPT_INJECTION_PATTERNS = (
        "ignore previous instructions",
        "ignore all previous",
        "disregard previous instructions",
        "reveal secrets",
        "show system prompt",
        "disable audit",
        "bypass policy",
        "bypass toolbroker",
        "bypass approval",
    )
    LOCAL_REPO_CONTEXT_PATTERNS = (
        "in this repo",
        "in this repository",
        "this repo",
        "this repository",
        "this codebase",
        "local repo",
        "from the code",
        "from local docs",
    )
    STABLE_NON_INTERNET_PREFIXES = (
        "explain ",
        "write ",
        "draft ",
        "solve ",
        "calculate ",
        "summarize this",
        "summarize the following",
        "what is ",
        "what are ",
        "why is ",
        "how does ",
        "help me think",
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
            return RouteDecision(
                name="chat.no_tools",
                use_tools=False,
                metadata=self._routing_metadata(
                    needs_internet=False,
                    reason="no-tools mode disables internet and all other tool attachments",
                    tools=[],
                    risk_hint="SAFE: no tools attached",
                ),
            )
        normalized = user_message.casefold()
        if self._looks_like_prompt_injection(normalized):
            return RouteDecision(
                name="chat.prompt_injection_no_tools",
                use_tools=False,
                risk_level=RiskLevel.SAFE,
                metadata=self._routing_metadata(
                    needs_internet=False,
                    reason="prompt-injection-like text cannot force internet routing",
                    tools=[],
                    risk_hint="SAFE: suspicious routing instruction ignored",
                ),
            )
        if any(pattern in normalized for pattern in self.TIME_PATTERNS):
            return RouteDecision(
                name="tool.time",
                use_tools=True,
                tool_names={"time.get_current_time"},
                risk_level=RiskLevel.SAFE,
                metadata=self._routing_metadata(
                    needs_internet=False,
                    reason="stable local time/date request uses the time tool, not internet",
                    tools=["time.get_current_time"],
                    risk_hint="SAFE: local metadata only",
                ),
            )
        url = self._extract_url(user_message)
        if url or "fetch url" in normalized or "read this url" in normalized:
            return RouteDecision(
                name="tool.web_fetch",
                use_tools=True,
                tool_names={"web.fetch_url"},
                risk_level=RiskLevel.MEDIUM,
                metadata=self._routing_metadata(
                    needs_internet=True,
                    reason="explicit URL or selected-URL fetch request",
                    suggested_sources=["user_url", "direct_fetch"],
                    tools=["web.fetch_url"],
                    risk_hint="MEDIUM: selected public URL fetch returns UNTRUSTED_WEB data",
                    url=url,
                ),
            )
        weather_route = self._weather_route(user_message, normalized)
        if weather_route is not None:
            return weather_route
        if self._is_personal_data_request(normalized):
            return RouteDecision(
                name="chat.personal_data_approval_required",
                use_tools=False,
                risk_level=RiskLevel.HIGH,
                metadata={
                    **self._routing_metadata(
                        needs_internet=False,
                        reason="personal-data request requires a separate approved connector path, not internet routing",
                        tools=[],
                        risk_hint="HIGH: approval-gated personal-data request",
                    ),
                    "personal_data_request": True,
                    "approval_required": True,
                },
            )
        if any(pattern in normalized for pattern in self.MEMORY_PATTERNS):
            return RouteDecision(
                name="tool.memory",
                use_tools=True,
                tool_names={"memory.store", "memory.search", "memory.delete", "memory.export"},
                risk_level=RiskLevel.LOW,
                metadata=self._routing_metadata(
                    needs_internet=False,
                    reason="memory request uses local memory tools, not internet",
                    tools=["memory.delete", "memory.export", "memory.search", "memory.store"],
                    risk_hint="LOW: local memory capability policy applies",
                ),
            )
        internet_route = self._internet_route(user_message, normalized)
        if internet_route is not None:
            return internet_route
        return RouteDecision(
            name="chat.default",
            use_tools=False,
            metadata=self._routing_metadata(
                needs_internet=False,
                reason="no deterministic internet trigger matched",
                tools=[],
                risk_hint="SAFE: normal chat without tool attachments",
            ),
        )

    def explain(self, user_message: str, *, force_no_tools: bool = False) -> dict[str, Any]:
        route = self.route(user_message, force_no_tools=force_no_tools)
        return self.explain_decision(user_message, route)

    def explain_decision(self, user_message: str, route: RouteDecision) -> dict[str, Any]:
        metadata = route.metadata
        return {
            "needs_internet": bool(metadata.get("needs_internet", False)),
            "reason": str(metadata.get("reason", "no route reason recorded")),
            "suggested_sources": list(metadata.get("suggested_sources", [])),
            "provider_policy": dict(metadata.get("provider_policy", self._provider_policy())),
            "tools": sorted(route.tool_names or metadata.get("tools", [])),
            "risk_hint": str(metadata.get("risk_hint", route.risk_level.value)),
            "ask_clarification": bool(metadata.get("ask_clarification", False)),
            "route": {
                "name": route.name,
                "use_tools": route.use_tools,
                "risk_level": route.risk_level.value,
                "metadata": metadata,
            },
            "llm_router_used": False,
            "user_message_rewritten": False,
            "message_length": len(user_message),
        }

    def _internet_route(self, user_message: str, normalized: str) -> RouteDecision | None:
        if self._is_local_repo_request(normalized):
            return None

        source_grounded = any(pattern in normalized for pattern in self.SOURCE_GROUNDED_PATTERNS)
        current_info = any(pattern in normalized for pattern in self.CURRENT_INFO_PATTERNS)
        explicit_search = any(pattern in normalized for pattern in self.WEB_SEARCH_PATTERNS)
        niche_stale = self._looks_like_named_stale_fact(user_message, normalized)

        if source_grounded:
            return RouteDecision(
                name="tool.web_research",
                use_tools=True,
                tool_names={"web.search", "web.fetch_url"},
                risk_level=RiskLevel.MEDIUM,
                metadata=self._routing_metadata(
                    needs_internet=True,
                    reason="user requested citations, sources, or source-grounded evidence",
                    suggested_sources=["source_grounded_research", "search_provider", "selected_source_fetch"],
                    tools=["web.fetch_url", "web.search"],
                    risk_hint="MEDIUM: search/fetch returns UNTRUSTED_WEB data",
                ),
            )
        if current_info:
            return RouteDecision(
                name="tool.web_research",
                use_tools=True,
                tool_names={"web.search", "web.fetch_url"},
                risk_level=RiskLevel.MEDIUM,
                metadata=self._routing_metadata(
                    needs_internet=True,
                    reason="request asks for current, live, changing, or source-sensitive information",
                    suggested_sources=["cache", "rss_feed", "sitemap", "official_api", "search_provider"],
                    tools=["web.fetch_url", "web.search"],
                    risk_hint="MEDIUM: current public web data is untrusted and source-dependent",
                ),
            )
        if explicit_search:
            return RouteDecision(
                name="tool.web_search",
                use_tools=True,
                tool_names={"web.search"},
                risk_level=RiskLevel.LOW,
                metadata=self._routing_metadata(
                    needs_internet=True,
                    reason="user explicitly asked to search, look up, browse, verify, or use web sources",
                    suggested_sources=["search_provider", "official_api", "cache"],
                    tools=["web.search"],
                    risk_hint="LOW: search result snippets are UNTRUSTED_WEB data",
                ),
            )
        if niche_stale:
            return RouteDecision(
                name="tool.web_research",
                use_tools=True,
                tool_names={"web.search", "web.fetch_url"},
                risk_level=RiskLevel.MEDIUM,
                metadata=self._routing_metadata(
                    needs_internet=True,
                    reason="named niche fact is likely to be stale without source data",
                    suggested_sources=["official_api", "search_provider", "selected_source_fetch"],
                    tools=["web.fetch_url", "web.search"],
                    risk_hint="MEDIUM: source validation required before claiming current facts",
                ),
            )
        return None

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
                metadata={
                    **self._routing_metadata(
                        needs_internet=False,
                        reason="weather request needs an explicit location before attaching tools",
                        tools=[],
                        risk_hint="SAFE: ask for clarification before tool use",
                        ask_clarification=True,
                    ),
                    **metadata,
                    "missing_location": True,
                },
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
                metadata={
                    **self._routing_metadata(
                        needs_internet=True,
                        reason="weather impact, alert, or disruption request needs live public context",
                        suggested_sources=["weather_provider", "search_provider"],
                        tools=sorted(tool_names),
                        risk_hint="LOW: public weather/web context only",
                        ask_clarification=not bool(location) and not metadata["weather_alerts_needed"],
                    ),
                    **metadata,
                    "location": location,
                    "missing_location": not bool(location),
                },
            )

        return RouteDecision(
            name="tool.weather",
            use_tools=True,
            tool_names={"weather.current", "weather.forecast"},
            risk_level=RiskLevel.LOW,
            metadata={
                **self._routing_metadata(
                    needs_internet=False,
                    reason="weather request uses configured weather tools rather than generic internet search",
                    suggested_sources=["weather_provider"],
                    tools=["weather.current", "weather.forecast"],
                    risk_hint="LOW: explicit location weather lookup",
                ),
                **metadata,
                "location": location,
            },
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

    def _extract_url(self, user_message: str) -> str | None:
        match = self.URL_PATTERN.search(user_message)
        return match.group(0).rstrip(".,!?") if match else None

    def _looks_like_prompt_injection(self, normalized: str) -> bool:
        if not any(pattern in normalized for pattern in self.PROMPT_INJECTION_PATTERNS):
            return False
        routing_terms = self.WEB_SEARCH_PATTERNS + self.CURRENT_INFO_PATTERNS + ("call tools", "use tools")
        return any(term in normalized for term in routing_terms)

    def _is_local_repo_request(self, normalized: str) -> bool:
        if not any(pattern in normalized for pattern in self.LOCAL_REPO_CONTEXT_PATTERNS):
            return False
        return not any(pattern in normalized for pattern in self.WEB_SEARCH_PATTERNS + self.CURRENT_INFO_PATTERNS)

    def _looks_like_named_stale_fact(self, user_message: str, normalized: str) -> bool:
        if any(normalized.startswith(prefix) for prefix in self.STABLE_NON_INTERNET_PREFIXES):
            return False
        if any(term in normalized for term in ("release", "roadmap", "pricing", "availability", "status")):
            return True
        capitalized_terms = re.findall(r"\b[A-Z][A-Za-z0-9]+(?:[.-][A-Z][A-Za-z0-9]+)?\b", user_message)
        return len(capitalized_terms) >= 2 and any(
            cue in normalized for cue in ("who runs", "who owns", "founder", "ceo", "version", "docs")
        )

    def _routing_metadata(
        self,
        *,
        needs_internet: bool,
        reason: str,
        tools: list[str],
        risk_hint: str,
        suggested_sources: list[str] | None = None,
        ask_clarification: bool = False,
        **extra: Any,
    ) -> dict[str, Any]:
        metadata = {
            "needs_internet": needs_internet,
            "reason": reason,
            "suggested_sources": suggested_sources or [],
            "provider_policy": self._provider_policy(),
            "tools": tools,
            "risk_hint": risk_hint,
            "ask_clarification": ask_clarification,
            "llm_router_used": False,
            "user_message_rewritten": False,
        }
        metadata.update({key: value for key, value in extra.items() if value is not None})
        return metadata

    def _provider_policy(self) -> dict[str, Any]:
        return {
            "mode": os.getenv("PROVIDER_COST_MODE", "free_first"),
            "default_provider": os.getenv("SEARCH_DEFAULT_PROVIDER", "auto"),
            "paid_apis_allowed": os.getenv("ALLOW_PAID_APIS", "false").casefold() == "true",
            "paid_apis_default": False,
            "query_history_persisted": False,
            "web_content_memory_default": False,
            "missing_provider_behavior": "return setup hint or structured unavailable result",
            "llm_router_default": False,
        }
