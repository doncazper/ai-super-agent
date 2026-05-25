from __future__ import annotations

import json
from pathlib import Path

from agent.forums.reddit.client import RedditApiResponse, parse_post_id, parse_rate_limit_headers
from agent.forums.reddit.provider import RedditReadOnlyProvider
from agent.forums.reddit.retention import RedditCache
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _configured_env() -> dict[str, str]:
    return {
        "REDDIT_ENABLED": "true",
        "REDDIT_CLIENT_ID": "client",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "ai-super-agent:reddit-thread:v1 (by /u/local-test)",
        "REDDIT_ACCESS_TOKEN": "access-token",
        "REDDIT_STORE_AUTHOR_METADATA": "false",
    }


class FakeThreadClient:
    def __init__(self, payload) -> None:
        self.payload = payload
        self.calls: list[tuple[str, dict[str, object]]] = []

    def fetch_thread(self, post_id_or_url, *, sort="confidence", limit=100):
        self.calls.append(("fetch_thread", {"post_id_or_url": post_id_or_url, "sort": sort, "limit": limit}))
        return RedditApiResponse(
            payload=self.payload,
            status_code=200,
            endpoint="/mock/comments",
            network_domains=["oauth.reddit.com"],
            rate_limit=parse_rate_limit_headers(
                {
                    "x-ratelimit-used": "1",
                    "x-ratelimit-remaining": "59",
                    "x-ratelimit-reset": "60",
                }
            ),
        )


def _thread_payload() -> list[dict[str, object]]:
    return [
        {
            "kind": "Listing",
            "data": {
                "children": [
                    {
                        "kind": "t3",
                        "data": {
                            "id": "p999",
                            "subreddit": "LocalAI",
                            "title": "Useful Reddit discussion",
                            "url": "https://example.test/post",
                            "permalink": "/r/LocalAI/comments/p999/useful_reddit_discussion/",
                            "selftext": "Thread body",
                            "score": 42,
                            "num_comments": 3,
                            "created_utc": 1700000000,
                            "author": "post_author",
                        },
                    }
                ]
            },
        },
        {
            "kind": "Listing",
            "data": {
                "children": [
                    {
                        "kind": "t1",
                        "data": {
                            "id": "c1",
                            "subreddit": "LocalAI",
                            "body": "Top comment",
                            "permalink": "/r/LocalAI/comments/p999/x/c1/",
                            "score": 10,
                            "author": "commenter",
                            "replies": {
                                "kind": "Listing",
                                "data": {
                                    "children": [
                                        {
                                            "kind": "t1",
                                            "data": {
                                                "id": "c2",
                                                "subreddit": "LocalAI",
                                                "body": "Nested reply",
                                                "permalink": "/r/LocalAI/comments/p999/x/c2/",
                                                "score": 4,
                                                "author": "reply_author",
                                            },
                                        },
                                        {
                                            "kind": "t1",
                                            "data": {
                                                "id": "c3",
                                                "subreddit": "LocalAI",
                                                "body": "[removed]",
                                                "permalink": "/r/LocalAI/comments/p999/x/c3/",
                                                "score": 0,
                                                "author": "[deleted]",
                                            },
                                        },
                                    ]
                                },
                            },
                        },
                    }
                ]
            },
        },
    ]


def _provider(tmp_path: Path) -> RedditReadOnlyProvider:
    return RedditReadOnlyProvider(
        client=FakeThreadClient(_thread_payload()),
        cache=RedditCache(tmp_path / "cache.json"),
        env=_configured_env(),
    )


def test_reddit_thread_url_and_id_parsing() -> None:
    assert parse_post_id("t3_p999") == "p999"
    assert parse_post_id("https://www.reddit.com/r/LocalAI/comments/p999/useful_reddit_discussion/") == "p999"


def test_thread_fetch_normalizes_tree_and_flattened_comments(tmp_path) -> None:
    provider = _provider(tmp_path)

    result = provider.fetch_thread("p999", max_comments=10, sort="top", collapse_depth=3)

    assert result["status"] == "ok"
    assert result["post"]["reddit_id"] == "p999"
    assert [comment["reddit_id"] for comment in result["flattened_comments"]] == ["c1", "c2", "c3"]
    assert result["comment_tree"][0]["reddit_id"] == "c1"
    assert [reply["reddit_id"] for reply in result["comment_tree"][0]["replies"]] == ["c2", "c3"]
    assert result["flattened_comments"][1]["depth"] == 1
    assert result["source_references"][0]["source_id"] == result["post"]["source_id"]
    assert result["trust_level"] == "UNTRUSTED_WEB"
    assert result["_audit"]["network_domains"] == ["oauth.reddit.com"]
    assert result["web_scraping_fallback_used"] is False


def test_thread_fetch_enforces_max_comments_and_handles_removed(tmp_path) -> None:
    provider = _provider(tmp_path)

    limited = provider.fetch_thread("p999", max_comments=2, sort="top", collapse_depth=3)
    full = provider.fetch_thread("p999", max_comments=10, sort="new", collapse_depth=3)

    assert [comment["reddit_id"] for comment in limited["flattened_comments"]] == ["c1", "c2"]
    assert limited["truncation_info"]["truncated"] is True
    removed = next(comment for comment in full["flattened_comments"] if comment["reddit_id"] == "c3")
    assert removed["removed"] is True
    assert removed["body_text"] == ""
    assert "author_display" not in json.dumps(full)


def test_thread_export_writes_only_inside_workspace_and_redacts_authors(tmp_path) -> None:
    provider = _provider(tmp_path)
    workspace = tmp_path / "workspace"

    result = provider.export_thread(
        "https://www.reddit.com/r/LocalAI/comments/p999/useful_reddit_discussion/",
        export_format="json",
        max_comments=10,
        sort="top",
        collapse_depth=3,
        workspace_dir=workspace,
    )

    output_path = Path(result["path"])
    assert result["status"] == "ok"
    assert output_path.is_file()
    assert workspace.resolve() in output_path.resolve().parents
    assert result["document_trust_level"] == "UNTRUSTED_DOCUMENT"
    exported = output_path.read_text(encoding="utf-8")
    assert "post_author" not in exported
    assert "commenter" not in exported
    assert "UNTRUSTED_DOCUMENT" in exported
    assert result["_audit"]["files_written"] == [str(output_path)]


def test_reddit_thread_cli_audits_fetch_and_export_without_config(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "thread", "p999", "--max-comments", "5"], project_root=tmp_path) == 0
    thread_output = json.loads(capsys.readouterr().out)
    assert thread_output["status"] == "setup_required"

    assert dispatch_cli(["reddit", "thread-export", "p999", "--format", "markdown"], project_root=tmp_path) == 0
    export_output = json.loads(capsys.readouterr().out)
    assert export_output["status"] == "setup_required"

    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "reddit.fetch_thread" in audit_text
    assert "reddit.thread_export" in audit_text
    assert "oauth.reddit.com/comments" not in audit_text


def test_reddit_thread_commands_registered() -> None:
    for command_id in ("CMD-REDDIT-011", "CMD-REDDIT-012"):
        record = get_command(command_id)
        assert record is not None
        assert record.example
        assert record.requires_connector == "reddit"
