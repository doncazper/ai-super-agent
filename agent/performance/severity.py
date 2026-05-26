from __future__ import annotations


SEVERITY_ORDER = ("P0", "P1", "P2", "P3", "P4")
DEFAULT_SEVERITY = "P3"


def normalize_severity(value: str | None) -> str:
    candidate = (value or DEFAULT_SEVERITY).upper()
    if candidate not in SEVERITY_ORDER:
        return DEFAULT_SEVERITY
    return candidate


def severity_rank(value: str | None) -> int:
    return SEVERITY_ORDER.index(normalize_severity(value))
