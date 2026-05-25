from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import httpx

from agent.config.loader import load_capabilities_config
from agent.forums.reddit.client import RedditApiResponse, parse_rate_limit_headers
from agent.forums.reddit.errors import RedditRateLimitError
from agent.forums.reddit.models import RedditPost, utc_now_iso
from agent.forums.reddit.provider import RedditReadOnlyProvider
from agent.forums.reddit.retention import RedditCache, reddit_cache_key
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _configured_env() -> dict[str, str]:
    return {
        "REDDIT_ENABLED": "true",
        "REDDIT_CLIENT_ID": "client",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "ai-super-agent:reddit-read-only:v1 (by /u/local-test)",
        "REDDIT_ACCESS_TOKEN": "access-token",
        "REDDIT_STORE_AUTHOR_METADATA": "false",
    }


class FakeRedditClient:
    def __init__(self, response: RedditApiResponse | None = None, *, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls: list[tuple[str, dict[str, object]]] = []

    def search_posts(self, query, *, subreddit=None, limit=10, sort="relevance", time_filter="all", language="auto"):
        self.calls.append(
            (
                "search_posts",
                {
                    "query": query,
                    "subreddit": subreddit,
                    "limit": limit,
                    "sort": sort,
                    "time_filter": time_filter,
                    "language": language,
                },
            )
        )
        if self.error:
            raise self.error
        return self.response

    def fetch_post(self, post_id_or_url):
        self.calls.append(("fetch_post", {"post_id_or_url": post_id_or_url}))
        if self.error:
            raise self.error
        return self.response

    def fetch_thread(self, post_id_or_url, *, sort="confidence", limit=100):
        self.calls.append(("fetch_thread", {"post_id_or_url": post_id_or_url, "sort": sort, "limit": limit}))
        if self.error:
            raise self.error
        return self.response

    def fetch_subreddit_info(self, subreddit):
        self.calls.append(("fetch_subreddit_info", {"subreddit": subreddit}))
        if self.error:
            raise self.error
        return self.response


def _api_response(payload) -> RedditApiResponse:
    return RedditApiResponse(
        payload=payload,
        status_code=200,
        endpoint="/mock",
        network_domains=["oauth.reddit.com"],
        rate_limit=parse_rate_limit_headers(
            {
                "x-ratelimit-used": "1",
                "x-ratelimit-remaining": "59",
                "x-ratelimit-reset": "60",
            }
        ),
    )


def _listing_post(post_id: str = "abc123", *, body: str = "Helpful answer", author: str = "public_author"):
    return {
        "kind": "Listing",
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": post_id,
                        "subreddit": "LocalAI",
                        "title": "Useful Reddit discussion",
                        "url": "https://example.test/post",
                        "permalink": f"/r/LocalAI/comments/{post_id}/useful_reddit_discussion/",
                        "selftext": body,
                        "score": 42,
                        "num_comments": 7,
                        "created_utc": 1700000000,
                        "author": author,
                    },
                }
            ]
        },
    }


