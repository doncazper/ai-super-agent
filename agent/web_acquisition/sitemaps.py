from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass

from agent.web_acquisition.errors import WebAcquisitionError


DEFAULT_SITEMAP_TIMEOUT_SECONDS = 10
DEFAULT_MAX_SITEMAP_URLS = 500


@dataclass(frozen=True)
class SitemapParseResult:
    urls: list[dict[str, str]]
    child_sitemaps: list[str]
    truncated: bool


def parse_sitemap_xml(text: str, *, max_urls: int = DEFAULT_MAX_SITEMAP_URLS) -> SitemapParseResult:
    if max_urls <= 0:
        raise WebAcquisitionError("max_urls must be positive")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise WebAcquisitionError("sitemap XML is malformed") from exc
    urls: list[dict[str, str]] = []
    child_sitemaps: list[str] = []
    for element in root.iter():
        if _local_name(element.tag) != "loc" or not element.text:
            continue
        loc = element.text.strip()
        parent = _local_name(_parent_tag(root, element) or "")
        if parent == "sitemap":
            child_sitemaps.append(loc)
        else:
            urls.append({"url": loc, "trust_level": "UNTRUSTED_WEB"})
        if len(urls) >= max_urls:
            break
    return SitemapParseResult(urls=urls[:max_urls], child_sitemaps=child_sitemaps, truncated=len(urls) >= max_urls)


def _parent_tag(root: ET.Element, target: ET.Element) -> str | None:
    for parent in root.iter():
        if target in list(parent):
            return parent.tag
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
