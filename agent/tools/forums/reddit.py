from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from agent.forums.reddit.doctor import reddit_auth_check, reddit_doctor, reddit_status
from agent.forums.reddit.provider import default_reddit_provider


REDDIT_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.status",
        "description": "Inspect Reddit OAuth/config status without fetching Reddit posts or comments.",
        "parameters": {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "enum": ["status", "doctor"],
                    "description": "Use doctor for full diagnostics and status for compact readiness.",
                }
            },
            "additionalProperties": False,
        },
    },
}

REDDIT_AUTH_CHECK_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.auth_check",
        "description": "Explicitly verify Reddit OAuth token/config against a harmless OAuth endpoint; never fetch posts/comments.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_SEARCH_POSTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.search_posts",
        "description": "Search Reddit posts through the official Reddit Data API only; no web scraping fallback.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "subreddit": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "sort": {"type": "string", "enum": ["relevance", "hot", "top", "new", "comments"]},
                "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"]},
                "language": {"type": "string", "enum": ["auto", "en", "es", "zh", "ja", "ko"]},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_EXPLAIN_RESULT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.explain_result",
        "description": "Explain cached Reddit search result metadata by source_id without calling Reddit or storing query history.",
        "parameters": {
            "type": "object",
            "properties": {"source_id": {"type": "string"}},
            "required": ["source_id"],
            "additionalProperties": False,
        },
    },
}

REDDIT_SEARCH_SUBREDDIT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.search_subreddit",
        "description": "Fetch public subreddit metadata through the official Reddit Data API only.",
        "parameters": {
            "type": "object",
            "properties": {"subreddit": {"type": "string"}},
            "required": ["subreddit"],
            "additionalProperties": False,
        },
    },
}

REDDIT_FETCH_SUBREDDIT_INFO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.fetch_subreddit_info",
        "description": "Fetch public subreddit metadata through the official Reddit Data API only.",
        "parameters": {
            "type": "object",
            "properties": {"subreddit": {"type": "string"}},
            "required": ["subreddit"],
            "additionalProperties": False,
        },
    },
}

REDDIT_FETCH_POST_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.fetch_post",
        "description": "Fetch a Reddit post by id or URL through the official Reddit Data API only.",
        "parameters": {
            "type": "object",
            "properties": {"post_id_or_url": {"type": "string"}},
            "required": ["post_id_or_url"],
            "additionalProperties": False,
        },
    },
}

REDDIT_FETCH_COMMENTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.fetch_comments",
        "description": "Fetch Reddit post comments through the official Reddit Data API only.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id_or_url": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                "sort": {"type": "string", "enum": ["confidence", "top", "new", "controversial", "old", "qa"]},
            },
            "required": ["post_id_or_url"],
            "additionalProperties": False,
        },
    },
}

REDDIT_FETCH_THREAD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.fetch_thread",
        "description": "Fetch and normalize a Reddit thread through the official Reddit Data API only.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id_or_url": {"type": "string"},
                "max_comments": {"type": "integer", "minimum": 1, "maximum": 500},
                "sort": {"type": "string", "enum": ["top", "new", "controversial"]},
                "collapse_depth": {"type": "integer", "minimum": 0, "maximum": 20},
            },
            "required": ["post_id_or_url"],
            "additionalProperties": False,
        },
    },
}

REDDIT_THREAD_EXPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.thread_export",
        "description": "Export a normalized Reddit thread into the approved workspace as UNTRUSTED_DOCUMENT.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id_or_url": {"type": "string"},
                "format": {"type": "string", "enum": ["json", "markdown"]},
                "max_comments": {"type": "integer", "minimum": 1, "maximum": 500},
                "sort": {"type": "string", "enum": ["top", "new", "controversial"]},
                "collapse_depth": {"type": "integer", "minimum": 0, "maximum": 20},
            },
            "required": ["post_id_or_url"],
            "additionalProperties": False,
        },
    },
}

REDDIT_SUMMARIZE_THREAD_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.summarize_thread",
        "description": "Summarize a fetched Reddit thread with source IDs, caveats, disagreements, and limitations.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id_or_url": {"type": "string"},
                "max_comments": {"type": "integer", "minimum": 1, "maximum": 500},
                "sort": {"type": "string", "enum": ["top", "new", "controversial"]},
                "collapse_depth": {"type": "integer", "minimum": 0, "maximum": 20},
            },
            "required": ["post_id_or_url"],
            "additionalProperties": False,
        },
    },
}

