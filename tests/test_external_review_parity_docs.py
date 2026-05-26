from __future__ import annotations

from pathlib import Path

from agent.ui.command_registry import get_command


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_external_review_docs_exist_and_cover_required_parity_areas() -> None:
    paths = [
        "docs/reviews/EXTERNAL_ARCHITECTURE_REVIEW_FINDINGS.md",
        "docs/reviews/EXTERNAL_REVIEW_HARDENING_PLAN.md",
        "docs/reviews/EXTERNAL_REVIEW_PARITY_CHECKLIST.md",
    ]
    for path in paths:
        assert (ROOT / path).exists(), path

    combined = "\n".join(read(path) for path in paths)
    for phrase in [
        "Audit hash-chain",
        "Audit receipt",
        "Native skill",
        "Source/provider explainability",
        "HIGH/CRITICAL approval semantics",
        "Backup restore policy",
        "Self-improvement safety lints",
        "Overclaim cleanup",
        "No runtime architecture rewrite",
        "No personal-data access",
    ]:
        assert phrase in combined


def test_external_review_tracks_audit_receipt_commands_as_planned_only() -> None:
    verify = get_command("CMD-AUDIT-001")
    receipt = get_command("CMD-AUDIT-002")
    assert verify is not None
    assert receipt is not None

    for record in (verify, receipt):
        assert record.status == "planned"
        assert "not implemented" in record.manual_qa_status
        assert "no memory write" in record.memory_behavior
        assert "planned" in record.side_effects

    registry = read("docs/COMMAND_REGISTRY.md")
    assert "`python smart_agent.py audit verify-chain`" in registry
    assert "`python smart_agent.py audit export-receipt <audit_id>`" in registry


def test_external_review_does_not_overclaim_audit_receipt_runtime() -> None:
    findings = read("docs/reviews/EXTERNAL_ARCHITECTURE_REVIEW_FINDINGS.md")
    plan = read("docs/reviews/EXTERNAL_REVIEW_HARDENING_PLAN.md")
    assert "Partially covered" in findings
    assert "These commands are not implemented yet" in plan
    assert "They are tracked as `planned`" in plan
