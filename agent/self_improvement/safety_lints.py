from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .artifact_hashes import build_artifact_hash_report, sha256_text


@dataclass(frozen=True)
class SafetyLintRule:
    rule_id: str
    description: str
    severity: str
    patterns: tuple[re.Pattern[str], ...]
    blocks_self_heal_safe_only: bool = True


SAFETY_LINT_RULES: tuple[SafetyLintRule, ...] = (
    SafetyLintRule("audit_logging_disabled", "Disables or bypasses audit logging.", "high", (re.compile(r"(?i)\b(disable|skip|bypass)[_\s-]*audit"), re.compile(r"(?i)AuditLogger\s*=\s*None"))),
    SafetyLintRule("policy_engine_weakened", "Weakens PolicyEngine checks or risk decisions.", "high", (re.compile(r"(?i)\b(weaken|bypass|skip)[_\s-]*policy"), re.compile(r"(?i)PolicyEngine.*return\s+True"))),
    SafetyLintRule("toolbroker_bypass", "Bypasses ToolBroker for tool execution.", "high", (re.compile(r"(?i)\bbypass[_\s-]*ToolBroker\b"), re.compile(r"(?i)direct[_\s-]*tool[_\s-]*execution"))),
    SafetyLintRule("critical_approval_reuse", "Allows CRITICAL approval reuse or non-explicit approval.", "critical", (re.compile(r"(?i)CRITICAL.*(reuse|cached|previous).*approval"), re.compile(r"(?i)per[_\s-]?action\s*[:=]\s*false"))),
    SafetyLintRule("personal_data_default_enabled", "Enables personal-data capabilities by default.", "high", (re.compile(r"(?i)(personal[_\s-]*data|LOCAL_PRIVATE_DATA).*default[_\s-]*enabled\s*[:=]\s*true"), re.compile(r"(?i)PERSONAL.*enabled\s*[:=]\s*true"))),
    SafetyLintRule("background_persistence_added", "Adds background persistence, daemon behavior, or unattended loops.", "high", (re.compile(r"(?i)\b(background|daemon|launchd|cron|persistent)[_\s-]*(service|loop|worker|agent)"), re.compile(r"(?i)while\s+True:.*sleep", re.DOTALL))),
    SafetyLintRule("filesystem_scope_expanded", "Expands filesystem access outside approved workspace boundaries.", "high", (re.compile(r"(?i)(full disk access|broad filesystem|outside workspace|path traversal allowed)"), re.compile(r"(?i)WorkspaceGuard.*disabled"))),
    SafetyLintRule("redaction_removed", "Removes or bypasses secret redaction.", "high", (re.compile(r"(?i)(disable|remove|bypass)[_\s-]*redact"), re.compile(r"(?i)SecretRedactor\s*=\s*None"))),
    SafetyLintRule("package_install_without_approval", "Adds package installation without approval.", "high", (re.compile(r"(?i)\b(pip|npm|pnpm|yarn|brew)\s+install\b"), re.compile(r"(?i)subprocess\..*(pip|npm|pnpm|yarn|brew).*install"))),
    SafetyLintRule("live_provider_default", "Enables live provider calls by default.", "high", (re.compile(r"(?i)LIVE_.*ENABLED\s*=\s*true"), re.compile(r"(?i)ALLOW_PAID_APIS\s*=\s*true"), re.compile(r"(?i)default_provider\s*[:=]\s*(live|paid|cloud)"))),
    SafetyLintRule("server_listener_default", "Starts a server or listener by default.", "high", (re.compile(r"(?i)(start|run).*(server|listener).*default"), re.compile(r"(?i)APP_BRIDGE_ENABLED\s*=\s*true"), re.compile(r"(?i)\.listen\("))),
    SafetyLintRule("secret_storage", "Stores raw secrets or credential values.", "critical", (re.compile(r"(?i)(write_text|json\.dump).*?(token|secret|password|private_key)"), re.compile(r"(?i)store_raw_secret"))),
    SafetyLintRule("backup_restore_weakened", "Weakens backup restore policy or integrity checks.", "high", (re.compile(r"(?i)(skip|disable|bypass).*backup.*(integrity|verify|hash)"), re.compile(r"(?i)restore.*without.*(approval|verification)"))),
)


def lint_diff_text(diff_text: str) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    added_text = "\n".join(line[1:] for line in diff_text.splitlines() if line.startswith("+") and not line.startswith("+++"))
    for rule in SAFETY_LINT_RULES:
        if any(pattern.search(added_text) for pattern in rule.patterns):
            findings.append(
                {
                    "rule_id": rule.rule_id,
                    "severity": rule.severity,
                    "description": rule.description,
                    "blocks_self_heal_safe_only": rule.blocks_self_heal_safe_only,
                    "evidence_hash": sha256_text(f"{rule.rule_id}:{added_text}"),
                }
            )
    blockers = [finding for finding in findings if finding["blocks_self_heal_safe_only"]]
    return {
        "status": "blocked" if blockers else "ok",
        "finding_count": len(findings),
        "blocker_count": len(blockers),
        "safe_only_allowed": not blockers,
        "raw_evidence_included": False,
        "findings": findings,
    }


def lint_project_diff(project_root: str | Path = ".") -> dict[str, object]:
    root = Path(project_root).resolve()
    return lint_diff_text(_git_diff(root))


def verify_self_heal_artifacts(project_root: str | Path = ".") -> dict[str, object]:
    root = Path(project_root).resolve()
    lint_report = lint_project_diff(root)
    hash_report = build_artifact_hash_report(root)
    return {
        "status": "blocked" if lint_report["safe_only_allowed"] is False else "ok",
        "safe_only_allowed": bool(lint_report["safe_only_allowed"]),
        "lint_report": lint_report,
        "artifact_hashes": hash_report,
        "side_effects": "none; verify-only",
    }


def summarize_lint_findings(findings: Iterable[dict[str, object]]) -> list[str]:
    return [f"{item.get('severity')} {item.get('rule_id')}: {item.get('description')}" for item in findings]


def _git_diff(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "diff", "--no-ext-diff"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return completed.stdout if completed.returncode in {0, 1} else ""
