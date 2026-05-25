from __future__ import annotations

from agent.web_acquisition.errors import WebAcquisitionError
from agent.web_acquisition.extraction import extract_metadata, extract_readable_text
from agent.web_acquisition.feeds import FeedParseResult, parse_feed_xml
from agent.web_acquisition.fetch import WebResponse, build_fetch_payload, default_fetcher
from agent.web_acquisition.models import (
    AcquisitionRequest,
    AcquisitionResult,
    ProviderDecision,
    SourceCandidate,
    SourceTrust,
    SourceType,
)
from agent.web_acquisition.robots import RobotsPolicy, RobotsRule, parse_robots_txt
from agent.web_acquisition.router import WebAcquisitionRouter
from agent.web_acquisition.sitemaps import SitemapParseResult, parse_sitemap_xml
from agent.web_acquisition.url_normalization import DomainRules, normalize_url

__all__ = [
    "AcquisitionRequest",
    "AcquisitionResult",
    "ProviderDecision",
    "SourceCandidate",
    "SourceTrust",
    "SourceType",
    "WebAcquisitionError",
    "WebAcquisitionRouter",
    "RobotsPolicy",
    "RobotsRule",
    "parse_robots_txt",
    "SitemapParseResult",
    "parse_sitemap_xml",
    "FeedParseResult",
    "parse_feed_xml",
    "DomainRules",
    "WebResponse",
    "build_fetch_payload",
    "default_fetcher",
    "extract_metadata",
    "extract_readable_text",
    "normalize_url",
]
