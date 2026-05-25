from __future__ import annotations

import json
from pathlib import Path

from agent.forums.models import ForumProviderStatus
from agent.forums.registry import ForumProviderRegistry
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def test_forum_provider_registry_loads() -> None:
    registry = ForumProviderRegistry()
    providers = registry.list_providers()

    assert len(providers) >= 11
    assert "reddit" in {provider.provider_id for provider in providers}


def test_reddit_provider_registered_read_only() -> None:
    provider = ForumProviderRegistry().get_provider("reddit")

    assert provider.provider_id == "reddit"
    assert provider.official_api_available is True
    assert provider.auth_required is True
    assert "reddit.search_posts" in provider.read_capabilities
    assert provider.write_capabilities == ()
    assert provider.default_enabled is False
    assert provider.access_policy["web_scraping_fallback_allowed"] is False


def test_v2ex_provider_registered_as_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("V2EX_ENABLED", raising=False)
    provider = ForumProviderRegistry().get_provider("v2ex")

    assert provider.provider_id == "v2ex"
    assert provider.status == ForumProviderStatus.DISABLED
    assert provider.official_api_available is True
    assert provider.write_capabilities == ()
    assert provider.source_type == "documented_api"
    assert "V2EX_ENABLED=true" in provider.setup_hint


def test_chinese_platforms_are_discovery_only_site_filter_stubs() -> None:
    registry = ForumProviderRegistry()

    for provider_id in ("zhihu", "baidu_tieba", "douban_groups", "xiaohongshu", "weibo", "nga"):
        provider = registry.get_provider(provider_id)
        assert provider.status == ForumProviderStatus.DISCOVERY_ONLY
        assert provider.source_type == "discovery_only_search"
        assert provider.access_policy["discovery_method"] == "approved_search_site_filter"
        assert str(provider.access_policy["site_filter"]).startswith("site:")
        assert provider.access_policy["scraping_allowed"] is False
        assert provider.write_capabilities == ()


def test_unknown_provider_returns_structured_unsupported() -> None:
    provider = ForumProviderRegistry().get_provider("unknown_forum")

    assert provider.status == ForumProviderStatus.UNSUPPORTED
    assert provider.read_capabilities == ()
    assert provider.write_capabilities == ()
    assert provider.access_policy["scraping_allowed"] is False


def test_status_and_doctor_do_not_perform_personal_or_logged_in_reads(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    status_code = dispatch_cli(["forums", "status", "zhihu"], project_root=tmp_path)
    status_payload = json.loads(capsys.readouterr().out)
    doctor_code = dispatch_cli(["forums", "doctor"], project_root=tmp_path)
    doctor_payload = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert status_code == 0
    assert doctor_code == 0
    assert status_payload["status_check"]["personal_data_accessed"] is False
    assert status_payload["status_check"]["logged_in_read_performed"] is False
    assert status_payload["status_check"]["network_call_performed"] is False
    assert doctor_payload["status_checks_personal_data"] is False
    assert doctor_payload["logged_in_read_performed"] is False
    assert doctor_payload["network_call_performed"] is False
    assert "forums.status" in audit_text
    assert "forums.doctor" in audit_text
    assert "oauth.reddit.com" not in audit_text
    assert "zhihu.com" not in audit_text


def test_forums_providers_and_capabilities_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))

    providers_code = dispatch_cli(["forums", "providers"], project_root=tmp_path)
    providers_payload = json.loads(capsys.readouterr().out)
    capabilities_code = dispatch_cli(["forums", "capabilities", "reddit"], project_root=tmp_path)
    capabilities_payload = json.loads(capsys.readouterr().out)

    assert providers_code == 0
    assert capabilities_code == 0
    assert providers_payload["provider_count"] >= 11
    assert providers_payload["write_capabilities_enabled"] is False
    assert capabilities_payload["provider_id"] == "reddit"
    assert capabilities_payload["write_capabilities"] == []
    assert capabilities_payload["write_capabilities_deferred"] is True


def test_forum_provider_commands_registered() -> None:
    expected = {
        "CMD-FORUMS-003": "forums providers",
        "CMD-FORUMS-004": "forums status",
        "CMD-FORUMS-005": "forums doctor",
        "CMD-FORUMS-006": "forums capabilities",
    }
    for command_id, text in expected.items():
        record = get_command(command_id)
        assert record is not None
        assert text in record.command
        assert record.risk_level == "SAFE"
        assert record.example
