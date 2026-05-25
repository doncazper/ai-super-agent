from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.forums.chinese_discovery import (
    build_site_filter_queries,
    fetch_chinese_forum_url,
    list_chinese_forum_providers,
    normalize_sites,
    research_chinese_forums,
    search_chinese_forums,
)
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _search_backend(
    *,
    query: str,
    max_results: int | None = None,
    locale: str | None = None,
    language: str | None = None,
    safe_search: bool | None = None,
    provider: str | None = None,
    freshness: str | None = None,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "provider": "mock_search",
        "results": [
            {
                "title": "本地模型讨论",
                "url": "https://www.v2ex.com/t/12345",
                "snippet": "大家讨论本地模型，重点是显存和速度。",
                "source": "mock",
                "retrieved_at": "2026-05-25T00:00:00+00:00",
            }
        ][: max_results or 1],
        "query_history_persisted": False,
        "_audit": {"network_domains": ["search.local"], "result_summary": f"mock search {query}"},
    }


def _blocked_fetcher(**kwargs: Any) -> dict[str, Any]:
    return {
        "status": "ok",
        "url": kwargs["url"],
        "final_url": kwargs["url"],
        "title": "请登录后继续",
        "text": "请登录后查看内容。验证码验证。",
        "retrieved_at": "2026-05-25T00:00:00+00:00",
        "trust_level": "UNTRUSTED_WEB",
        "_audit": {"network_domains": ["www.zhihu.com"], "result_summary": "mock blocked"},
    }


def _public_fetcher(**kwargs: Any) -> dict[str, Any]:
    return {
        "status": "ok",
        "url": kwargs["url"],
        "final_url": kwargs["url"],
        "title": "本地模型讨论",
        "text": "大家讨论本地模型。体验不错，但需要注意显存和驱动版本。这个页面没有要求登录。",
        "retrieved_at": "2026-05-25T00:00:00+00:00",
        "trust_level": "UNTRUSTED_WEB",
        "source_metadata": {"title": "本地模型讨论"},
        "_audit": {"network_domains": ["www.v2ex.com"], "result_summary": "mock fetch ok"},
    }


class FakeTranslationProvider:
    provider_name = "fake_translation"

    def translate(self, *, prompt: str, source_text: str, source_id: str, source_language: str, target_language: str) -> str:
        return "People discuss local models; the experience is good but VRAM and driver versions matter."


def test_site_filter_query_generated() -> None:
    sites = normalize_sites("zhihu,v2ex,tieba")
    queries = build_site_filter_queries("本地模型", sites)

    assert queries == [
        ("zhihu", "本地模型 site:zhihu.com"),
        ("v2ex", "本地模型 site:v2ex.com"),
        ("baidu_tieba", "本地模型 site:tieba.baidu.com"),
    ]


def test_search_uses_site_filters_and_labels_snippets() -> None:
    payload = search_chinese_forums("本地模型", sites="v2ex", search_backend=_search_backend)

    assert payload["status"] == "ok"
    assert payload["site_filter_search_only"] is True
    assert payload["results"][0]["evidence_type"] == "search_snippet"
    assert payload["results"][0]["trust_level"] == "UNTRUSTED_WEB"
    assert payload["results"][0]["language"] == "zh"
    assert payload["memory_written"] is False
    assert payload["search_history_persisted"] is False
    assert payload["login_cookies_used"] is False


def test_blocked_page_reported_unavailable() -> None:
    payload = fetch_chinese_forum_url("https://www.zhihu.com/question/123", fetch_backend=_blocked_fetcher)

    assert payload["status"] == "unavailable"
    assert payload["blocked_reason"] == "login_captcha_or_block_page"
    assert payload["captcha_bypass_attempted"] is False
    assert payload["login_cookies_used"] is False


def test_public_fixture_fetched_and_language_detected() -> None:
    payload = fetch_chinese_forum_url("https://www.v2ex.com/t/12345", fetch_backend=_public_fetcher)

    assert payload["status"] == "ok"
    assert payload["provider"] == "v2ex"
    assert payload["language_detection"]["language"] == "zh"
    assert "本地模型" in payload["summary"]
    assert payload["source_references"][0]["url"] == "https://www.v2ex.com/t/12345"


def test_translation_triggered_with_mock_provider() -> None:
    payload = fetch_chinese_forum_url(
        "https://www.v2ex.com/t/12345",
        translate_to="en",
        fetch_backend=_public_fetcher,
        translation_provider=FakeTranslationProvider(),
    )

    assert payload["status"] == "ok"
    assert payload["translation"]["translation_label"] == "MODEL_GENERATED_TRANSLATION"
    assert payload["translation"]["provider"] == "fake_translation"
    assert payload["translation"]["memory_written"] is False


def test_research_fetches_public_fixture_and_reports_no_memory() -> None:
    payload = research_chinese_forums(
        "本地模型",
        sites="v2ex",
        search_backend=_search_backend,
        fetch_backend=_public_fetcher,
        translation_provider=FakeTranslationProvider(),
    )

    assert payload["status"] == "ok"
    assert payload["fetched_sources"][0]["status"] == "ok"
    assert payload["translations"][0]["translation_label"] == "MODEL_GENERATED_TRANSLATION"
    assert payload["memory_written"] is False
    assert payload["search_history_persisted"] is False
    assert payload["paid_provider_used"] is False


def test_no_login_cookies_or_browser_session_used() -> None:
    providers = list_chinese_forum_providers()
    fetched = fetch_chinese_forum_url("https://www.v2ex.com/t/12345", fetch_backend=_public_fetcher)

    assert providers["no_login_cookies"] is True
    assert fetched["login_cookies_used"] is False
    assert fetched["browser_session_used"] is False
    assert fetched["captcha_bypass_attempted"] is False


def test_cn_forums_cli_and_audit(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    exit_code = dispatch_cli(["cn-forums", "providers"], project_root=tmp_path)
    payload = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["provider_count"] == 7
    assert "cn_forums.providers" in audit_text
    assert "zhihu.com" not in audit_text


def test_cn_forum_command_registry_updated() -> None:
    expected = {
        "CMD-CNFORUMS-001": "cn-forums search",
        "CMD-CNFORUMS-002": "cn-forums fetch",
        "CMD-CNFORUMS-003": "cn-forums research",
        "CMD-CNFORUMS-004": "cn-forums providers",
    }
    for command_id, text in expected.items():
        record = get_command(command_id)
        assert record is not None
        assert text in record.command
        assert record.example
        assert record.risk_level in {"SAFE", "MEDIUM"}
        assert record.memory_behavior == "no memory write"
