from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping

from .models import (
    RedditComment,
    RedditPost,
    RedditSearchResult,
    RedditSubreddit,
    RedditThread,
    reddit_permalink,
    stable_source_id,
    utc_now_iso,
)


REMOVED_MARKERS = {"[deleted]", "[removed]", "deleted", "removed"}


def normalize_listing(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    children = payload.get("data", {}).get("children", []) if isinstance(payload.get("data"), Mapping) else []
    if not isinstance(children, list):
        return []
    return [child.get("data", {}) for child in children if isinstance(child, Mapping) and isinstance(child.get("data"), Mapping)]


def normalize_search_results(payload: Mapping[str, Any], *, retrieved_at: str | None = None) -> list[RedditSearchResult]:
    timestamp = retrieved_at or utc_now_iso()
    results: list[RedditSearchResult] = []
    for index, data in enumerate(normalize_listing(payload), start=1):
        post = normalize_post(data, retrieved_at=timestamp)
        results.append(
            RedditSearchResult(
                source_id=post.source_id,
                reddit_id=post.reddit_id,
                subreddit=post.subreddit,
                title=post.title,
                url=post.url,
                permalink=post.permalink,
                body_text=post.body_text,
                score=post.score,
                comment_count=post.comment_count,
                created_at=post.created_at,
                retrieved_at=post.retrieved_at,
                author_display=post.author_display,
                removed=post.removed,
                rank=index,
                snippet_only=True,
            )
        )
    return results


def normalize_post(data: Mapping[str, Any], *, retrieved_at: str | None = None) -> RedditPost:
    reddit_id = _string(data.get("id") or data.get("name")).removeprefix("t3_")
    permalink = reddit_permalink(_string(data.get("permalink")))
    removed = _is_removed(data.get("selftext")) or _is_removed(data.get("author"))
    body = "" if removed else _string(data.get("selftext") or data.get("body") or "")
    author = None if removed else _author(data)
    return RedditPost(
        source_id=stable_source_id("post", reddit_id, permalink),
        reddit_id=reddit_id,
        subreddit=_string(data.get("subreddit")),
        title=_string(data.get("title")),
        url=_string(data.get("url")) or permalink,
        permalink=permalink,
        body_text=body,
        score=_int_or_none(data.get("score")),
        comment_count=_int_or_none(data.get("num_comments")),
        created_at=_created_at(data),
        retrieved_at=retrieved_at or utc_now_iso(),
        author_display=author,
        removed=removed,
    )


def normalize_subreddit(data: Mapping[str, Any], *, retrieved_at: str | None = None) -> RedditSubreddit:
    reddit_id = _string(data.get("id") or data.get("name")).removeprefix("t5_")
    display = _string(data.get("display_name") or data.get("display_name_prefixed")).removeprefix("r/")
    permalink = reddit_permalink(_string(data.get("url") or f"/r/{display}/"))
    description = _string(data.get("public_description") or data.get("description") or "")
    return RedditSubreddit(
        source_id=stable_source_id("subreddit", reddit_id or display, permalink),
        reddit_id=reddit_id,
        subreddit=display,
        title=_string(data.get("title") or display),
        url=permalink,
        permalink=permalink,
        body_text=description,
        subscribers=_int_or_none(data.get("subscribers")),
        public_description=description,
        created_at=_created_at(data),
        retrieved_at=retrieved_at or utc_now_iso(),
    )


def normalize_thread(
    payload: Any,
    *,
    retrieved_at: str | None = None,
    max_comments: int | None = None,
    collapse_depth: int | None = None,
) -> RedditThread:
    timestamp = retrieved_at or utc_now_iso()
    if not isinstance(payload, list) or not payload:
        empty_post = normalize_post({}, retrieved_at=timestamp)
        return RedditThread(
            post=empty_post,
            comments=[],
            comment_tree=[],
            retrieved_at=timestamp,
            fetch_warnings=[{"code": "reddit_thread_empty", "message": "Reddit thread payload did not include listings."}],
        )
    post_listing = payload[0] if isinstance(payload[0], Mapping) else {}
    post_items = normalize_listing(post_listing)
    post = normalize_post(post_items[0] if post_items else {}, retrieved_at=timestamp)
    comments_listing = payload[1] if len(payload) > 1 and isinstance(payload[1], Mapping) else {}
    comments: list[RedditComment] = []
    comment_tree: list[dict[str, Any]] = []
    state = {"count": 0, "truncated": False, "collapsed": 0}
    for child in normalize_listing(comments_listing):
        node = _normalize_comment_node(
            child,
            retrieved_at=timestamp,
            depth=0,
            max_comments=max_comments,
            collapse_depth=collapse_depth,
            state=state,
            flattened=comments,
        )
        if node is not None:
            comment_tree.append(node)
    return RedditThread(
        post=post,
        comments=comments,
        comment_tree=comment_tree,
        retrieved_at=timestamp,
        truncation_info={
            "truncated": bool(state["truncated"]),
            "max_comments": max_comments,
            "returned_comments": len(comments),
            "collapse_depth": collapse_depth,
            "collapsed_comment_count": int(state["collapsed"]),
        },
    )


def _normalize_comment_tree(data: Mapping[str, Any], *, retrieved_at: str, depth: int) -> list[RedditComment]:
    if _is_more_comment(data):
        return []
    comment = normalize_comment(data, retrieved_at=retrieved_at, depth=depth)
    comments = [comment]
    replies = data.get("replies")
    if isinstance(replies, Mapping):
        for child in normalize_listing(replies):
            comments.extend(_normalize_comment_tree(child, retrieved_at=retrieved_at, depth=depth + 1))
    return comments


def _normalize_comment_node(
    data: Mapping[str, Any],
    *,
    retrieved_at: str,
    depth: int,
    max_comments: int | None,
    collapse_depth: int | None,
    state: dict[str, int | bool],
    flattened: list[RedditComment],
) -> dict[str, Any] | None:
    if _is_more_comment(data):
        return None
    if max_comments is not None and int(state["count"]) >= max_comments:
        state["truncated"] = True
        return None
    comment = normalize_comment(data, retrieved_at=retrieved_at, depth=depth)
    flattened.append(comment)
    state["count"] = int(state["count"]) + 1
    node = comment.to_dict()
    node["replies"] = []
    replies = data.get("replies")
    if not isinstance(replies, Mapping):
        return node
    child_items = normalize_listing(replies)
    if collapse_depth is not None and depth >= collapse_depth:
        if child_items:
            node["collapsed"] = True
            node["collapsed_reply_count"] = len(child_items)
            state["collapsed"] = int(state["collapsed"]) + len(child_items)
        return node
    for child in child_items:
        child_node = _normalize_comment_node(
            child,
            retrieved_at=retrieved_at,
            depth=depth + 1,
            max_comments=max_comments,
            collapse_depth=collapse_depth,
            state=state,
            flattened=flattened,
        )
        if child_node is not None:
            node["replies"].append(child_node)
    return node


def normalize_comment(data: Mapping[str, Any], *, retrieved_at: str | None = None, depth: int = 0) -> RedditComment:
    reddit_id = _string(data.get("id") or data.get("name")).removeprefix("t1_")
    permalink = reddit_permalink(_string(data.get("permalink")))
    removed = _is_removed(data.get("body")) or _is_removed(data.get("author"))
    body = "" if removed else _string(data.get("body"))
    author = None if removed else _author(data)
    return RedditComment(
        source_id=stable_source_id("comment", reddit_id, permalink),
        reddit_id=reddit_id,
        subreddit=_string(data.get("subreddit")),
        title=_string(data.get("link_title") or data.get("title")),
        url=permalink,
        permalink=permalink,
        body_text=body,
        score=_int_or_none(data.get("score")),
        comment_count=None,
        created_at=_created_at(data),
        retrieved_at=retrieved_at or utc_now_iso(),
        author_display=author,
        parent_id=_string(data.get("parent_id")),
        depth=depth,
        removed=removed,
    )


def _author(data: Mapping[str, Any]) -> str | None:
    author = _string(data.get("author"))
    if not author or _is_removed(author):
        return None
    return author


def _is_removed(value: Any) -> bool:
    text = _string(value).strip().casefold()
    return text in REMOVED_MARKERS


def _is_more_comment(data: Mapping[str, Any]) -> bool:
    return "children" in data and "body" not in data


def _created_at(data: Mapping[str, Any]) -> str:
    raw = data.get("created_utc") or data.get("created")
    try:
        return datetime.fromtimestamp(float(raw), tz=UTC).isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _string(value: Any) -> str:
    return str(value or "").strip()