REDDIT_SUMMARIZE_SEARCH_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.summarize_search",
        "description": "Summarize Reddit search snippets with source IDs and snippet-only evidence labels.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
                "subreddit": {"type": "string"},
                "sort": {"type": "string", "enum": ["relevance", "hot", "top", "new", "comments"]},
                "time_filter": {"type": "string", "enum": ["hour", "day", "week", "month", "year", "all"]},
                "language": {"type": "string", "enum": ["auto", "en", "es", "zh", "ja", "ko"]},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_TOPIC_SUMMARY_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.consensus",
        "description": "Summarize Reddit search snippets for consensus-style discussion with anecdotal caveats.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_PROS_CONS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.pros_cons",
        "description": "Summarize Reddit search snippets as source-grounded pros and cons.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_COMPLAINTS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.complaints",
        "description": "Summarize source-grounded Reddit complaint signals for a product or topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_BUYING_ADVICE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.buying_advice",
        "description": "Summarize source-grounded Reddit buying-advice signals with caveats.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100},
            },
            "required": ["query"],
            "additionalProperties": False,
        },
    },
}

REDDIT_CACHE_CLEAR_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.cache_clear",
        "description": "Clear TTL-bounded local Reddit cache entries.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_CACHE_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.cache_status",
        "description": "Show TTL-bounded local Reddit cache status with counts only.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_RETENTION_STATUS_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.retention_status",
        "description": "Show Reddit retention policy status without raw cached content.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_RETENTION_SWEEP_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.retention_sweep",
        "description": "Delete expired TTL-bounded cached Reddit content.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_PRIVACY_REPORT_SCHEMA = {
    "type": "function",
    "function": {
        "name": "reddit.privacy_report",
        "description": "Show count-only Reddit cache/privacy retention report without raw Reddit content.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
}

REDDIT_SCHEMAS = {
    "reddit.status": REDDIT_STATUS_SCHEMA,
    "reddit.auth_check": REDDIT_AUTH_CHECK_SCHEMA,
    "reddit.search_posts": REDDIT_SEARCH_POSTS_SCHEMA,
    "reddit.search_subreddit": REDDIT_SEARCH_SUBREDDIT_SCHEMA,
    "reddit.fetch_subreddit_info": REDDIT_FETCH_SUBREDDIT_INFO_SCHEMA,
    "reddit.fetch_post": REDDIT_FETCH_POST_SCHEMA,
    "reddit.fetch_comments": REDDIT_FETCH_COMMENTS_SCHEMA,
    "reddit.fetch_thread": REDDIT_FETCH_THREAD_SCHEMA,
    "reddit.thread_export": REDDIT_THREAD_EXPORT_SCHEMA,
    "reddit.summarize_thread": REDDIT_SUMMARIZE_THREAD_SCHEMA,
    "reddit.summarize_search": REDDIT_SUMMARIZE_SEARCH_SCHEMA,
    "reddit.consensus": REDDIT_TOPIC_SUMMARY_SCHEMA,
    "reddit.pros_cons": REDDIT_PROS_CONS_SCHEMA,
    "reddit.complaints": REDDIT_COMPLAINTS_SCHEMA,
    "reddit.buying_advice": REDDIT_BUYING_ADVICE_SCHEMA,
    "reddit.explain_result": REDDIT_EXPLAIN_RESULT_SCHEMA,
    "reddit.cache_status": REDDIT_CACHE_STATUS_SCHEMA,
    "reddit.cache_clear": REDDIT_CACHE_CLEAR_SCHEMA,
    "reddit.retention_status": REDDIT_RETENTION_STATUS_SCHEMA,
    "reddit.retention_sweep": REDDIT_RETENTION_SWEEP_SCHEMA,
    "reddit.privacy_report": REDDIT_PRIVACY_REPORT_SCHEMA,
}


