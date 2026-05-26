from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_hermes_safe_autonomy_docs_exist_and_define_boundaries() -> None:
    for path in (
        "docs/decisions/hermes_inspired_safe_autonomy.md",
        "docs/autonomy/SAFE_AUTONOMY_ROADMAP.md",
        "docs/autonomy/AUTONOMY_RISK_MODEL.md",
        "docs/autonomy/HIGH_RISK_AUTONOMY_GATES.md",
        "docs/autonomy/HERMES_FEATURE_COMPARISON.md",
        "docs/autonomy/UNAUTHORIZED_BYPASS_POLICY.md",
    ):
        assert (ROOT / path).exists(), path

    decision = read("docs/decisions/hermes_inspired_safe_autonomy.md")
    roadmap = read("docs/autonomy/SAFE_AUTONOMY_ROADMAP.md")
    risk_model = read("docs/autonomy/AUTONOMY_RISK_MODEL.md")
    gates = read("docs/autonomy/HIGH_RISK_AUTONOMY_GATES.md")
    comparison = read("docs/autonomy/HERMES_FEATURE_COMPARISON.md")
    bypass = read("docs/autonomy/UNAUTHORIZED_BYPASS_POLICY.md")

    for text in (decision, roadmap, risk_model, gates, comparison, bypass):
        assert "ToolBroker" in text
        assert "PolicyEngine" in text
        assert "AuditLogger" in text

    assert "No unattended high-risk workflows." in decision
    assert "No arbitrary browser automation." in decision
    assert "No background persistence." in decision
    assert "No personal-data tools." in decision
    assert "No anti-bot or CAPTCHA bypass." in decision
    assert "HIGH and CRITICAL actions cannot run unattended." in roadmap
    assert "Anti-bot/CAPTCHA/login/paywall bypass" in risk_model
    assert "CRITICAL actions require exact per-action approval and no reuse" in gates
    assert "Unsafe Interpretation Rejected" in comparison
    assert "CAPTCHA bypass" in bypass
    assert "Cloudflare or anti-bot bypass" in bypass
    assert "must report `unavailable`, `blocked`, `requires_setup`, or `unsupported`" in bypass


def test_hermes_tracking_mentions_architecture_track() -> None:
    assert "HERMES-SAFE-AUTONOMY-ARCHITECTURE" in read("docs/FEATURE_REGISTRY.md")
    assert "Hermes-Inspired Safe Autonomy Track" in read("docs/FEATURE_ROADMAP.md")
    assert "Hermes-inspired safe autonomy architecture" in read("docs/FEATURE_MATURITY.md")
    assert "Hermes-inspired safe autonomy" in read("CHANGELOG.md")
