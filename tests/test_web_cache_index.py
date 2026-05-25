from __future__ import annotations

import json

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.registry import default_registry
from agent.web_acquisition.cache import WebCacheStore
from agent.web_acquisition.dedupe import dedupe_sources
from agent.web_acquisition.index import LocalWebIndex


def cache_capabilities() -> dict[str, Capability]:
    return {
        "web.cache.lookup": Capability("web.cache.lookup", RiskLevel.LOW),
        "web.cache.clear": Capability("web.cache.clear", RiskLevel.LOW),
        "web.cache.status": Capability("web.cache.status", RiskLevel.SAFE),
        "web.index.search": Capability("web.index.search", RiskLevel.LOW),
        "web.index.add_public_source": Capability("web.index.add_public_source", RiskLevel.LOW),
        "web.index.rebuild": Capability("web.index.rebuild", RiskLevel.LOW),
    }


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def make_broker(tmp_path) -> ToolBroker:
    return ToolBroker(
        default_registry(project_root=tmp_path),
        PolicyEngine(cache_capabilities()),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def public_source(**overrides: object) -> dict[str, object]:
    source: dict[str, object] = {
        "title": "Cacheable Public Article",
        "url": "https://example.com/articles/cache",
        "snippet": "A public source about local web cache behavior.",
        "provider": "fixture",
        "retrieved_at": "2026-05-24T00:00:00+00:00",
        "trust_level": "UNTRUSTED_WEB",
        "source_metadata": {"source_type": "fixture"},
    }
    source.update(overrides)
    return source


def test_cache_hit_before_provider_call(tmp_path) -> None:
    store = WebCacheStore(tmp_path / "cache.json")
    calls = {"count": 0}

    def loader() -> dict[str, object]:
        calls["count"] += 1
        return public_source()

    first = store.get_or_refresh(url="https://example.com/articles/cache", provider="fixture", loader=loader)
    second = store.get_or_refresh(url="https://example.com/articles/cache", provider="fixture", loader=loader)

    assert first["loaded"] is True
    assert second["status"] == "hit"
    assert second["cache_used"] is True
    assert calls["count"] == 1


def test_cache_expiry_refreshes(tmp_path) -> None:
    store = WebCacheStore(tmp_path / "cache.json")
    store.put_public_source(public_source(title="Expired"), provider="fixture", ttl_seconds=-1)
    calls = {"count": 0}

    def loader() -> dict[str, object]:
        calls["count"] += 1
        return public_source(title="Fresh")

    refreshed = store.get_or_refresh(url="https://example.com/articles/cache", provider="fixture", loader=loader)

    assert refreshed["status"] == "refreshed"
    assert refreshed["loaded"] is True
    assert calls["count"] == 1
    assert refreshed["entry"]["title"] == "Fresh"


def test_dedupe_avoids_duplicate_source() -> None:
    sources = [
        public_source(snippet="same"),
        public_source(url="https://example.com/articles/cache?utm_source=test", snippet="same"),
    ]

    deduped = dedupe_sources(sources)

    assert len(deduped) == 1
    assert deduped[0]["content_hash"]


def test_index_search_returns_cached_source(tmp_path) -> None:
    index = LocalWebIndex(tmp_path / "index.json")
    add_result = index.add_public_source(public_source())

    result = index.search("local cache")

    assert add_result["indexed"] is True
    assert result["status"] == "ok"
    assert result["query_persisted"] is False
    assert result["results"][0]["title"] == "Cacheable Public Article"
    assert result["results"][0]["trust_level"] == "UNTRUSTED_WEB"


def test_personal_content_not_cached(tmp_path) -> None:
    store = WebCacheStore(tmp_path / "cache.json")
    result = store.put_public_source(public_source(source_metadata={"authenticated": True}))

    assert result["stored"] is False
    assert result["status"] == "denied"
    assert store.status()["entry_count"] == 0


def test_clear_works_through_toolbroker(tmp_path) -> None:
    broker = make_broker(tmp_path)
    add = broker.execute(call("web.index.add_public_source", {"source": public_source()}))
    assert add.allowed is True

    cleared = broker.execute(call("web.cache.clear", {}))
    payload = json.loads(cleared.content)

    assert cleared.allowed is True
    assert payload["status"] == "cleared"
    assert payload["cache"]["entries_deleted"] == 1


def test_no_sensitive_query_stored_or_audited(tmp_path) -> None:
    broker = make_broker(tmp_path)
    result = broker.execute(
        call(
            "web.index.add_public_source",
            {"source": public_source(), "query": "secret token query", "provider": "fixture"},
        )
    )

    assert result.allowed is True
    cache_text = (tmp_path / "data" / "web_cache" / "cache.json").read_text(encoding="utf-8")
    audit_text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "secret token query" not in cache_text
    assert "secret token query" not in audit_text
    assert "[WEB_SEARCH_QUERY_REDACTED]" in audit_text


def test_audit_logs_cache_index_operations(tmp_path) -> None:
    broker = make_broker(tmp_path)
    broker.execute(call("web.index.add_public_source", {"source": public_source()}))
    broker.execute(call("web.index.search", {"query": "cache", "limit": 5}))
    broker.execute(call("web.cache.status", {}))

    events = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in events] == [
        "web.index.add_public_source",
        "web.index.search",
        "web.cache.status",
    ]
    assert events[0]["files_written"]
    assert events[1]["files_read"]
    assert events[1]["sanitized_args"]["query"] == "[WEB_SEARCH_QUERY_REDACTED]"
    assert events[2]["files_read"]
