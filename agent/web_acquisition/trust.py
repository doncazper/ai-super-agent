from __future__ import annotations

UNTRUSTED_WEB = "UNTRUSTED_WEB"
UNTRUSTED_DOCUMENT = "UNTRUSTED_DOCUMENT"


def trust_labels() -> dict[str, str]:
    return {
        "trust_level": UNTRUSTED_WEB,
        "document_trust_level": UNTRUSTED_DOCUMENT,
    }

