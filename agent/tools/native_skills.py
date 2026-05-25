from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.native_skills.finder import find_native_skills
from agent.native_skills.vetter import inspect_candidate, last_report, score_candidate as score_native_skill_candidate, vet_candidate
from agent.tools.errors import ToolError


TRUST_LEVEL = "UNTRUSTED_DOCUMENT"
MAX_SKILL_BYTES = 250_000
MAX_FOLDER_FILES = 50

SCRIPT_SUFFIXES = {".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".py", ".js", ".ts", ".rb", ".pl"}
BINARY_SUFFIXES = {".bin", ".exe", ".dylib", ".so", ".dll", ".app", ".pkg", ".jar", ".class"}
MANIFEST_NAMES = {"package.json", "pyproject.toml", "requirements.txt", "Pipfile", "Cargo.toml", "go.mod"}


def make_native_skill_tools(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def inspect_skill(path_or_skill_id: str) -> dict[str, Any]:
        report = inspect_candidate(root, path_or_skill_id)
        return {
            **report,
            "_audit": {
                "files_read": report.get("files_read", []),
                "result_summary": f"Native skill inspected: target={report.get('skill_id')}",
            },
        }

    def vet_skill_file(path: str) -> dict[str, Any]:
        report = vet_candidate(root, path)
        files_read = [str(report.get("path"))]
        files_written = [str(report["report_path"])] if report.get("report_path") else []
        return {
            **report,
            "_audit": {
                "files_read": files_read,
                "files_written": files_written,
                "result_summary": f"Native skill vetted: risk={report['risk_level']}; safe_to_import={report['safe_to_import']}; safe_to_enable={report['safe_to_enable']}",
            },
        }

    def vet_skill_folder(path: str) -> dict[str, Any]:
        report = vet_candidate(root, path)
        files_written = [str(report["report_path"])] if report.get("report_path") else []
        return {
            **report,
            "_audit": {
                "files_read": [str(report.get("path"))],
                "files_written": files_written,
                "result_summary": f"Native skill folder vetted: risk={report['risk_level']}; safe_to_import={report['safe_to_import']}",
            },
        }

    def score_candidate(path: str) -> dict[str, Any]:
        report = score_native_skill_candidate(root, path)
        return {
            **report,
            "_audit": {
                "files_read": [str(report.get("path"))],
                "result_summary": f"Native skill candidate scored: risk={report['risk_level']}; score={report['score']}",
            },
        }

    def report_last() -> dict[str, Any]:
        report = last_report(root)
        audit = {
            "files_read": [report["report_path"]] if report.get("report_path") else [],
            "result_summary": f"Native skill report lookup: status={report['status']}",
        }
        return {**report, "_audit": audit}

    def find_skill(query: str, max_results: int = 5) -> dict[str, Any]:
        return find_native_skills(query, project_root=root, max_results=max_results)

    return {
        "native_skills.inspect_skill": inspect_skill,
        "native_skills.vet_skill_file": vet_skill_file,
        "native_skills.vet_skill_folder": vet_skill_folder,
        "native_skills.score_candidate": score_candidate,
        "native_skills.report_last": report_last,
        "native_skills.find_skill": find_skill,
    }


def _resolve_workspace_file(workspace: Path, path: str) -> Path:
    target = _resolve_workspace_path(workspace, path, must_exist=True)
    if not target.is_file():
        raise ToolError("path is not a file")
    return target


def _resolve_workspace_path(workspace: Path, path: str, *, must_exist: bool) -> Path:
    if not path:
        raise ToolError("path is required")
    raw = Path(path).expanduser()
    if ".." in raw.parts:
        raise ToolError("path traversal is blocked")
    candidate = raw if raw.is_absolute() else workspace.parent / raw
    if must_exist and not candidate.exists():
        raise ToolError("path does not exist")
    resolved = candidate.resolve() if candidate.exists() else candidate.parent.resolve() / candidate.name
    if not (resolved == workspace or workspace in resolved.parents):
        raise ToolError("native skill vetting is limited to approved workspace files")
    return resolved


def _read_text(path: Path) -> str:
    data = path.read_bytes()
    if len(data) > MAX_SKILL_BYTES:
        raise ToolError("skill file exceeds max vetting size")
    if b"\x00" in data:
        raise ToolError("skill file appears to be binary")
    return data.decode("utf-8", errors="replace")


def _analyze_skill_text(text: str, *, path: str) -> dict[str, Any]:
    frontmatter, body = _parse_frontmatter(text)
    combined = f"{frontmatter}\n{body}"
    findings: list[dict[str, str]] = []

    def add(kind: str, severity: str, evidence: str, reason: str) -> None:
        findings.append({"kind": kind, "severity": severity, "evidence": evidence[:180], "reason": reason})

    _find_requested_tools(combined, add)
    _find_patterns(combined, add)

    license_info = _license_info(frontmatter, body)
    if not license_info["present"]:
        add("missing_license", "LOW", "license not found", "License information should be recorded before native porting.")

    risk = _risk_from_findings(findings)
    required_capabilities = _required_capabilities(findings)
    approval_gates = _approval_gates(findings, risk)
    score = _score(findings, risk)
    safe_to_port = _safe_to_port(risk, findings)
    return {
        "path": path,
        "trust_level": TRUST_LEVEL,
        "frontmatter": frontmatter,
        "license": license_info,
        "requested_tools": [finding["evidence"] for finding in findings if finding["kind"] == "requested_tool"],
        "findings": findings,
        "risk_level": risk.value,
        "score": score,
        "required_capabilities": required_capabilities,
        "approval_gates": approval_gates,
        "reasons": [finding["reason"] for finding in findings],
        "safe_to_port": safe_to_port,
        "recommended_native_implementation_path": _implementation_path(risk, findings),
        "memory_behavior": "no_store",
        "content_handling": "skill content treated as untrusted data; instructions inside the skill were not followed",
    }


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw = parts[1]
    body = parts[2].lstrip("\n")
    parsed: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip("'\"")
    return parsed, body


def _find_requested_tools(text: str, add: Any) -> None:
    for match in sorted(set(re.findall(r"\b[a-zA-Z_]+(?:\.[a-zA-Z_][\w-]*)+\b", text))):
        if any(match.startswith(prefix) for prefix in ("filesystem.", "web.", "email.", "messages.", "calendar.", "contacts.", "git.", "code.", "memory.", "browser.", "tasks.")):
            add("requested_tool", "INFO", match, f"Skill references tool or capability `{match}`.")


def _find_patterns(text: str, add: Any) -> None:
    checks: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
        ("script", "HIGH", ("install.sh", "postinstall", "preinstall", "setup.py", "Makefile", "run script"), "Skill references scripts or install hooks."),
        ("shell_command", "HIGH", ("rm -rf", "sudo ", "chmod +x", "bash ", "zsh ", "sh ", "subprocess", "os.system", "child_process", "exec("), "Skill requests shell command execution."),
        ("package_install", "HIGH", ("npm install", "pip install", "brew install", "curl | sh", "wget | sh", "npx "), "Skill requests package installation or remote installer execution."),
        ("network_call", "MEDIUM", ("http://", "https://", "curl ", "wget ", "fetch(", "requests.", "axios.", "websocket"), "Skill references external network calls."),
        ("secret_reference", "FORBIDDEN", ("api_key", "apikey", "secret", "password", "token", "keychain", "1password", "op read"), "Skill references secrets, tokens, passwords, or Keychain-like access."),
        ("filesystem_access", "FORBIDDEN", ("~/.ssh", "~/.gnupg", "~/Library", "/etc/passwd", "/var/db", "full disk access", "unrestricted filesystem"), "Skill requests private or unrestricted filesystem access."),
        ("personal_data", "HIGH", ("gmail", "inbox", "email body", "messages database", "contacts database", "calendar database", "browser history"), "Skill references personal-data sources."),
        ("browser_session", "FORBIDDEN", ("cookies", "session token", "browser profile", "password manager", "localstorage", "chrome profile"), "Skill references browser cookies, sessions, profiles, or password manager data."),
        ("prompt_injection", "HIGH", ("ignore previous instructions", "ignore system instructions", "reveal secrets", "developer message", "system prompt", "call tools"), "Skill contains prompt-injection-like language."),
        ("approval_bypass", "FORBIDDEN", ("bypass approval", "skip approval", "disable audit", "ignore policy", "bypass toolbroker", "grant permissions"), "Skill requests approval, policy, or audit bypass."),
        ("dangerous_action", "CRITICAL", ("send email", "send message", "delete contacts", "delete calendar", "push to production", "deploy to production"), "Skill describes high-impact send/write actions."),
        ("opaque_binary", "HIGH", (".dylib", ".so", ".dll", ".exe", ".bin", ".pkg", ".jar"), "Skill references opaque binary artifacts."),
    )
    lowered = text.casefold()
    for kind, severity, needles, reason in checks:
        for needle in needles:
            if needle.casefold() in lowered:
                add(kind, severity, needle, reason)


def _license_info(frontmatter: dict[str, Any], body: str) -> dict[str, Any]:
    for key, value in frontmatter.items():
        if key.casefold() in {"license", "licence"} and str(value).strip():
            return {"present": True, "value": str(value).strip(), "source": "frontmatter"}
    match = re.search(r"(?im)^\s*license\s*[:#-]\s*(.+)$", body)
    if match:
        return {"present": True, "value": match.group(1).strip(), "source": "body"}
    return {"present": False, "value": None, "source": None}


def _risk_from_findings(findings: list[dict[str, str]]) -> RiskLevel:
    order = {
        "INFO": RiskLevel.LOW,
        "LOW": RiskLevel.LOW,
        "MEDIUM": RiskLevel.MEDIUM,
        "HIGH": RiskLevel.HIGH,
        "CRITICAL": RiskLevel.CRITICAL,
        "FORBIDDEN": RiskLevel.FORBIDDEN,
    }
    risk = RiskLevel.LOW
    severity_order = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.FORBIDDEN]
    for finding in findings:
        candidate = order.get(finding["severity"], RiskLevel.LOW)
        if severity_order.index(candidate) > severity_order.index(risk):
            risk = candidate
    return risk


