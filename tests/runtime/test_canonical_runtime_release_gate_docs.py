from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_doc(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_canonical_runtime_release_gate_docs_exist_and_cover_required_checks() -> None:
    release_gate = read_doc("docs/runtime/CANONICAL_RUNTIME_RELEASE_GATE.md")
    maturity = read_doc("docs/runtime/CANONICAL_RUNTIME_MATURITY_REVIEW.md")
    external_gate = read_doc("docs/reviews/EXTERNAL_REVIEW_HARDENING_RELEASE_GATE.md")

    combined = "\n".join([release_gate, maturity, external_gate]).lower()
    required_terms = [
        "canonical state model",
        "durable execution record",
        "gateway / kernel boundary",
        "cli remains first frontend",
        "toolbroker",
        "policyengine",
        "approvalmanager",
        "auditlogger",
        "recovery previews do not auto-resume",
        "critical resume requires fresh approval",
        "artifact hash",
        "surface regression lanes",
        "backup policy weakening",
        "audit receipt",
        "native skill diagnostics",
        "source/provider explainability",
        "overclaimed maturity",
    ]
    for term in required_terms:
        assert term in combined


def test_canonical_runtime_release_gate_does_not_overclaim_runtime_behavior() -> None:
    release_gate = read_doc("docs/runtime/CANONICAL_RUNTIME_RELEASE_GATE.md")
    maturity = read_doc("docs/runtime/CANONICAL_RUNTIME_MATURITY_REVIEW.md")
    external_gate = read_doc("docs/reviews/EXTERNAL_REVIEW_HARDENING_RELEASE_GATE.md")

    combined = "\n".join([release_gate, maturity, external_gate]).lower()
    forbidden_claims = [
        "server starts by default",
        "is live-validated",
        "personal-data tools are enabled",
        "sends/writes are enabled",
        "is a runtime replacement",
        "audit receipt verifier/exporter are implemented",
    ]
    for claim in forbidden_claims:
        assert claim not in combined

    assert "planned-only" in combined
    assert "not live-validated" in combined or "not live validated" in combined
