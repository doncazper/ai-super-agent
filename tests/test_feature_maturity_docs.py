from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def table_rows(markdown: str, required_header: str) -> list[dict[str, str]]:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("|") or required_header not in line:
            continue
        headers = [cell.strip() for cell in line.strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for row in lines[index + 2 :]:
            if not row.startswith("|"):
                break
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))
        return rows
    raise AssertionError(f"table with header {required_header!r} not found")


def test_feature_maturity_docs_exist() -> None:
    for path in (
        "docs/FEATURE_MATURITY.md",
        "docs/FEATURE_REGISTRY.md",
        "docs/PROJECT_STATE.md",
        "docs/FEATURE_ROADMAP.md",
        "docs/templates/feature_maturity_template.md",
        "CHANGELOG.md",
    ):
        assert (ROOT / path).exists(), path


def test_feature_registry_has_maturity_columns() -> None:
    registry = read("docs/FEATURE_REGISTRY.md")
    header = next(line for line in registry.splitlines() if line.startswith("| Feature |"))
    for column in (
        "Maturity Level",
        "Readiness Score",
        "Prompt / Iteration Count",
        "Test Depth",
        "Security Hardening Status",
        "Live Validation Status",
        "UX/Docs Status",
        "Last Hardening Pass",
        "Next Work Needed",
    ):
        assert column in header


def test_project_state_references_maturity() -> None:
    project_state = read("docs/PROJECT_STATE.md")

    assert "Maturity Summary" in project_state
    assert "Most mature features" in project_state
    assert "Least mature features" in project_state
    assert "Features needing hardening" in project_state
    assert "Features needing live validation" in project_state
    assert "Current Recommended Work Up Next" in project_state


def test_agents_requires_maturity_updates() -> None:
    agents = read("AGENTS.md")

    assert "Before starting feature work, read `docs/FEATURE_MATURITY.md`." in agents
    assert "update `docs/FEATURE_MATURITY.md`" in agents
    assert "Prompt count is useful context but not proof of maturity." in agents
    assert "A feature can be complete but still immature." in agents


def test_every_registry_feature_has_valid_maturity_level() -> None:
    rows = table_rows(read("docs/FEATURE_REGISTRY.md"), "Maturity Level")

    assert rows
    for row in rows:
        feature = row["Feature"]
        maturity = row["Maturity Level"]
        assert re.fullmatch(
            r"[0-8] (Idea|Specified|Scaffolded|Implemented|Tested|Hardened|Live-Validated|User-Ready|Mature Pattern)",
            maturity,
        ), f"{feature}: {maturity}"
        assert row["Readiness Score"].isdigit(), feature
        assert row["Next Work Needed"], feature


def test_feature_maturity_assessment_covers_registry_features() -> None:
    registry_features = {row["Feature"] for row in table_rows(read("docs/FEATURE_REGISTRY.md"), "Maturity Level")}
    maturity_features = {row["Feature"] for row in table_rows(read("docs/FEATURE_MATURITY.md"), "Maturity Level")}

    assert registry_features <= maturity_features
