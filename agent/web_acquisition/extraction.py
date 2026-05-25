from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin

from agent.web_acquisition.sanitization import sanitize_html


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


class MetadataParser(HTMLParser):
    def __init__(self, base_url: str | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.canonical_url: str | None = None
        self.author: str | None = None
        self.published_at: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag == "title":
            self.in_title = True
        if tag == "link" and attr_map.get("rel", "").lower() == "canonical" and attr_map.get("href"):
            self.canonical_url = urljoin(self.base_url or "", attr_map["href"])
        if tag == "meta":
            key = (attr_map.get("name") or attr_map.get("property") or "").lower()
            content = attr_map.get("content", "").strip()
            if not content:
                return
            if key in {"author", "article:author", "parsely-author"} and self.author is None:
                self.author = content
            if key in {"article:published_time", "date", "dc.date", "publishdate", "pubdate"} and self.published_at is None:
                self.published_at = content

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    def metadata(self) -> dict[str, str | None]:
        title = _clean_text(" ".join(self.title_parts))
        return {
            "title": title or None,
            "canonical_url": self.canonical_url,
            "author": self.author,
            "published_at": self.published_at,
        }


def extract_readable_text(content: str, content_type: str = "text/html") -> dict[str, object]:
    if not _is_html(content_type):
        text = _clean_text(content)
        return {"title": "", "text": text, "html_sanitized": "", "extraction_warnings": []}

    sanitized = sanitize_html(content)
    html_sanitized = str(sanitized["html"])
    title_match = TITLE_RE.search(html_sanitized)
    title = _clean_text(title_match.group(1)) if title_match else ""
    text = _clean_text(TAG_RE.sub(" ", html_sanitized))
    return {
        "title": title,
        "text": text,
        "html_sanitized": html_sanitized,
        "extraction_warnings": list(sanitized["warnings"]),
    }


def extract_metadata(content: str, *, base_url: str | None = None, content_type: str = "text/html") -> dict[str, str | None]:
    if not _is_html(content_type):
        return {"title": None, "canonical_url": base_url, "author": None, "published_at": None}
    parser = MetadataParser(base_url=base_url)
    parser.feed(content)
    parser.close()
    metadata = parser.metadata()
    if metadata["canonical_url"] is None:
        metadata["canonical_url"] = base_url
    return metadata


def _is_html(content_type: str) -> bool:
    normalized = content_type.split(";")[0].strip().lower()
    return normalized in {"text/html", "application/xhtml+xml"} or normalized.endswith("+html")


def _clean_text(value: str) -> str:
    return SPACE_RE.sub(" ", value).strip()
