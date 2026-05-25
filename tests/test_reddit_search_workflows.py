from __future__ import annotations

import json
from pathlib import Path

from agent.forums.reddit.client import RedditApiResponse, parse_rate_limit_headers
from agent.forums.reddit.errors import RedditRateLimitError
from agent.forums.reddit.provider import RedditReadOnlyProvider
from agent.forums.reddit.retention import RedditCache
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _configured_env() -> dict[str, str]:
    return {
        "REDDIT_ENABLED": "true",
        "REDDIT_CLIENT_ID": "client",
        "REDDIT_CLIENT_SECRET": "secret",
        "REDDIT_USER_AGENT": "ai-super-agent:reddit-search:v1 (by /u/local-test)",
        "REDDIT_ACCESS_TOKEN": "access-token",
        "REDDIT_STORE_AUTHOR_METADATA": "false",
    }


class FakeSearchClient:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[dict[str, object]] = []

    def search_posts(self, query, *, subreddit=None, limit=10, sort="relevance", time_filter="all", language="auto"):
        self.calls.append(
            {
                "query": query,
                "subreddit": subreddit,
                "limit": limit,
                "sort": sort,
                "time_filter": time_filter,
                "language": language,
            }
        )
        if self.error:
            raise self.error
        return RedditApiResponse(
            payload=_listing_post("abc123", subreddit=subreddit or "all"),
            status_code=200,
            endpoint="/search",
            network_domains=["oauth.reddit.com"],
            rate_limit=parse_rate_limit_headers({"x-ratelimit-remaining": "58"}),
        )


def _listing_post(post_id: str, *, subreddit: str):
    return {
        "kind": "Listing",
        "data": {
            "children": [
                {
                    "kind": "t3",
                    "data": {
                        "id": post_id,
                        "subreddit": subreddit,
                        "title": "Search workflow result",
                        "url": "https://example.test/result",
                        "permalink": f"/r/{subreddit}/comments/{post_id}/search_workflow_result/",
                        "selftext": "Useful snippet from a public Reddit thread.",
                        "score": 12,
                        "num_comments": 3,
                        "created_utc": 1700000000,
                        "author": "public_author",
                    },
                }
            ]
        },
    }


def test_global_search_workflow_returns_normalized_snippet_only_result(tmp_path: Path) -> None:
    provider = RedditReadOnlyProvider(client=FakeSearchClient(), cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    payload = provider.search_posts("local ai", limit=5, language="zh")

    assert payload["status"] == "ok"
    assert payload["results"][0]["provider"] == "reddit_api"
    assert payload["results"][0]["snippet_only"] is True
    assert payload["results"][0]["evidence_type"] == "snippet_only"
    assert payload["source_references"][0]["evidence_type"] == "snippet_only"
    assert payload["language_support"]["requested_language"] == "zh"
    assert payload["language_support"]["provider_enforced"] is False
    assert payload["query_history_persisted"] is False


def test_subreddit_search_and_sort_time_limit_are_passed_to_api_client(tmp_path: Path) -> None:
    client = FakeSearchClient()
    provider = RedditReadOnlyProvider(client=client, cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    payload = provider.search_posts("gpu deals", subreddit="LocalLLaMA", sort="comments", time_filter="week", limit=7, language="en")

    assert payload["status"] == "ok"
    assert client.calls == [
        {
            "query": "gpu deals",
            "subreddit": "LocalLLaMA",
            "limit": 7,
            "sort": "comments",
            "time_filter": "week",
            "language": "en",
        }
    ]
    assert payload["search_parameters"] == {
        "subreddit": "LocalLLaMA",
        "limit": 7,
        "sort": "comments",
        "time_filter": "week",
        "language": "en",
    }


def test_no_provider_configured_returns_setup_hint_and_no_fallback(tmp_path: Path) -> None:
    provider = RedditReadOnlyProvider(client=FakeSearchClient(), cache=RedditCache(tmp_path / "cache.json"), env={})

    payload = provider.search_posts("local ai")

    assert payload["status"] == "setup_required"
    assert "setup_hint" in payload
    assert payload["web_scraping_fallback_used"] is False
    assert payload["query_history_persisted"] is False


def test_sensitive_query_is_not_persisted_in_cache(tmp_path: Path) -> None:
    query = "private token query should not be readable"
    cache_path = tmp_path / "cache.json"
    provider = RedditReadOnlyProvider(client=FakeSearchClient(), cache=RedditCache(cache_path), env=_configured_env())

    payload = provider.search_posts(query)

    assert payload["query_hash"]
    assert payload["query_history_persisted"] is False
    assert query not in cache_path.read_text(encoding="utf-8")


def test_explain_result_reads_cached_source_without_network_call(tmp_path: Path) -> None:
    client = FakeSearchClient()
    provider = RedditReadOnlyProvider(client=client, cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())
    search_payload = provider.search_posts("local ai")
    source_id = search_payload["results"][0]["source_id"]

    explanation = provider.explain_result(source_id)

    assert explanation["status"] == "ok"
    assert explanation["source_id"] == source_id
    assert explanation["evidence_type"] == "snippet_only"
    assert explanation["snippet_only"] is True
    assert explanation["web_scraping_fallback_used"] is False
    assert len(client.calls) == 1


def test_explain_result_unknown_source_is_metadata_only(tmp_path: Path) -> None:
    provider = RedditReadOnlyProvider(client=FakeSearchClient(), cache=RedditCache(tmp_path / "cache.json"), env=_configured_env())

    explanation = provider.explain_result("reddit_post_missing")

    assert explanation["status"] == "not_found"
    assert explanation["query_history_persisted"] is False
    assert explanation["_audit"]["network_domains"] == []


def test_rate_limit_error_is_structured_for_search_workflow(tmp_path: Path) -> None:
    provider = RedditReadOnlyProvider(
        client=FakeSearchClient(error=RedditRateLimitError("Reddit API rate limit exceeded")),
        cache=RedditCache(tmp_path / "cache.json"),
        env=_configured_env(),
    )

    payload = provider.search_posts("local ai")

    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "reddit_rate_limit_exceeded"
    assert payload["errors"][0]["retryable"] is True


def test_reddit_search_cli_redacts_query_and_accepts_language(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "search", "private sensitive query", "--language", "ja", "--limit", "10"], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert output["status"] == "setup_required"
    assert "private sensitive query" not in audit_text
    assert "[WEB_SEARCH_QUERY_REDACTED]" in audit_text


def test_reddit_explain_result_cli_is_registered_and_safe(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "explain-result", "reddit_post_missing"], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert output["status"] == "not_found"
    assert "reddit.explain_result" in audit_text
    assert "oauth.reddit.com" not in audit_text


def test_reddit_search_workflow_commands_registered() -> None:
    search = get_command("CMD-REDDIT-004")
    explain = get_command("CMD-REDDIT-010")

    assert search is not None
    assert "--language" in search.example
    assert explain is not None
    assert explain.command == "python smart_agent.py reddit explain-result <source_id>"