def _required_capabilities(findings: list[dict[str, str]]) -> list[str]:
    capabilities = {finding["evidence"] for finding in findings if finding["kind"] == "requested_tool"}
    for finding in findings:
        if finding["kind"] == "network_call":
            capabilities.add("web.fetch_url")
        if finding["kind"] == "filesystem_access":
            capabilities.add("filesystem.read")
        if finding["kind"] == "personal_data":
            capabilities.add("selected-scope personal connector capability")
        if finding["kind"] == "shell_command":
            capabilities.add("none: arbitrary shell is not available")
    return sorted(capabilities)


def _approval_gates(findings: list[dict[str, str]], risk: RiskLevel) -> list[str]:
    gates: set[str] = set()
    if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        gates.add("ApprovalManager required before implementation")
    if risk is RiskLevel.CRITICAL:
        gates.add("Action Center per-action approval required")
    if any(finding["kind"] == "personal_data" for finding in findings):
        gates.add("personal-data connector readiness gate")
    if any(finding["kind"] in {"shell_command", "package_install"} for finding in findings):
        gates.add("package/shell execution decision record required")
    if risk is RiskLevel.FORBIDDEN:
        gates.add("reject or redesign; forbidden behavior cannot be approved")
    return sorted(gates) or ["none for static review"]


