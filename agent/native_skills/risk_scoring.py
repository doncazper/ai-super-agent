from __future__ import annotations

from typing import Any

from agent.safety.policy import RiskLevel


SEVERITY_TO_RISK = {
    "INFO": RiskLevel.LOW,
    "LOW": RiskLevel.LOW,
    "MEDIUM": RiskLevel.MEDIUM,
    "HIGH": RiskLevel.HIGH,
    "CRITICAL": RiskLevel.CRITICAL,
    "FORBIDDEN": RiskLevel.FORBIDDEN,
}

RISK_ORDER = [
    RiskLevel.SAFE,
    RiskLevel.LOW,
    RiskLevel.MEDIUM,
    RiskLevel.HIGH,
    RiskLevel.CRITICAL,
    RiskLevel.FORBIDDEN,
]


def risk_from_findings(findings: list[dict[str, str]]) -> RiskLevel:
    risk = RiskLevel.LOW
    for finding in findings:
        candidate = SEVERITY_TO_RISK.get(finding.get("severity", "LOW"), RiskLevel.LOW)
        if RISK_ORDER.index(candidate) > RISK_ORDER.index(risk):
            risk = candidate
    return risk


def score_findings(findings: list[dict[str, str]], risk: RiskLevel) -> int:
    penalty = {"INFO": 0, "LOW": 5, "MEDIUM": 15, "HIGH": 30, "CRITICAL": 45, "FORBIDDEN": 70}
    score = 100 - sum(penalty.get(finding.get("severity", "LOW"), 5) for finding in findings)
    if risk is RiskLevel.FORBIDDEN:
        score = min(score, 10)
    return max(0, min(100, score))


def safe_to_import(risk: RiskLevel, findings: list[dict[str, str]]) -> str:
    if risk is RiskLevel.FORBIDDEN:
        return "no"
    if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        return "no"
    if any(finding.get("kind") == "missing_license" for finding in findings):
        return "maybe"
    return "yes"


def safe_to_enable(risk: RiskLevel, findings: list[dict[str, str]]) -> str:
    if risk in {RiskLevel.FORBIDDEN, RiskLevel.CRITICAL, RiskLevel.HIGH}:
        return "no"
    if any(finding.get("kind") in {"missing_license", "unknown_capability"} for finding in findings):
        return "maybe"
    return "maybe"


def required_capabilities(findings: list[dict[str, str]]) -> list[str]:
    capabilities = {finding["evidence"] for finding in findings if finding.get("kind") == "requested_tool"}
    for finding in findings:
        kind = finding.get("kind")
        if kind == "network_call":
            capabilities.add("web.fetch_url")
        if kind == "filesystem_access":
            capabilities.add("filesystem.read")
        if kind == "personal_data":
            capabilities.add("selected-scope personal connector capability")
        if kind == "shell_command":
            capabilities.add("none: arbitrary shell is not available")
    return sorted(capabilities)


def approval_gates(findings: list[dict[str, str]], risk: RiskLevel) -> list[str]:
    gates: set[str] = set()
    if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        gates.add("ApprovalManager required before implementation")
    if risk is RiskLevel.CRITICAL:
        gates.add("Action Center per-action approval required")
    if any(finding.get("kind") == "personal_data" for finding in findings):
        gates.add("personal-data connector readiness gate")
    if any(finding.get("kind") in {"shell_command", "package_install"} for finding in findings):
        gates.add("package/shell execution decision record required")
    if risk is RiskLevel.FORBIDDEN:
        gates.add("reject or redesign; forbidden behavior cannot be approved")
    return sorted(gates) or ["none for static review"]


def implementation_path(risk: RiskLevel, findings: list[dict[str, str]]) -> str:
    if risk is RiskLevel.FORBIDDEN:
        return "Reject or redesign as a local native skill without forbidden access, bypasses, secrets, or private data scraping."
    if any(finding.get("kind") in {"shell_command", "package_install"} for finding in findings):
        return "Specify a local implementation using existing brokered capabilities; do not port shell/package-install behavior."
    if any(finding.get("kind") == "network_call" for finding in findings):
        return "Use existing brokered web tools with timeout, domain policy, rate limits, and untrusted-content wrappers."
    return "Port as a reviewed local workflow mapped to existing ToolBroker capabilities with tests and docs."


def recommended_tests(findings: list[dict[str, str]], risk: RiskLevel) -> list[str]:
    tests = ["manifest validation", "ToolBroker routing test", "AuditLogger evidence test"]
    kinds = {finding.get("kind") for finding in findings}
    if "network_call" in kinds:
        tests.append("network disabled/default-denied test")
    if "filesystem_access" in kinds:
        tests.append("workspace path-boundary test")
    if "prompt_injection" in kinds:
        tests.append("untrusted skill prompt-injection regression")
    if "approval_bypass" in kinds or risk in {RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.FORBIDDEN}:
        tests.append("approval/policy bypass denial test")
    return tests


def recommended_docs(findings: list[dict[str, str]]) -> list[str]:
    docs = ["native skill README", "command registry entry", "feature maturity note"]
    if any(finding.get("kind") == "missing_license" for finding in findings):
        docs.append("license/provenance record")
    if any(finding.get("kind") in {"network_call", "personal_data", "filesystem_access"} for finding in findings):
        docs.append("risk and threat-model note")
    return docs


def review_required(risk: RiskLevel, findings: list[dict[str, str]]) -> bool:
    return risk in {RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.FORBIDDEN} or any(
        finding.get("kind") in {"missing_license", "unknown_capability", "opaque_binary"} for finding in findings
    )


def score_report(findings: list[dict[str, str]]) -> dict[str, Any]:
    risk = risk_from_findings(findings)
    return {
        "risk_level": risk.value,
        "score": score_findings(findings, risk),
        "safe_to_import": safe_to_import(risk, findings),
        "safe_to_enable": safe_to_enable(risk, findings),
        "required_capabilities": required_capabilities(findings),
        "required_approvals": approval_gates(findings, risk),
        "recommended_native_port_path": implementation_path(risk, findings),
        "recommended_tests": recommended_tests(findings, risk),
        "recommended_docs": recommended_docs(findings),
        "review_required": review_required(risk, findings),
    }