def make_reddit_tools(project_root: str | Path = ".") -> dict[str, Callable[..., dict[str, Any]]]:
    root = Path(project_root)
    provider = default_reddit_provider(root)

    def status(detail: str = "status") -> dict[str, Any]:
        if detail == "doctor":
            return reddit_doctor(project_root=root)
        return reddit_status(project_root=root)

    def auth_check() -> dict[str, Any]:
        return reddit_auth_check(project_root=root)

    def search_posts(
        query: str,
        subreddit: str = "",
        limit: int = 10,
        sort: str = "relevance",
        time_filter: str = "all",
        language: str = "auto",
    ) -> dict[str, Any]:
        return provider.search_posts(
            query,
            subreddit=subreddit or None,
            limit=limit,
            sort=sort,
            time_filter=time_filter,
            language=language,
        )

    def search_subreddit(subreddit: str) -> dict[str, Any]:
        return provider.fetch_subreddit_info(subreddit)

    def fetch_post(post_id_or_url: str) -> dict[str, Any]:
        return provider.fetch_post(post_id_or_url)

    def fetch_comments(post_id_or_url: str, limit: int = 100, sort: str = "confidence") -> dict[str, Any]:
        return provider.fetch_comments(post_id_or_url, limit=limit, sort=sort)

    def fetch_thread(
        post_id_or_url: str,
        max_comments: int = 100,
        sort: str = "top",
        collapse_depth: int = 3,
    ) -> dict[str, Any]:
        return provider.fetch_thread(
            post_id_or_url,
            max_comments=max_comments,
            sort=sort,
            collapse_depth=collapse_depth,
        )

    def thread_export(
        post_id_or_url: str,
        format: str = "json",
        max_comments: int = 100,
        sort: str = "top",
        collapse_depth: int = 3,
    ) -> dict[str, Any]:
        return provider.export_thread(
            post_id_or_url,
            export_format=format,
            max_comments=max_comments,
            sort=sort,
            collapse_depth=collapse_depth,
            workspace_dir=root / "workspace" / "reddit_threads",
        )

    def summarize_thread(
        post_id_or_url: str,
        max_comments: int = 100,
        sort: str = "top",
        collapse_depth: int = 3,
    ) -> dict[str, Any]:
        return provider.summarize_thread(
            post_id_or_url,
            max_comments=max_comments,
            sort=sort,
            collapse_depth=collapse_depth,
        )

    def summarize_search(
        query: str,
        limit: int = 10,
        subreddit: str = "",
        sort: str = "relevance",
        time_filter: str = "all",
        language: str = "auto",
    ) -> dict[str, Any]:
        return provider.summarize_search(
            query,
            limit=limit,
            subreddit=subreddit or None,
            sort=sort,
            time_filter=time_filter,
            language=language,
            summary_kind="search",
        )

    def consensus(query: str, limit: int = 10) -> dict[str, Any]:
        return provider.summarize_search(query, limit=limit, summary_kind="consensus")

    def pros_cons(query: str, limit: int = 10) -> dict[str, Any]:
        return provider.summarize_search(query, limit=limit, summary_kind="pros_cons")

    def complaints(query: str, limit: int = 10) -> dict[str, Any]:
        return provider.summarize_search(query, limit=limit, summary_kind="complaints")

    def buying_advice(query: str, limit: int = 10) -> dict[str, Any]:
        return provider.summarize_search(query, limit=limit, summary_kind="buying_advice")

    def explain_result(source_id: str) -> dict[str, Any]:
        return provider.explain_result(source_id)

    def cache_clear() -> dict[str, Any]:
        return provider.cache_clear()

    def cache_status() -> dict[str, Any]:
        return provider.cache_status()

    def retention_status() -> dict[str, Any]:
        return provider.retention_status()

    def retention_sweep() -> dict[str, Any]:
        return provider.retention_sweep()

    def privacy_report() -> dict[str, Any]:
        return provider.privacy_report()

    return {
        "reddit.status": status,
        "reddit.auth_check": auth_check,
        "reddit.search_posts": search_posts,
        "reddit.search_subreddit": search_subreddit,
        "reddit.fetch_subreddit_info": search_subreddit,
        "reddit.fetch_post": fetch_post,
        "reddit.fetch_comments": fetch_comments,
        "reddit.fetch_thread": fetch_thread,
        "reddit.thread_export": thread_export,
        "reddit.summarize_thread": summarize_thread,
        "reddit.summarize_search": summarize_search,
        "reddit.consensus": consensus,
        "reddit.pros_cons": pros_cons,
        "reddit.complaints": complaints,
        "reddit.buying_advice": buying_advice,
        "reddit.explain_result": explain_result,
        "reddit.cache_status": cache_status,
        "reddit.cache_clear": cache_clear,
        "reddit.retention_status": retention_status,
        "reddit.retention_sweep": retention_sweep,
        "reddit.privacy_report": privacy_report,
    }
