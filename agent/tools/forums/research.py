from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agent.forums.research import compare_topic, default_source_fetcher, research_topic


def _schema(name: str, description: str) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "languages": {"type": "string", "default": "en,zh,ja,ko"},
                    "sources": {"type": "string", "default": "reddit,v2ex,web"},
                    "translate_to": {"type": "string", "default": "en"},
                    "limit_per_source": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5},
                },
                "required": ["topic"],
                "additionalProperties": False,
            },
        },
    }


FORUM_RESEARCH_SCHEMAS = {
    "forums.research": _schema(
        "forums.research",
        "Research a topic across configured forum providers with source-grounded multilingual summaries; no scraping fallback.",
    ),
    "forums.compare": _schema(
        "forums.compare",
        "Compare source-labeled forum viewpoints across configured providers/languages without claiming statistical consensus.",
    ),
}


def make_forum_research_tools(project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    root = Path(project_root)
    fetcher = default_source_fetcher(root)

    def research(
        topic: str,
        languages: str = "en,zh,ja,ko",
        sources: str = "reddit,v2ex,web",
        translate_to: str = "en",
        limit_per_source: int = 5,
    ) -> dict[str, Any]:
        return research_topic(
            topic,
            languages=languages,
            sources=sources,
            translate_to=translate_to,
            limit_per_source=limit_per_source,
            source_fetcher=fetcher,
            translator=None,
        )

    def compare(
        topic: str,
        languages: str = "en,zh,ja,ko",
        sources: str = "reddit,v2ex,web",
        translate_to: str = "en",
        limit_per_source: int = 5,
    ) -> dict[str, Any]:
        return compare_topic(
            topic,
            languages=languages,
            sources=sources,
            translate_to=translate_to,
            limit_per_source=limit_per_source,
            source_fetcher=fetcher,
            translator=None,
        )

    return {"forums.research": research, "forums.compare": compare}
