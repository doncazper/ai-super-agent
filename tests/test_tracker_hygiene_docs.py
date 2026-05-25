from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_tracker_hygiene_docs_exist() -> None:
    required = [
        "docs/TRACKER_DASHBOARD.md",
        "docs/TRACKER_INDEX.md",
        "docs/TRACKER_MAINTENANCE.md",
        "docs/TRACKER_ARCHIVE_POLICY.md",
        "docs/TRACKER_CONSISTENCY_REPORT.md",
    ]

    for path in required:
        assert (ROOT / path).exists(), path


def test_tracker_navigation_links_are_present() -> None:
    assert "docs/TRACKER_DASHBOARD.md" in read("docs/PROJECT_STATE.md")
    assert "docs/TRACKER_DASHBOARD.md" in read("docs/FEATURE_MATURITY.md")
    assert "docs/TRACKER_INDEX.md" in read("docs/COMMAND_REGISTRY.md")
    assert "docs/TRACKER_INDEX.md" in read("README.md")


def test_agents_tracker_rules_are_anchored() -> None:
    text = read("AGENTS.md")

    assert "small anchored edits" in text
    assert "TRACKER_DASHBOARD" in text
    assert "TRACKER_CONSISTENCY_REPORT" in text
    assert "If trackers disagree" in text

