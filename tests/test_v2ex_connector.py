from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent.forums.v2ex.cache import V2EXCache
from agent.forums.v2ex.client import V2EXApiResponse, V2EXConfig, V2EXRateLimitStatus
from agent.forums.v2ex.errors import V2EXRateLimitError
from agent.forums.v2ex.provider import READ_CAPABILITIES, WRITE_CAPABILITIES, V2EXReadOnlyProvider
from agent.ui.cli_commands import dispatch_cli
from agent.ui.command_registry import get_command


def _config(*, enabled: bool = True, token: bool = False) -> V2EXConfig:
    return V2EXConfig(
        enabled=enabled,
        token_configured=token,
        timeout_seconds=10,
        max_requests_per_hour=600,
        cache_enabled=True,
        cache_ttl_seconds=86400,
    )


def _response(payload: Any, *, endpoint: str = "/api/test") -> V2EXApiResponse:
    return V2EXApiResponse(
        payload=payload,
        status_code=200,
        endpoint=endpoint,
        endpoint_family="legacy",
        network_domains=["www.v2ex.com"],
        rate_limit=V2EXRateLimitStatus(limit=600, remaining=599, reset=3600, local_used=1, local_limit=600),
    )


class FakeV2EXClient:
    def __init__(self, *, config: V2EXConfig | None = None, error: Exception | None = None) -> None:
        self.config = config or _config()
        self.error = error
        self.calls: list[str] = []

    def _maybe_error(self) -> None:
        if self.error:
            raise self.error

    def nodes(self) -> V2EXApiResponse:
        self.calls.append("nodes")
        self._maybe_error()
        return _response([{"id": 1, "name": "python", "title": "Python", "topics": 42, "url": "/go/python"}])

    def node_topics(self, node_name: str) -> V2EXApiResponse:
        self.calls.append(f"node_topics:{node_name}")
        self._maybe_error()
        return _response(
            [
                {
                    "id": 12345,
                    "title": "中文本地模型讨论",
                    "url": "https://www.v2ex.com/t/12345",
                    "content": "大家在讨论本地模型和工具。",
                    "node": {"name": node_name},
                    "member": {"username": "alice"},
                    "replies": 2,
                    "created": 1700000000,
                }
            ]
        )

    def topic(self, topic_id: str) -> V2EXApiResponse:
        self.calls.append(f"topic:{topic_id}")
        self._maybe_error()
        return _response(
            [
                {
                    "id": topic_id,
                    "title": "V2EX topic",
                    "url": f"https://www.v2ex.com/t/{topic_id}",
                    "content": "Topic body",
                    "node": {"name": "python"},
                    "member": {"username": "bob"},
                    "replies": 1,
                    "created": 1700000000,
                }
            ]
        )

    def replies(self, topic_id: str) -> V2EXApiResponse:
        self.calls.append(f"replies:{topic_id}")
        self._maybe_error()
        return _response(
            [
                {
                    "id": 777,
                    "content": "回复内容",
                    "member": {"username": "carol"},
                    "created": 1700000001,
                }
            ]
        )

    def latest(self) -> V2EXApiResponse:
        self.calls.append("latest")
        return self.node_topics("latest")

    def hot(self) -> V2EXApiResponse:
        self.calls.append("hot")
        return self.node_topics("hot")


class FakeTranslationProvider:
    provider_name = "fake_translation"

    def translate(self, *, prompt: str, source_text: str, source_id: str, source_language: str, target_language: str) -> str:
        return f"[translated {source_language}->{target_language}] {source_text}"


def _provider(tmp_path: Path, client: FakeV2EXClient | None = None) -> V2EXReadOnlyProvider:
    fake_client = client or FakeV2EXClient()
    return V2EXReadOnlyProvider(
        client=fake_client,  # type: ignore[arg-type]
        config=fake_client.config,
        cache=V2EXCache(tmp_path / "v2ex_cache.json", ttl_seconds=86400, enabled=True),
    )


