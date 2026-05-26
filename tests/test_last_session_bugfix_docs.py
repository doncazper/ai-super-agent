from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_last_session_bugfix_docs_exist_and_record_evidence() -> None:
    review_path = REPO_ROOT / "docs" / "bugfix" / "LAST_SESSION_REVIEW.md"
    plan_path = REPO_ROOT / "docs" / "bugfix" / "LAST_SESSION_FIX_PLAN.md"

    review = review_path.read_text(encoding="utf-8")
    plan = plan_path.read_text(encoding="utf-8")

    assert "sess_20260525T110516Z_c5539999" in review
    assert "BUG-0001" in review
    assert "BUG-0002" in review
    assert "HERMES-09" in review
    assert "| P0 | None found." in review
    assert "No approval gate has been hit" in plan
    assert "Restore/resume `HERMES-09`" in plan
