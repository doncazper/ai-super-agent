from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

from agent.forums.reddit.provider import RedditReadOnlyProvider
from agent.forums.reddit.retention import RedditCache
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _events(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_reddit_cache_entry_expires(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    cache.set("entry", {"source_id": "reddit_post_1", "body_text": "ttl bounded"})
    records = cache._read_records()
    records["entry"]["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    cache._write_records(records)

    assert cache.get("entry") is None
    assert cache.status()["expired_count"] == 1


def test_reddit_retention_sweep_deletes_expired_data(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    cache.set("entry", {"source_id": "reddit_post_1", "body_text": "expired"})
    records = cache._read_records()
    records["entry"]["expires_at"] = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    cache._write_records(records)

    result = cache.sweep()

    assert result["entries_deleted"] == 1
    assert cache.status()["entry_count"] == 0


def test_reddit_author_metadata_absent_by_default(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")

    cache.set("entry", {"source_id": "reddit_post_1", "author_display": "public_author", "body_text": "cached"})

    raw_cache = (tmp_path / "cache.json").read_text(encoding="utf-8")
    assert "author_display" not in raw_cache
    assert "public_author" not in raw_cache
    assert cache.privacy_report()["entries_with_author_metadata"] == 0


def test_reddit_privacy_report_is_counts_only(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    cache.set(
        "entry",
        {
            "source_id": "reddit_post_1",
            "title": "Fixture title",
            "body_text": "raw Reddit body should not appear in report",
            "query": "sensitive search phrase",
        },
    )

    report = RedditReadOnlyProvider(cache=cache, env={}).privacy_report()
    rendered = json.dumps(report, sort_keys=True)

    assert report["report_type"] == "counts_only"
    assert report["raw_content_included"] is False
    assert "raw Reddit body should not appear" not in rendered
    assert "sensitive search phrase" not in rendered
    assert "Fixture title" not in rendered


def test_reddit_query_history_not_stored(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    cache.set("entry", {"query": "private query text", "raw_query": "another private query"})

    raw_cache = (tmp_path / "cache.json").read_text(encoding="utf-8")
    report = cache.privacy_report()

    assert "private query text" not in raw_cache
    assert "another private query" not in raw_cache
    assert report["query_history_entries"] == 0
    assert report["query_history_stored"] is False


def test_reddit_removed_content_not_cached(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")

    result = cache.set("entry", {"source_id": "reddit_comment_1", "removed": True, "body_text": "[deleted]"})

    assert result["stored"] is False
    assert result["reason"] == "removed_or_deleted_content"
    assert cache.status()["entry_count"] == 0


def test_reddit_cache_clear_works(tmp_path) -> None:
    cache = RedditCache(tmp_path / "cache.json")
    cache.set("entry", {"source_id": "reddit_post_1", "body_text": "delete me"})

    result = cache.clear()

    assert result["entries_deleted"] == 1
    assert not (tmp_path / "cache.json").exists()


def test_reddit_retention_sweep_audited(tmp_path, monkeypatch, capsys) -> None:
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("AUDIT_LOG_PATH", str(audit_path))

    assert dispatch_cli(["reddit", "retention", "sweep"], project_root=tmp_path) == 0
    output = json.loads(capsys.readouterr().out)
    events = _events(audit_path)

    assert output["status"] == "swept"
    assert events[-1]["tool_name"] == "reddit.retention_sweep"
    assert events[-1]["policy_decision"] == "ALLOW"
    assert "entries_deleted=" in events[-1]["result_summary"]


def test_reddit_retention_status_and_privacy_cli_work(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    assert dispatch_cli(["reddit", "cache", "status"], project_root=tmp_path) == 0
    cache_status = json.loads(capsys.readouterr().out)
    assert cache_status["entry_count"] == 0
    assert cache_status["query_history_stored"] is False

    assert dispatch_cli(["reddit", "retention", "status"], project_root=tmp_path) == 0
    retention_status = json.loads(capsys.readouterr().out)
    assert retention_status["retention_action"] == "status"

    assert dispatch_cli(["reddit", "privacy-report"], project_root=tmp_path) == 0
    privacy_report = json.loads(capsys.readouterr().out)
    assert privacy_report["report_type"] == "counts_only"
    assert privacy_report["raw_content_included"] is False


def test_reddit_retention_commands_registered() -> None:
    for command_id in ("CMD-REDDIT-019", "CMD-REDDIT-020", "CMD-REDDIT-021"):
        record = get_command(command_id)
        assert record is not None
        assert record.example
        assert record.requires_connector == "reddit"
