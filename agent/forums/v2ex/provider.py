from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.forums.v2ex.cache import V2EXCache, v2ex_cache_key
from agent.forums.v2ex.client import V2EXApiClient, V2EXConfig, load_v2ex_config, v2ex_setup_hint
from agent.forums.v2ex.errors import V2EXConnectorError, normalize_error
from agent.forums.v2ex.models import PROVIDER, TRUST_LEVEL, V2EXReply, utc_now_iso
from agent.forums.v2ex.normalizer import normalize_node, normalize_reply, normalize_topic, payload_items, topic_to_forum_thread
from agent.language.detection import detect_language
from agent.language.translation import TranslationProvider, translate_text

READ_CAPABILITIES = (
    "v2ex.nodes.get",
    "v2ex.node_topics",
    "v2ex.topic.get",
    "v2ex.topic_replies",
    "v2ex.latest",
    "v2ex.hot",
)
WRITE_CAPABILITIES: tuple[str, ...] = ()


class V2EXReadOnlyProvider:
    def __init__(
        self,
        *,
        client: V2EXApiClient | None = None,
        config: V2EXConfig | None = None,
        cache: V2EXCache | None = None,
    ) -> None:
        self.config = config or (client.config if client is not None else load_v2ex_config())
        self.client = client or V2EXApiClient(config=self.config)
        self.cache = cache or V2EXCache(ttl_seconds=self.config.cache_ttl_seconds, enabled=self.config.cache_enabled)

    def status(self, *, detail: str = "status") -> dict[str, Any]:
        payload = {
            **self.config.public_status(),
            "setup_hint": v2ex_setup_hint(self.config),
            "read_capabilities": list(READ_CAPABILITIES),
            "write_capabilities": list(WRITE_CAPABILITIES),
            "network_call_performed": False,
            "personal_data_accessed": False,
            "logged_in_read_performed": False,
            "token_printed": False,
            "token_redacted": True,
            "official_api_only": True,
            "web_scraping_fallback_used": False,
            "cache_status": self.cache.status(),
            "_audit": _audit("v2ex.status", "V2EX status inspected without provider network calls."),
        }
        if detail == "doctor":
            payload["warnings"] = _doctor_warnings(self.config)
            payload["next_setup_steps"] = [
                "Set V2EX_ENABLED=true to enable read-only documented API access.",
                "Set V2EX_TOKEN only for API 2.0 endpoints that require bearer-token auth.",
                "Do not enable member/profile/notification/write endpoints in this track.",
            ]
        return payload

    def nodes(self, *, limit: int = 500) -> dict[str, Any]:
        return self._cached_call("nodes", (limit,), lambda: self.client.nodes(), self._nodes_payload, limit=limit)

    def node_topics(
        self,
        node_name: str,
        *,
        limit: int = 10,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        return self._cached_call(
            "node_topics",
            (node_name, limit, detect, translate_to),
            lambda: self.client.node_topics(node_name),
            self._topics_payload,
            limit=limit,
            detect=detect,
            translate_to=translate_to,
            translation_provider=translation_provider,
        )

    def topic(
        self,
        topic_id: int | str,
        *,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        return self._cached_call(
            "topic",
            (topic_id, detect, translate_to),
            lambda: self.client.topic(topic_id),
            self._topic_payload,
            detect=detect,
            translate_to=translate_to,
            translation_provider=translation_provider,
        )

    def replies(
        self,
        topic_id: int | str,
        *,
        limit: int = 100,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        return self._cached_call(
            "replies",
            (topic_id, limit, detect, translate_to),
            lambda: self.client.replies(topic_id),
            self._replies_payload,
            topic_id=str(topic_id),
            limit=limit,
            detect=detect,
            translate_to=translate_to,
            translation_provider=translation_provider,
        )

    def latest(self, *, limit: int = 10) -> dict[str, Any]:
        return self._cached_call("latest", (limit,), lambda: self.client.latest(), self._topics_payload, limit=limit)

    def hot(self, *, limit: int = 10) -> dict[str, Any]:
        return self._cached_call("hot", (limit,), lambda: self.client.hot(), self._topics_payload, limit=limit)

    def _cached_call(self, operation: str, key_parts: tuple[object, ...], fetcher: Any, formatter: Any, **kwargs: Any) -> dict[str, Any]:
        key = v2ex_cache_key(operation, *key_parts)
        cached = self.cache.get(key)
        if cached is not None:
            payload = dict(cached)
            payload["cache_used"] = True
            payload["_audit"] = _audit(f"v2ex.{operation}", f"V2EX {operation} returned from TTL cache.")
            return payload
        try:
            response = fetcher()
            payload = formatter(response, **kwargs)
            payload.update(
                {
                    "status": "ok",
                    "provider": PROVIDER,
                    "trust_level": TRUST_LEVEL,
                    "retrieved_at": utc_now_iso(),
                    "cache_used": False,
                    "rate_limit_status": response.rate_limit.to_dict(),
                    "endpoint_family": response.endpoint_family,
                    "query_history_stored": False,
                    "memory_written": False,
                    "web_scraping_fallback_used": False,
                    "write_capabilities_enabled": False,
                    "_audit": _audit(f"v2ex.{operation}", f"V2EX {operation} fetched through documented API.", response.network_domains),
                }
            )
            self.cache.set(key, {k: v for k, v in payload.items() if k != "_audit"}, source=operation)
            return payload
        except V2EXConnectorError as exc:
            return {
                "status": "setup_required" if exc.code == "v2ex_setup_required" else "error",
                "provider": PROVIDER,
                "error": normalize_error(exc),
                "setup_hint": v2ex_setup_hint(self.config),
                "trust_level": TRUST_LEVEL,
                "memory_written": False,
                "web_scraping_fallback_used": False,
                "_audit": _audit(f"v2ex.{operation}", f"V2EX {operation} failed: {exc.code}."),
            }

    def _nodes_payload(self, response: Any, *, limit: int = 500) -> dict[str, Any]:
        nodes = [normalize_node(item).to_dict() for item in payload_items(response.payload, "nodes", "result")[: max(1, min(limit, 1000))]]
        return {"nodes": nodes, "node_count": len(nodes)}

    def _topics_payload(
        self,
        response: Any,
        *,
        limit: int = 10,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        topics = [normalize_topic(item).to_dict() for item in payload_items(response.payload, "topics", "result")[: max(1, min(limit, 100))]]
        threads = []
        for topic_payload in topics:
            thread = topic_to_forum_thread(normalize_topic(topic_payload)).to_dict()
            self._maybe_language(thread["post"], detect=detect, translate_to=translate_to, translation_provider=translation_provider)
            threads.append(thread)
        return {"threads": threads, "results": threads, "result_count": len(threads), "language_workflow": _language_workflow(detect, translate_to)}

    def _topic_payload(
        self,
        response: Any,
        *,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        items = payload_items(response.payload, "result", "topics")
        topic = normalize_topic(items[0]) if items else normalize_topic({})
        thread = topic_to_forum_thread(topic).to_dict()
        self._maybe_language(thread["post"], detect=detect, translate_to=translate_to, translation_provider=translation_provider)
        return {"thread": thread, "source_references": thread["source_references"], "language_workflow": _language_workflow(detect, translate_to)}

    def _replies_payload(
        self,
        response: Any,
        *,
        topic_id: str,
        limit: int = 100,
        detect: bool = False,
        translate_to: str = "",
        translation_provider: TranslationProvider | None = None,
    ) -> dict[str, Any]:
        replies: list[V2EXReply] = [
            normalize_reply(item, topic_id=topic_id)
            for item in payload_items(response.payload, "replies", "result")[: max(1, min(limit, 500))]
        ]
        comments = []
        for reply in replies:
            comment = {
                "source_id": reply.source_id,
                "provider": PROVIDER,
                "provider_comment_id": reply.reply_id,
                "thread_id": reply.topic_id,
                "url": reply.url,
                "body_text": reply.body_text,
                "created_at": reply.created_at,
                "retrieved_at": reply.retrieved_at,
                "trust_level": reply.trust_level,
                "language": reply.language,
                "metadata": {},
            }
            self._maybe_language(comment, detect=detect, translate_to=translate_to, translation_provider=translation_provider)
            comments.append(comment)
        return {"comments": comments, "comment_count": len(comments), "language_workflow": _language_workflow(detect, translate_to)}

    def _maybe_language(
        self,
        item: dict[str, Any],
        *,
        detect: bool,
        translate_to: str,
        translation_provider: TranslationProvider | None,
    ) -> None:
        text = " ".join(part for part in (item.get("title", ""), item.get("body_text", "")) if part)
        if not (detect or translate_to) or not text:
            return
        detection = detect_language(text, source_id=str(item["source_id"]), trust_level=TRUST_LEVEL)
        item["language"] = detection.language
        item["language_detection"] = detection.to_dict()
        if translate_to:
            item["translation"] = translate_text(
                text,
                from_language=detection.language,
                to_language=translate_to,
                source_id=str(item["source_id"]),
                trust_level=TRUST_LEVEL,
                provider=translation_provider,
            )


def default_v2ex_provider(project_root: str | Path = ".") -> V2EXReadOnlyProvider:
    config = load_v2ex_config()
    cache = V2EXCache(Path(project_root) / "data" / "v2ex" / "cache.json", ttl_seconds=config.cache_ttl_seconds, enabled=config.cache_enabled)
    return V2EXReadOnlyProvider(config=config, cache=cache)


def _doctor_warnings(config: V2EXConfig) -> list[str]:
    warnings: list[str] = []
    if not config.enabled:
        warnings.append("V2EX_ENABLED=false; read-only API calls are disabled.")
    if not config.token_configured:
        warnings.append("V2EX_TOKEN is not configured; token-required API 2.0 endpoints may be unavailable.")
    warnings.append("V2EX member/profile/notification/write endpoints are disabled in this track.")
    return warnings


def _language_workflow(detect: bool, translate_to: str) -> dict[str, Any]:
    return {
        "requested": bool(detect or translate_to),
        "language_detection_requested": bool(detect or translate_to),
        "translation_requested": bool(translate_to),
        "translation_label": "MODEL_GENERATED_TRANSLATION" if translate_to else "",
        "memory_written": False,
    }


def _audit(action: str, summary: str, domains: list[str] | None = None) -> dict[str, Any]:
    return {"network_domains": list(domains or []), "result_summary": summary, "commands_run": [action]}
