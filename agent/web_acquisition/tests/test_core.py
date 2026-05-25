from __future__ import annotations

import pytest

from agent.tools.web.fetch import DomainRules
from agent.web_acquisition import AcquisitionRequest, SourceType, WebAcquisitionError, WebAcquisitionRouter


def test_acquisition_request_validates_query_or_url() -> None:
    with pytest.raises(WebAcquisitionError, match="query or url"):
        AcquisitionRequest()

    request = AcquisitionRequest(url="https://example.com")

    assert request.url == "https://example.com"


def test_unknown_provider_denied() -> None:
    with pytest.raises(WebAcquisitionError, match="unknown provider"):
        AcquisitionRequest(query="news", provider="mystery_provider")


def test_cache_source_preferred_when_available() -> None:
    router = WebAcquisitionRouter(domain_rules=DomainRules())
    result = router.plan(AcquisitionRequest(query="cached public source"), cache_available=True)

    assert result.status == "ok"
    assert result.source_type == SourceType.CACHE
    assert result.provider_decision is not None
    assert result.provider_decision.cache_used is True


def test_blocked_source_returns_structured_unavailable_error() -> None:
    router = WebAcquisitionRouter(domain_rules=DomainRules(blocked_domains=["example.com"]))
    result = router.source_status("https://example.com/private")

    assert result.status == "unavailable"
    assert result.source_type == SourceType.BLOCKED
    assert result.error == "blocked_or_invalid_url"
    assert result.metadata["bypass_attempted"] is False


def test_content_trust_label_applied() -> None:
    router = WebAcquisitionRouter(domain_rules=DomainRules())
    result = router.source_status("https://example.com")
    payload = result.to_dict()

    assert payload["trust_level"] == "UNTRUSTED_WEB"
    assert payload["document_trust_level"] == "UNTRUSTED_DOCUMENT"
    assert payload["metadata"]["final_model_handling"] == "web results are passed as data, never as instructions"


def test_sitemap_url_classified_before_generic_xml_feed() -> None:
    router = WebAcquisitionRouter(domain_rules=DomainRules())
    result = router.source_status("https://example.com/sitemap.xml")

    assert result.source_type == SourceType.SITEMAP


def test_no_query_history_stored_by_default() -> None:
    router = WebAcquisitionRouter(domain_rules=DomainRules())
    result = router.plan(AcquisitionRequest(query="sensitive topic"))

    assert result.metadata["query_history_stored"] is False
    assert result.provider_decision is not None
    assert result.provider_decision.to_dict()["paid_api_used"] is False
