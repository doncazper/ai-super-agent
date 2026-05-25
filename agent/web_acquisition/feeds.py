from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from urllib.parse import urljoin

from agent.web_acquisition.errors import WebAcquisitionError


DEFAULT_FEED_TIMEOUT_SECONDS = 10
DEFAULT_MAX_FEED_ITEMS = 50


@dataclass(frozen=True)
class FeedParseResult:
    items: list[dict[str, str]]
    truncated: bool


def parse_feed_xml(text: str, *, source_url: str, max_items: int = DEFAULT_MAX_FEED_ITEMS) -> FeedParseResult:
    if max_items <= 0:
        raise WebAcquisitionError("max_items must be positive")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise WebAcquisitionError("feed XML is malformed") from exc
    items: list[dict[str, str]] = []
    seen = 0
    for entry in root.iter():
        if _local_name(entry.tag) not in {"item", "entry"}:
            continue
        seen += 1
        item = _feed_entry(entry, source_url=source_url)
        if item["title"] or item["url"]:
            items.append(item)
        if len(items) >= max_items:
            break
    return FeedParseResult(items=items, truncated=seen > len(items) or len(items) >= max_items)


def _feed_entry(entry: ET.Element, *, source_url: str) -> dict[str, str]:
    title = ""
    link = ""
    published_date = ""
    summary = ""
    for child in list(entry):
        name = _local_name(child.tag)
        text = (child.text or "").strip()
        if name == "title" and text:
            title = text
        elif name == "link":
            link = child.attrib.get("href", "").strip() or text
        elif name in {"updated", "published", "pubDate"} and text:
            published_date = text
        elif name in {"summary", "description", "content"} and text:
            summary = re.sub(r"<[^>]+>", "", text).strip()
    snippet = summary[:500]
    return {
        "title": title,
        "url": urljoin(source_url, link) if link else "",
        "published_date": published_date,
        "updated": published_date,
        "summary": snippet,
        "snippet": snippet,
        "source": source_url,
        "trust_level": "UNTRUSTED_WEB",
    }


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]
