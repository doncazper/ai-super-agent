from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_generated_artifact_hygiene_doc_exists() -> None:
    text = read("docs/release/GENERATED_ARTIFACT_HYGIENE.md")

    assert "workspace/eval/*" in text
    assert "workspace/messaging/drafts/*.json" in text
    assert "workspace/leads/apple_business/*.json" in text
    assert "Do not delete generated artifacts automatically" in text
    assert "broader P2 release blocker remains open" in text


def test_generated_workspace_artifacts_are_ignored_narrowly() -> None:
    text = read(".gitignore")
    required_patterns = [
        "workspace/eval/*",
        "workspace/leads/apple_business/*.json",
        "workspace/leads/status/*.json",
        "workspace/messaging/drafts/*.json",
        "workspace/messaging/inbound/*.json",
        "workspace/messaging/ios_compose/payloads/*.json",
        "workspace/messaging/ios_compose/results/*.json",
        "workspace/reddit_threads/*",
    ]

    for pattern in required_patterns:
        assert pattern in text


def test_source_fixtures_are_not_blanket_ignored() -> None:
    text = read(".gitignore")

    assert "workspace/*" not in text
    assert "workspace/dogfood/*" not in text
    assert "workspace/skills/*" not in text
    assert "workspace/dogfood/" in read("docs/release/GENERATED_ARTIFACT_HYGIENE.md")
    assert "workspace/skills/" in read("docs/release/GENERATED_ARTIFACT_HYGIENE.md")