def test_v2ex_doctor_missing_config_is_safe(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    monkeypatch.delenv("V2EX_ENABLED", raising=False)
    monkeypatch.delenv("V2EX_TOKEN", raising=False)

    status = dispatch_cli(["v2ex", "doctor"], project_root=tmp_path)
    payload = json.loads(capsys.readouterr().out)
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")

    assert status == 0
    assert payload["enabled"] is False
    assert payload["network_call_performed"] is False
    assert payload["write_capabilities_allowed"] is False
    assert "V2EX_ENABLED=true" in payload["setup_hint"]
    assert "v2ex.status" in audit_text
    assert "www.v2ex.com" not in audit_text


def test_v2ex_token_redacted_in_status(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    monkeypatch.setenv("V2EX_ENABLED", "true")
    monkeypatch.setenv("V2EX_TOKEN", "v2ex-secret-token")

    assert dispatch_cli(["v2ex", "status"], project_root=tmp_path) == 0
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert payload["token_configured"] is True
    assert payload["token_printed"] is False
    assert "v2ex-secret-token" not in output


def test_v2ex_node_topics_mock_normalized(tmp_path: Path) -> None:
    result = _provider(tmp_path).node_topics("python", limit=1)

    assert result["status"] == "ok"
    assert result["provider"] == "v2ex_api"
    assert result["result_count"] == 1
    thread = result["threads"][0]
    assert thread["provider"] == "v2ex_api"
    assert thread["post"]["provider_post_id"] == "12345"
    assert thread["trust_level"] == "UNTRUSTED_WEB"
    assert "author_display" not in thread["post"]
    assert thread["source_references"][0]["url"] == "https://www.v2ex.com/t/12345"


def test_v2ex_topic_mock_normalized(tmp_path: Path) -> None:
    result = _provider(tmp_path).topic("12345")

    assert result["status"] == "ok"
    assert result["thread"]["provider_thread_id"] == "12345"
    assert result["thread"]["post"]["title"] == "V2EX topic"
    assert result["source_references"][0]["url"].endswith("/t/12345")


def test_v2ex_replies_mock_normalized(tmp_path: Path) -> None:
    result = _provider(tmp_path).replies("12345", limit=10)

    assert result["status"] == "ok"
    assert result["comment_count"] == 1
    assert result["comments"][0]["provider_comment_id"] == "777"
    assert result["comments"][0]["trust_level"] == "UNTRUSTED_WEB"
    assert "author_display" not in result["comments"][0]


def test_v2ex_rate_limit_error_is_structured(tmp_path: Path) -> None:
    provider = _provider(tmp_path, FakeV2EXClient(error=V2EXRateLimitError("local limit exceeded")))

    result = provider.hot()

    assert result["status"] == "error"
    assert result["error"]["code"] == "v2ex_rate_limit_exceeded"
    assert result["error"]["retryable"] is True


def test_v2ex_translation_workflow_integration_mocked(tmp_path: Path) -> None:
    result = _provider(tmp_path).node_topics(
        "python",
        limit=1,
        detect=True,
        translate_to="en",
        translation_provider=FakeTranslationProvider(),
    )

    post = result["threads"][0]["post"]
    assert post["language"] == "zh"
    assert post["translation"]["translation_label"] == "MODEL_GENERATED_TRANSLATION"
    assert post["translation"]["provider"] == "fake_translation"
    assert result["language_workflow"]["memory_written"] is False


def test_v2ex_has_no_write_endpoints() -> None:
    assert WRITE_CAPABILITIES == ()
    assert all("write" not in capability and "post.create" not in capability for capability in READ_CAPABILITIES)


def test_v2ex_command_registry_updated() -> None:
    expected = {
        "CMD-V2EX-001": "v2ex doctor",
        "CMD-V2EX-002": "v2ex nodes",
        "CMD-V2EX-003": "v2ex node",
        "CMD-V2EX-004": "v2ex topic",
        "CMD-V2EX-005": "v2ex replies",
        "CMD-V2EX-006": "v2ex latest",
        "CMD-V2EX-007": "v2ex hot",
    }
    for command_id, text in expected.items():
        record = get_command(command_id)
        assert record is not None
        assert text in record.command
        assert record.example
        assert record.risk_level in {"SAFE", "MEDIUM"}
        assert record.toolbroker_path.startswith("yes via v2ex.")
