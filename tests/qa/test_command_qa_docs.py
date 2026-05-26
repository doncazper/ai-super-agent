from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_command_qa_architecture_docs_exist_and_define_tiers() -> None:
    required = [
        "docs/qa/COMMAND_QA_SANDBOX_STRATEGY.md",
        "docs/qa/COMMAND_QA_SAFETY_POLICY.md",
        "docs/qa/COMMAND_QA_TIERS.md",
        "docs/qa/COMMAND_QA_RESULT_SCHEMA.md",
        "docs/qa/SELF_HEALING_LOOP_POLICY.md",
        "docs/decisions/command_qa_sandbox_self_heal.md",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative

    tiers = (ROOT / "docs/qa/COMMAND_QA_TIERS.md").read_text(encoding="utf-8")
    for marker in ("Tier 0", "Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5", "Tier 6", "Tier 7"):
        assert marker in tiers


def test_command_qa_policy_keeps_high_risk_manual() -> None:
    policy = (ROOT / "docs/qa/COMMAND_QA_SAFETY_POLICY.md").read_text(encoding="utf-8")
    decision = (ROOT / "docs/decisions/command_qa_sandbox_self_heal.md").read_text(encoding="utf-8")
    assert "HIGH" in policy
    assert "CRITICAL" in policy
    assert "must deny automatic execution" in policy
    assert "No automatic HIGH or CRITICAL execution" in decision
    assert "No real personal-data reads" in decision
