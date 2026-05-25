from __future__ import annotations


def romanize_term(term: str, language: str) -> tuple[str | None, str]:
    if language in {"zh", "ja", "ko"}:
        return None, "Romanization requires a dedicated provider; original term preserved."
    return None, "Romanization not applicable."
