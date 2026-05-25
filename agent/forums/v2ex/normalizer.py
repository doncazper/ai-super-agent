from __future__ import annotations

import html
import re
from datetime import UTC, datetime
from typing import Any, Mapping

from agent.forums.models import ForumComment, ForumPost, ForumThread
from agent.forums.v2ex.models import PROVIDER, TRUST_LEVEL, V2EXNode, V2EXReply, V2EXTopic, stable_source_id, utc_now_iso, v2ex_url


def payload_items(payload: Any, *keys: str) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, Mapping)]
    if isinstance(payload, Mapping):
        for key in keys or ("result", "items", "data", "topics", "replies", "nodes"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, Mapping)]
        if "id" in payload:
            return [payload]
    return []


def normalize_node(payload: Mapping[str, Any]) -> V2EXNode:
    node_id = _text(payload.get("id") or payload.get("name"))
    name = _text(payload.get("name") or node_id)
    title = _text(payload.get("title") or payload.get("title_alternative") or name)
    url = v2ex_url(_text(payload.get("url") or f"/go/{name}"))
    return V2EXNode(
        source_id=stable_source_id("node", node_id or name, url),
        node_id=node_id or name,
        name=name,
        title=title,
        url=url,
        topics=_optional_int(payload.get("topics")),
        created_at=_created_at(payload),
        body_text=_clean_html(_text(payload.get("header") or payload.get("footer") or "")),
    )


def normalize_topic(payload: Mapping[str, Any], *, include_author: bool = False) -> V2EXTopic:
    topic_id = _text(payload.get("id") or payload.get("topic_id"))
    node = payload.get("node")
    node_name = ""
    if isinstance(node, Mapping):
        node_name = _text(node.get("name") or node.get("title"))
    node_name = node_name or _text(payload.get("node_name"))
    url = v2ex_url(_text(payload.get("url") or f"/t/{topic_id}"))
    member = payload.get("member")
    author = _text(member.get("username")) if include_author and isinstance(member, Mapping) else None
    return V2EXTopic(
        source_id=stable_source_id("topic", topic_id, url),
        topic_id=topic_id,
        node_name=node_name,
        title=_clean_html(_text(payload.get("title"))),
        url=url,
        body_text=_clean_html(_text(payload.get("content") or payload.get("content_rendered") or "")),
        reply_count=_optional_int(payload.get("replies")),
        created_at=_created_at(payload),
        author_display=author or None,
    )


def normalize_reply(payload: Mapping[str, Any], *, topic_id: str, topic_url: str = "", include_author: bool = False) -> V2EXReply:
    reply_id = _text(payload.get("id") or payload.get("reply_id"))
    url = f"{topic_url}#reply{reply_id}" if topic_url else v2ex_url(f"/t/{topic_id}#reply{reply_id}")
    member = payload.get("member")
    author = _text(member.get("username")) if include_author and isinstance(member, Mapping) else None
    return V2EXReply(
        source_id=stable_source_id("reply", reply_id, url),
        reply_id=reply_id,
        topic_id=str(topic_id),
        url=url,
        body_text=_clean_html(_text(payload.get("content") or payload.get("content_rendered") or "")),
        created_at=_created_at(payload),
        author_display=author or None,
    )


def topic_to_forum_thread(topic: V2EXTopic, *, replies: list[V2EXReply] | None = None) -> ForumThread:
    retrieved_at = utc_now_iso()
    post = ForumPost(
        source_id=topic.source_id,
        provider=PROVIDER,
        provider_post_id=topic.topic_id,
        title=topic.title,
        url=topic.url,
        body_text=topic.body_text,
        created_at=topic.created_at,
        retrieved_at=retrieved_at,
        trust_level=TRUST_LEVEL,
        author_display=topic.author_display,
        language=topic.language,
        metadata={"node_name": topic.node_name, "reply_count": topic.reply_count},
    )
    comments = [
        ForumComment(
            source_id=reply.source_id,
            provider=PROVIDER,
            provider_comment_id=reply.reply_id,
            thread_id=topic.topic_id,
            url=reply.url,
            body_text=reply.body_text,
            created_at=reply.created_at,
            retrieved_at=retrieved_at,
            trust_level=TRUST_LEVEL,
            author_display=reply.author_display,
            language=reply.language,
        )
        for reply in replies or []
    ]
    return ForumThread(
        source_id=topic.source_id,
        provider=PROVIDER,
        provider_thread_id=topic.topic_id,
        title=topic.title,
        url=topic.url,
        post=post,
        comments=comments,
        retrieved_at=retrieved_at,
        trust_level=TRUST_LEVEL,
        language=topic.language,
        metadata={"node_name": topic.node_name, "reply_count": topic.reply_count},
    )


def _created_at(payload: Mapping[str, Any]) -> str:
    raw = payload.get("created") or payload.get("created_at")
    try:
        return datetime.fromtimestamp(float(raw), UTC).isoformat() if raw not in {None, ""} else ""
    except (TypeError, ValueError, OSError):
        return _text(raw)


def _optional_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _text(value: Any) -> str:
    return str(value or "").strip()


def _clean_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()
