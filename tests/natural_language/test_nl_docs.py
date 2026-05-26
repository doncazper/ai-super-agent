from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_natural_language_architecture_docs_exist_and_name_safety_boundaries() -> None:
    docs = [
        ROOT / "docs/natural_language/NL_COMMAND_UNDERSTANDING_TRACK.md",
        ROOT / "docs/natural_language/NL_INTENT_TAXONOMY.md",
        ROOT / "docs/natural_language/NL_COMMAND_SAFETY_POLICY.md",
        ROOT / "docs/decisions/natural_language_command_understanding.md",
    ]
    for path in docs:
        text = path.read_text(encoding="utf-8")
        assert "ToolBroker" in text
        assert "PolicyEngine" in text
        assert "Approval" in text
        assert "Audit" in text


def test_natural_language_taxonomy_and_outcomes_are_documented() -> None:
    taxonomy = (ROOT / "docs/natural_language/NL_INTENT_TAXONOMY.md").read_text(encoding="utf-8")
    policy = (ROOT / "docs/natural_language/NL_COMMAND_SAFETY_POLICY.md").read_text(encoding="utf-8")
    for intent in (
        "chat.no_tools",
        "weather.current",
        "web.research",
        "personal_data.request",
        "send_or_write.request",
        "ambiguous",
    ):
        assert intent in taxonomy
    for outcome in (
        "answer_directly",
        "show_command_suggestion",
        "dry_run_only",
        "ask_clarifying_question",
        "require_approval",
        "deny",
    ):
        assert outcome in policy

