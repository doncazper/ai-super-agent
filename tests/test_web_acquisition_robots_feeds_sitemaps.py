from __future__ import annotations

import json

import httpx
import pytest

from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.policy import Capability, PolicyEngine, RiskLevel
from agent.tools.errors import ToolError
from agent.tools.registry import default_registry
from agent.tools.web.acquisition import make_web_acquisition_tools
from agent.tools.web.fetch import DomainRules, WebResponse
from agent.web_acquisition.feeds import DEFAULT_MAX_FEED_ITEMS, parse_feed_xml
from agent.web_acquisition.errors import WebAcquisitionError
from agent.web_acquisition.robots import RobotsPolicy, parse_robots_txt
from agent.web_acquisition.sitemaps import DEFAULT_MAX_SITEMAP_URLS, parse_sitemap_xml


def response(url: str, text: str, *, content_type: str = "text/plain", status_code: int = 200) -> WebResponse:
    return WebResponse(url=url, status_code=status_code, headers={"content-type": content_type}, text=text)


def call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"call_{tool_name}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def make_broker(tmp_path, fetcher, domain_rules: DomainRules | None = None) -> ToolBroker:
    capabilities = {
        "web.robots": Capability("web.robots", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "web.robots.check": Capability("web.robots.check", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "web.sitemap": Capability("web.sitemap", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "web.sitemap.fetch": Capability("web.sitemap.fetch", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "web.feed": Capability("web.feed", RiskLevel.LOW, metadata={"requires_web_access": True}),
        "web.feed.fetch": Capability("web.feed.fetch", RiskLevel.LOW, metadata={"requires_web_access": True}),
    }
    return ToolBroker(
        default_registry(project_root=tmp_path, web_fetcher=fetcher, web_domain_rules=domain_rules or DomainRules()),
        PolicyEngine(capabilities),
        AuditLogger(tmp_path / "audit.jsonl"),
        session_id="test-session",
        model="test-model",
        route="test",
    )


def test_robots_allow_disallow_parsed() -> None:
    rules, sitemaps = parse_robots_txt(
        "User-agent: *\nDisallow: /private\nAllow: /private/public\nSitemap: https://example.com/sitemap.xml\n"
    )
    policy = RobotsPolicy("https://example.com/robots.txt", sitemaps, rules)

    assert policy.allowed("/public") is True
    assert policy.allowed("/private/secret") is False
    assert policy.allowed("/private/public/page") is True
    assert sitemaps == ["https://example.com/sitemap.xml"]


def test_malformed_robots_ignored_safely(tmp_path) -> None:
    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        return response(url, "this is not a directive\nDisallow without colon\nUser-agent: *\nAllow: /\n")

    tools = make_web_acquisition_tools(project_root=tmp_path, fetcher=fetcher, domain_rules=DomainRules())
    payload = tools["web.robots"]("example.com")

    assert payload["status"] == "ok"
    assert payload["robots"]["allowed"] is True
    assert payload["trust_level"] == "UNTRUSTED_WEB"


def test_sitemap_xml_and_index_parsed() -> None:
    parsed_urls = parse_sitemap_xml(
        """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://example.com/a</loc></url>
        </urlset>"""
    )
    parsed_index = parse_sitemap_xml(
        """<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap><loc>https://example.com/child.xml</loc></sitemap>
        </sitemapindex>"""
    )

    assert parsed_urls.urls == [{"url": "https://example.com/a", "trust_level": "UNTRUSTED_WEB"}]
    assert parsed_index.child_sitemaps == ["https://example.com/child.xml"]


def test_malformed_sitemap_handled() -> None:
    with pytest.raises(WebAcquisitionError, match="sitemap XML is malformed"):
        parse_sitemap_xml("<urlset><url>")


def test_feed_rss_and_atom_parsed() -> None:
    rss = parse_feed_xml(
        """<rss><channel><item><title>One</title><link>https://example.com/one</link>
        <pubDate>Sun, 24 May 2026 12:00:00 GMT</pubDate><description>First item</description></item></channel></rss>""",
        source_url="https://example.com/feed.xml",
    )
    atom = parse_feed_xml(
        """<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Two</title>
        <link href="/two" /><updated>2026-05-24T12:00:00Z</updated><summary>Second item</summary></entry></feed>""",
        source_url="https://example.com/feed.xml",
    )

    assert rss.items[0]["published_date"] == "Sun, 24 May 2026 12:00:00 GMT"
    assert rss.items[0]["snippet"] == "First item"
    assert rss.items[0]["source"] == "https://example.com/feed.xml"
    assert atom.items[0]["url"] == "https://example.com/two"
    assert atom.items[0]["trust_level"] == "UNTRUSTED_WEB"


def test_malformed_feed_handled() -> None:
    with pytest.raises(WebAcquisitionError, match="feed XML is malformed"):
        parse_feed_xml("<rss><channel>", source_url="https://example.com/feed.xml")


def test_timeout_handled_as_unavailable(tmp_path) -> None:
    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        raise httpx.TimeoutException("slow")

    tools = make_web_acquisition_tools(project_root=tmp_path, fetcher=fetcher, domain_rules=DomainRules())
    payload = tools["web.feed"]("https://example.com/feed.xml")

    assert payload["status"] == "unavailable"
    assert payload["reason"] == "web acquisition timed out"
    assert payload["bypass_attempted"] is False


def test_binary_feed_and_sitemap_content_blocked(tmp_path) -> None:
    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        if url.endswith("/robots.txt"):
            return response(url, "User-agent: *\nSitemap: https://example.com/sitemap.xml\n")
        return response(url, "not text", content_type="application/octet-stream")

    tools = make_web_acquisition_tools(project_root=tmp_path, fetcher=fetcher, domain_rules=DomainRules())

    with pytest.raises(ToolError, match="sitemap binary downloads are disabled"):
        tools["web.sitemap"]("example.com")
    with pytest.raises(ToolError, match="feed binary downloads are disabled"):
        tools["web.feed"]("https://example.com/feed.xml")


def test_default_max_limits_enforced(tmp_path) -> None:
    sitemap_xml = "<urlset>" + "".join(f"<url><loc>https://example.com/{idx}</loc></url>" for idx in range(600)) + "</urlset>"
    feed_xml = "<rss><channel>" + "".join(f"<item><title>{idx}</title><link>/{idx}</link></item>" for idx in range(60)) + "</channel></rss>"

    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        if url.endswith("/robots.txt"):
            return response(url, "User-agent: *\nSitemap: https://example.com/sitemap.xml\n")
        if url.endswith("/feed.xml"):
            return response(url, feed_xml, content_type="application/rss+xml")
        return response(url, sitemap_xml, content_type="application/xml")

    tools = make_web_acquisition_tools(project_root=tmp_path, fetcher=fetcher, domain_rules=DomainRules())

    assert tools["web.sitemap"]("example.com")["url_count"] == DEFAULT_MAX_SITEMAP_URLS
    assert tools["web.feed"]("https://example.com/feed.xml")["item_count"] == DEFAULT_MAX_FEED_ITEMS


def test_robots_sitemap_and_feed_cache_ttl_reuses_results(tmp_path) -> None:
    calls: list[str] = []

    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        calls.append(url)
        if url.endswith("/robots.txt"):
            return response(url, "User-agent: *\nSitemap: https://example.com/sitemap.xml\n")
        if url.endswith("/feed.xml"):
            return response(url, "<rss><channel><item><title>One</title><link>/one</link></item></channel></rss>", content_type="application/rss+xml")
        return response(url, "<urlset><url><loc>https://example.com/a</loc></url></urlset>", content_type="application/xml")

    tools = make_web_acquisition_tools(project_root=tmp_path, fetcher=fetcher, domain_rules=DomainRules())

    assert tools["web.robots"]("example.com")["cache"]["status"] == "miss"
    assert tools["web.robots"]("example.com")["cache"]["status"] == "hit"
    assert tools["web.sitemap"]("example.com")["cache"]["status"] == "miss"
    assert tools["web.sitemap"]("example.com")["cache"]["status"] == "hit"
    assert tools["web.feed"]("https://example.com/feed.xml")["cache"]["status"] == "miss"
    assert tools["web.feed"]("https://example.com/feed.xml")["cache"]["status"] == "hit"
    assert calls.count("https://example.com/robots.txt") == 3
    assert calls.count("https://example.com/sitemap.xml") == 1
    assert calls.count("https://example.com/feed.xml") == 1


def test_audit_logs_domain_for_robots_sitemap_and_feed(tmp_path) -> None:
    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        if url.endswith("/robots.txt"):
            return response(url, "User-agent: *\nSitemap: https://example.com/sitemap.xml\n")
        if url.endswith("/feed.xml"):
            return response(url, "<rss><channel><item><title>One</title><link>/one</link></item></channel></rss>")
        return response(url, "<urlset><url><loc>https://example.com/a</loc></url></urlset>")

    broker = make_broker(tmp_path, fetcher)
    assert broker.execute(call("web.robots", {"domain": "example.com"})).allowed is True
    assert broker.execute(call("web.sitemap", {"domain": "example.com"})).allowed is True
    assert broker.execute(call("web.feed", {"url": "https://example.com/feed.xml"})).allowed is True

    audit_lines = [json.loads(line) for line in (tmp_path / "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["tool_name"] for event in audit_lines] == ["web.robots", "web.sitemap", "web.feed"]
    assert all("example.com" in event["network_domains"] for event in audit_lines)


def test_requested_capability_aliases_are_brokered(tmp_path) -> None:
    def fetcher(url: str, timeout_seconds: int) -> WebResponse:
        if url.endswith("/robots.txt"):
            return response(url, "User-agent: *\nSitemap: https://example.com/sitemap.xml\n")
        if url.endswith("/feed.xml"):
            return response(url, "<rss><channel><item><title>One</title><link>/one</link></item></channel></rss>")
        return response(url, "<urlset><url><loc>https://example.com/a</loc></url></urlset>")

    broker = make_broker(tmp_path, fetcher)

    assert broker.execute(call("web.robots.check", {"domain": "example.com"})).allowed is True
    assert broker.execute(call("web.sitemap.fetch", {"domain": "example.com"})).allowed is True
    assert broker.execute(call("web.feed.fetch", {"url": "https://example.com/feed.xml"})).allowed is True


def test_blocked_domain_denied(tmp_path) -> None:
    tools = make_web_acquisition_tools(
        project_root=tmp_path,
        fetcher=lambda url, timeout_seconds: response(url, ""),
        domain_rules=DomainRules(blocked_domains=frozenset({"blocked.example"})),
    )

    with pytest.raises(ToolError, match="blocked domain denied"):
        tools["web.feed"]("https://blocked.example/feed.xml")