def test_search_posts_normalizes_mock_response(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    provider = RedditReadOnlyProvider(client=FakeRedditClient(_api_response(_listing_post())), cache=cache, env=_configured_env())

    result = provider.search_posts("local llm", limit=5)

    assert result["status"] == "ok"
    assert result["results"][0]["provider"] == "reddit_api"
    assert result["results"][0]["trust_level"] == "UNTRUSTED_WEB"
    assert "author_display" not in result["results"][0]
    assert result["results"][0]["permalink"].startswith("https://www.reddit.com/")
    assert result["results"][0]["snippet_only"] is True
    assert result["results"][0]["evidence_type"] == "snippet_only"
    assert result["result_data_state"] == "search_snippet"
    assert result["source_references"][0]["source_id"] == result["results"][0]["source_id"]
    assert result["query_history_persisted"] is False
    assert result["_audit"]["network_domains"] == ["oauth.reddit.com"]


def test_fetch_post_normalizes_mock_response(tmp_path) -> None:
    provider = RedditReadOnlyProvider(client=FakeRedditClient(_api_response(_listing_post("p123"))), cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    result = provider.fetch_post("p123")

    assert result["status"] == "ok"
    assert result["post"]["reddit_id"] == "p123"
    assert result["post"]["title"] == "Useful Reddit discussion"
    assert result["post"]["trust_level"] == "UNTRUSTED_WEB"
    assert result["source_references"][0]["url"].startswith("https://www.reddit.com/")


def test_fetch_comments_handles_nested_comments(tmp_path) -> None:
    payload = [
        _listing_post("p999"),
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
                                        }
                                    ]
                                },
                            },
                        },
                    }
                ]
            },
        },
    ]
    provider = RedditReadOnlyProvider(client=FakeRedditClient(_api_response(payload)), cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    result = provider.fetch_comments("https://www.reddit.com/r/LocalAI/comments/p999/title/")

    assert result["status"] == "ok"
    assert result["post"]["reddit_id"] == "p999"
    assert [comment["reddit_id"] for comment in result["comments"]] == ["c1", "c2"]
    assert result["comments"][1]["depth"] == 1


def test_deleted_removed_content_handled_and_author_redacted_by_default(tmp_path) -> None:
    provider = RedditReadOnlyProvider(
        client=FakeRedditClient(_api_response(_listing_post("gone", body="[deleted]", author="[deleted]"))),
        cache=RedditCache(tmp_path / "cache.json"),
        env=_configured_env(),
    )

    result = provider.fetch_post("gone")

    assert result["post"]["removed"] is True
    assert result["post"]["body_text"] == ""
    assert "author_display" not in result["post"]
    assert provider.cache.status()["entry_count"] == 0


def test_rate_limit_headers_parsed() -> None:
    status = parse_rate_limit_headers({"x-ratelimit-used": "3", "x-ratelimit-remaining": "0", "x-ratelimit-reset": "20"})

    assert status.used == 3
    assert status.remaining == 0
    assert status.reset_seconds == 20
    assert status.exceeded is True


def test_rate_limit_exceeded_returns_structured_error(tmp_path) -> None:
    provider = RedditReadOnlyProvider(
        client=FakeRedditClient(error=RedditRateLimitError("Reddit API rate limit exceeded")),
        cache=RedditCache(tmp_path / "cache.json"),
        env=_configured_env(),
    )

    result = provider.search_posts("local llm")

    assert result["status"] == "error"
    assert result["errors"][0]["code"] == "reddit_rate_limit_exceeded"
    assert result["errors"][0]["retryable"] is True


def test_cache_ttl_works(tmp_path) -> None:
    client = FakeRedditClient(_api_response(_listing_post("cached")))
    provider = RedditReadOnlyProvider(client=client, cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    first = provider.search_posts("cache me")
    second = provider.search_posts("cache me")

    assert first["cache_used"] is False
    assert second["cache_used"] is True
    assert len(client.calls) == 1

    records = provider.cache._read_records()
    key = reddit_cache_key("search_posts", query="cache me", subreddit="|".join(["", "relevance", "all", "auto", "10"]))
    records[key]["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    provider.cache._write_records(records)
    third = provider.search_posts("cache me")

    assert third["cache_used"] is False
    assert len(client.calls) == 2


def test_retention_sweep_deletes_expired_cached_content(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    key = "expired"
    cache.set(key, RedditPost(source_id="src", reddit_id="p1", subreddit="x", title="t", url="u", permalink="p", body_text="body").to_dict())
    records = cache._read_records()
    records[key]["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    cache._write_records(records)

    result = cache.sweep()

    assert result["entries_deleted"] == 1
    assert cache.status()["entry_count"] == 0


def test_no_write_capabilities_exist() -> None:
    tools = load_capabilities_config("config/capabilities.yaml")["tools"]

    for forbidden in ("reddit.post", "reddit.comment", "reddit.vote", "reddit.dm", "reddit.moderate"):
        assert forbidden not in tools


def test_reddit_cli_routes_through_broker_without_config(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "search", "local llm"], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert output["status"] == "setup_required"
    assert output["web_scraping_fallback_used"] is False
    assert "reddit.search_posts" in audit_text
    assert "local llm" not in audit_text


def test_reddit_commands_registered() -> None:
    for command_id in (
        "CMD-REDDIT-004",
        "CMD-REDDIT-005",
        "CMD-REDDIT-006",
        "CMD-REDDIT-007",
        "CMD-REDDIT-008",
        "CMD-REDDIT-009",
        "CMD-REDDIT-010",
    ):
        record = get_command(command_id)
        assert record is not None
        assert record.example
        assert record.requires_connector == "reddit"


def test_reddit_http_client_uses_oauth_api_only() -> None:
    seen_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_urls.append(str(request.url))
        return httpx.Response(200, json={"data": {"children": []}}, headers={"x-ratelimit-remaining": "12"})

    from agent.forums.reddit.client import RedditApiClient

    client = RedditApiClient.from_env(env=_configured_env(), transport=httpx.MockTransport(handler))
    response = client.search_posts("privacy")

    assert response.status_code == 200
    assert seen_urls
    assert all(url.startswith("https://oauth.reddit.com/") for url in seen_urls)
    assert not any("/submit" in url or "/api/comment" in url or "/api/vote" in url for url in seen_urls)