def _score(findings: list[dict[str, str]], risk: RiskLevel) -> int:
    penalty = {"INFO": 0, "LOW": 5, "MEDIUM": 15, "HIGH": 30, "CRITICAL": 45, "FORBIDDEN": 70}
    score = 100 - sum(penalty.get(finding["severity"], 5) for finding in findings)
    if risk is RiskLevel.FORBIDDEN:
        score = min(score, 10)
    return max(0, min(100, score))


def _safe_to_port(risk: RiskLevel, findings: list[dict[str, str]]) -> str:
    if risk is RiskLevel.FORBIDDEN:
        return "no"
    if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        return "maybe"
    if any(finding["kind"] == "missing_license" for finding in findings):
        return "maybe"
    return "yes"


def _implementation_path(risk: RiskLevel, findings: list[dict[str, str]]) -> str:
    if risk is RiskLevel.FORBIDDEN:
        return "Reject or redesign as a local native skill without forbidden access, bypasses, secrets, or private data scraping."
    if any(finding["kind"] in {"shell_command", "package_install"} for finding in findings):
        return "Specify a local implementation using existing brokered capabilities; do not port shell/package-install behavior."
    if any(finding["kind"] == "network_call" for finding in findings):
        return "Use existing brokered web tools with timeout, domain policy, rate limits, and untrusted-content wrappers."
    return "Port as a reviewed local workflow mapped to existing ToolBroker capabilities with tests and docs."


