from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser


class ReadableHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_stack: list[str] = []
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        if lower in {"script", "style", "noscript", "template", "svg", "canvas"}:
            self._skip_stack.append(lower)
        if lower == "title":
            self._in_title = True
        if lower in {"p", "br", "div", "section", "article", "li", "h1", "h2", "h3", "h4"}:
            self._text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if self._skip_stack and self._skip_stack[-1] == lower:
            self._skip_stack.pop()
        if lower == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_stack:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return normalize_text(" ".join(self._title_parts))

    @property
    def text(self) -> str:
        return normalize_text(" ".join(self._text_parts))


def normalize_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_readable_text(content: str, content_type: str = "text/html") -> dict[str, str]:
    if "html" not in content_type.lower():
        text = normalize_text(content)
        return {"title": "", "text": text}
    parser = ReadableHTMLExtractor()
    parser.feed(content)
    return {"title": parser.title, "text": parser.text}
