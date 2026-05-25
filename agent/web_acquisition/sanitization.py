from __future__ import annotations

from html import escape
from html.parser import HTMLParser
from typing import Iterable


DROP_CONTENT_TAGS = {"script", "style", "noscript", "template", "svg", "canvas"}
DROP_TAGS = {"iframe", "object", "embed"}
VOID_TAGS = {"br", "hr", "img", "meta", "link", "input"}
SAFE_ATTRS = {
    "a": {"href", "title", "rel"},
    "abbr": {"title"},
    "blockquote": {"cite"},
    "img": {"alt", "title"},
    "*": {"lang", "dir"},
}
URL_ATTRS = {"href", "src", "cite"}


class HTMLSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.warnings: list[str] = []
        self._drop_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            self._drop_depth += 1
            if f"stripped {tag} content" not in self.warnings:
                self.warnings.append(f"stripped {tag} content")
            return
        if self._drop_depth:
            return
        if tag in DROP_TAGS:
            if f"stripped {tag} tag" not in self.warnings:
                self.warnings.append(f"stripped {tag} tag")
            return
        cleaned_attrs = _clean_attrs(tag, attrs, self.warnings)
        attr_text = "".join(f' {name}="{escape(value, quote=True)}"' for name, value in cleaned_attrs)
        self.parts.append(f"<{tag}{attr_text}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in DROP_CONTENT_TAGS:
            if self._drop_depth:
                self._drop_depth -= 1
            return
        if self._drop_depth or tag in DROP_TAGS or tag in VOID_TAGS:
            return
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._drop_depth:
            self.parts.append(escape(data))

    def handle_entityref(self, name: str) -> None:
        if not self._drop_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self._drop_depth:
            self.parts.append(f"&#{name};")


def sanitize_html(html: str) -> dict[str, object]:
    parser = HTMLSanitizer()
    parser.feed(html)
    parser.close()
    return {"html": "".join(parser.parts), "warnings": parser.warnings}


def _clean_attrs(tag: str, attrs: Iterable[tuple[str, str | None]], warnings: list[str]) -> list[tuple[str, str]]:
    allowed = SAFE_ATTRS.get(tag, set()) | SAFE_ATTRS["*"]
    cleaned: list[tuple[str, str]] = []
    for raw_name, raw_value in attrs:
        name = raw_name.lower()
        value = raw_value or ""
        if name.startswith("on"):
            if "stripped event handler attributes" not in warnings:
                warnings.append("stripped event handler attributes")
            continue
        if name not in allowed:
            continue
        if name in URL_ATTRS and value.strip().lower().startswith(("javascript:", "data:", "vbscript:")):
            if "stripped unsafe URL attributes" not in warnings:
                warnings.append("stripped unsafe URL attributes")
            continue
        cleaned.append((name, value))
    return cleaned
