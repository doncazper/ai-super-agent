from __future__ import annotations

from pathlib import Path

from agent.ui.command_registry import list_commands


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_authorized_web_automation_policy_docs_exist() -> None:
    for path in (
        "docs/decisions/authorized_web_automation_boundary.md",
        "docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md",
        "docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md",
        "docs/web/FIRST_PARTY_TESTING_POLICY.md",
        "docs/web/DEEP_SCAN_POLICY.md",
    ):
        assert (ROOT / path).exists(), path


def test_bypass_categories_are_forbidden() -> None:
    combined = "\n".join(
        _read(path)
        for path in (
            "docs/decisions/authorized_web_automation_boundary.md",
            "docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md",
            "docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md",
        )
    )

    for phrase in (
        "CAPTCHA bypass",
        "Cloudflare or anti-bot bypass",
        "proxy evasion",
        "rate-limit evasion",
        "login-wall bypass",
        "paywall bypass",
        "cookie/session scraping",
        "human impersonation",
        "stealth browser automation",
    ):
        assert phrase in combined


def test_allowed_authorized_paths_are_scoped() -> None:
    policy = _read("docs/web/AUTHORIZED_WEB_AUTOMATION_POLICY.md")

    for phrase in (
        "First-party staging app testing",
        "Official CAPTCHA/Turnstile/reCAPTCHA test keys",
        "User-in-the-loop manual login",
        "Official APIs/OAuth",
        "Approved partner access",
        "Contracted security testing with written scope",
        "User-provided exports",
        "Browser selected-page handoff",
    ):
        assert phrase in policy


def test_blocked_sources_return_unavailable_not_bypass() -> None:
    blocked = _read("docs/web/BLOCKED_SOURCE_AND_BYPASS_POLICY.md")

    assert "Return unavailable" in blocked
    assert "bypass_attempted=false" in blocked
    assert "do not solve or bypass" in blocked
    assert "do not evade" in blocked


def test_deep_scan_is_planned_and_gated() -> None:
    policy = _read("docs/web/DEEP_SCAN_POLICY.md")

    assert "Deep scan is planned, not implemented." in policy
    for phrase in (
        "Explicit user approval",
        "Domain allowlist",
        "Crawl budget",
        "Rate limit",
        "Robots policy",
        "Legal/compliance note",
        "Data retention policy",
        "No paid API unless allowed",
        "No bypass/evasion",
        "Dogfood/eval suite",
        "UNTRUSTED_WEB",
    ):
        assert phrase in policy


def test_planned_deep_scan_commands_are_conservative() -> None:
    commands = {record.command_id: record for record in list_commands()}

    for command_id in ("CMD-WEB-033", "CMD-WEB-034", "CMD-WEB-035"):
        record = commands[command_id]
        assert record.status in {"planned", "stubbed"}
        assert record.example
        assert record.risk_level in {"LOW", "MEDIUM"}
        assert "planned" in record.toolbroker_path
        assert "no memory write" in record.memory_behavior
