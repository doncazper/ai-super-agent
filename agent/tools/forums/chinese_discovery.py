from __future__ import annotations

from typing import Any, Callable

from agent.forums.chinese_discovery import (
    fetch_chinese_forum_url,
    list_chinese_forum_providers,
    research_chinese_forums,
    search_chinese_forums,
)


def _schema(name: str, description: str, properties: dict[str, Any] | None = None, required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties or {},
                "required": required or [],
                "additionalProperties": False,
            },
        },
    }


CN_FORUM_SCHEMAS = {
    "cn_forums.providers": _schema(
        "cn_forums.providers",
        "List Chinese/forum discovery providers, site filters, and access limits without network calls.",
    ),
    "cn_forums.search": _schema(
        "cn_forums.search",
        "Discover Chinese-language forum discussions through approved web search provider site filters only.",
        {
            "topic": {"type": "string"},
            "sites": {"type": "string", "default": "zhihu,v2ex,tieba"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 10},
        },
        ["topic"],
    ),
    "cn_forums.fetch": _schema(
        "cn_forums.fetch",
        "Fetch one selected public Chinese/forum URL through the safe web fetch policy; login/CAPTCHA pages return unavailable.",
        {
            "url": {"type": "string"},
            "translate_to": {"type": "string", "default": ""},
        },
        ["url"],
    ),
    "cn_forums.research": _schema(
        "cn_forums.research",
        "Search approved Chinese/forum site filters, fetch selected public results where allowed, and produce source-grounded notes.",
        {
            "topic": {"type": "string"},
            "sites": {"type": "string", "default": "zhihu,v2ex,tieba"},
            "translate_to": {"type": "string", "default": "en"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
        },
        ["topic"],
    ),
}


def make_chinese_forum_tools() -> dict[str, Callable[..., dict[str, Any]]]:
    def providers() -> dict[str, Any]:
        return list_chinese_forum_providers()

    def search(topic: str, sites: str = "zhihu,v2ex,tieba", limit: int = 10) -> dict[str, Any]:
        return search_chinese_forums(topic, sites=sites, limit=limit)

    def fetch(url: str, translate_to: str = "") -> dict[str, Any]:
        return fetch_chinese_forum_url(url, translate_to=translate_to)

    def research(topic: str, sites: str = "zhihu,v2ex,tieba", translate_to: str = "en", limit: int = 5) -> dict[str, Any]:
        return research_chinese_forums(topic, sites=sites, translate_to=translate_to, limit=limit)

    return {
        "cn_forums.providers": providers,
        "cn_forums.search": search,
        "cn_forums.fetch": fetch,
        "cn_forums.research": research,
    }