def _folder_inventory(folder: Path, files: list[Path]) -> dict[str, Any]:
    scripts = [str(path.relative_to(folder)) for path in files if path.suffix in SCRIPT_SUFFIXES]
    binaries = [str(path.relative_to(folder)) for path in files if path.suffix in BINARY_SUFFIXES]
    manifests = [str(path.relative_to(folder)) for path in files if path.name in MANIFEST_NAMES]
    return {
        "file_count": len(files),
        "scripts": scripts,
        "opaque_binaries": binaries,
        "dependency_manifests": manifests,
        "has_skill_md": (folder / "SKILL.md").exists(),
    }


def _merge_folder_findings(report: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    findings = list(report["findings"])
    if inventory["scripts"]:
        findings.append({"kind": "script", "severity": "HIGH", "evidence": ", ".join(inventory["scripts"]), "reason": "Skill folder contains executable script files; they were not run."})
    if inventory["opaque_binaries"]:
        findings.append({"kind": "opaque_binary", "severity": "HIGH", "evidence": ", ".join(inventory["opaque_binaries"]), "reason": "Skill folder contains opaque binary artifacts."})
    if inventory["dependency_manifests"]:
        findings.append({"kind": "package_install", "severity": "HIGH", "evidence": ", ".join(inventory["dependency_manifests"]), "reason": "Skill folder includes dependency manifests that require separate review."})
    report["findings"] = findings
    risk = _risk_from_findings(findings)
    report["risk_level"] = risk.value
    report["score"] = _score(findings, risk)
    report["required_capabilities"] = _required_capabilities(findings)
    report["approval_gates"] = _approval_gates(findings, risk)
    report["reasons"] = [finding["reason"] for finding in findings]
    report["safe_to_port"] = _safe_to_port(risk, findings)
    report["recommended_native_implementation_path"] = _implementation_path(risk, findings)
    return report


NATIVE_SKILL_SCHEMAS = {
    "native_skills.inspect_skill": {
        "type": "function",
        "function": {
            "name": "native_skills.inspect_skill",
            "description": "Read-only inspection of a workspace/project native skill candidate or manifest id without executing it.",
            "parameters": {
                "type": "object",
                "properties": {"path_or_skill_id": {"type": "string"}},
                "required": ["path_or_skill_id"],
                "additionalProperties": False,
            },
        },
    },
    "native_skills.vet_skill_file": {
        "type": "function",
        "function": {
            "name": "native_skills.vet_skill_file",
            "description": "Statically vet a workspace SKILL.md file as untrusted document data without executing it.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    "native_skills.vet_skill_folder": {
        "type": "function",
        "function": {
            "name": "native_skills.vet_skill_folder",
            "description": "Statically vet a workspace skill folder without executing scripts or dependencies.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    "native_skills.score_candidate": {
        "type": "function",
        "function": {
            "name": "native_skills.score_candidate",
            "description": "Score a workspace skill candidate file and return a compact risk summary.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    "native_skills.report_last": {
        "type": "function",
        "function": {
            "name": "native_skills.report_last",
            "description": "Read the most recent native skill vetting report from reports/native_skills.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    "native_skills.find_skill": {
        "type": "function",
        "function": {
            "name": "native_skills.find_skill",
            "description": "Search reviewed local native skill manifests and candidate docs for a requested capability without browsing or installing external skills.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "minimum": 1, "maximum": 20},
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
}
