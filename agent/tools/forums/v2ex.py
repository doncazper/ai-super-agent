from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agent.forums.v2ex.provider import default_v2ex_provider


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


V2EX_SCHEMAS = {
    "v2ex.status": _schema(
        "v2ex.status",
        "Inspect V2EX connector status/doctor output without fetching topics or replies.",
        {"detail": {"type": "string", "enum": ["status", "doctor"]}},
    ),
    "v2ex.nodes.get": _schema(
        "v2ex.nodes.get",
        "Fetch V2EX nodes through documented read-only API endpoints.",
        {"limit": {"type": "integer", "minimum": 1, "maximum": 1000}},
    ),
    "v2ex.node_topics": _schema(
        "v2ex.node_topics",
        "Fetch V2EX topics for a node through documented read-only API endpoints.",
        {
            "node_name": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            "detect_language": {"type": "boolean"},
            "translate_to": {"type": "string"},
        },
        ["node_name"],
    ),
    "v2ex.topic.get": _schema(
        "v2ex.topic.get",
        "Fetch a V2EX topic through documented read-only API endpoints.",
        {
            "topic_id": {"type": "string"},
            "detect_language": {"type": "boolean"},
            "translate_to": {"type": "string"},
        },
        ["topic_id"],
    ),
    "v2ex.topic_replies": _schema(
        "v2ex.topic_replies",
        "Fetch V2EX topic replies through documented read-only API endpoints.",
        {
            "topic_id": {"type": "string"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 500},
            "detect_language": {"type": "boolean"},
            "translate_to": {"type": "string"},
        },
        ["topic_id"],
    ),
    "v2ex.latest": _schema(
        "v2ex.latest",
        "Fetch latest V2EX topics through documented read-only API endpoints.",
        {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
    ),
    "v2ex.hot": _schema(
        "v2ex.hot",
        "Fetch hot V2EX topics through documented read-only API endpoints.",
        {"limit": {"type": "integer", "minimum": 1, "maximum": 100}},
    ),
}


def make_v2ex_tools(project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    provider = default_v2ex_provider(project_root)

    def status(detail: str = "status") -> dict[str, Any]:
        return provider.status(detail=detail)

    def nodes_get(limit: int = 500) -> dict[str, Any]:
        return provider.nodes(limit=limit)

    def node_topics(node_name: str, limit: int = 10, detect_language: bool = False, translate_to: str = "") -> dict[str, Any]:
        return provider.node_topics(node_name, limit=limit, detect=detect_language, translate_to=translate_to)

    def topic_get(topic_id: str, detect_language: bool = False, translate_to: str = "") -> dict[str, Any]:
        return provider.topic(topic_id, detect=detect_language, translate_to=translate_to)

    def topic_replies(topic_id: str, limit: int = 100, detect_language: bool = False, translate_to: str = "") -> dict[str, Any]:
        return provider.replies(topic_id, limit=limit, detect=detect_language, translate_to=translate_to)

    def latest(limit: int = 10) -> dict[str, Any]:
        return provider.latest(limit=limit)

    def hot(limit: int = 10) -> dict[str, Any]:
        return provider.hot(limit=limit)

    return {
        "v2ex.status": status,
        "v2ex.nodes.get": nodes_get,
        "v2ex.node_topics": node_topics,
        "v2ex.topic.get": topic_get,
        "v2ex.topic_replies": topic_replies,
        "v2ex.latest": latest,
        "v2ex.hot": hot,
    }
