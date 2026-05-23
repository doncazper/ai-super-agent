from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.policy import RiskLevel


APPROVED_INSPECTION_FILES = (
    "SPEC.md",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "docs/PROJECT_STATE.md",
    "docs/FEATURE_REGISTRY.md",
    "docs/FEATURE_MATURITY.md",
    "docs/FEATURE_ROADMAP.md",
    "docs/COMPLETION_REPORT.md",
    "docs/RISK_REGISTER.md",
    "docs/THREAT_MODEL.md",
    "docs/TEST_PLAN.md",
    "docs/RELEASE_CHECKLIST.md",
    "config/capabilities.yaml",
    "tests/test_policy.py",
    "tests/test_tool_broker.py",
    "tests/test_workflows.py",
    "tests/test_personal_modules.py",
    "tests/test_self_improvement.py",
    "tests/test_feature_maturity_docs.py",
    "agent/workflows/self_improvement.py",
    "logs/audit.jsonl",
    "data/audit.jsonl",
)


BLOCKED_SAFETY_WEAKENING_SUGGESTIONS = (
    {
        "title": "Enable personal-data connectors by default",
        "blocked": True,
        "reason": "Personal-data capabilities must remain disabled by default and approval-gated.",
    },
    {
        "title": "Relax ToolBroker or PolicyEngine checks for faster iteration",
        "blocked": True,
        "reason": "All tool execution must keep ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger in path.",
    },
    {
        "title": "Disable audit logging during self-improvement runs",
        "blocked": True,
        "reason": "Audit logging is a non-negotiable safety control and cannot be disabled by self-improvement.",
    },
)


@dataclass(frozen=True)
class BacklogImprovement:
    rank: int
    title: str
    why: str
    risk_level: str
    expected_files: list[str]
    tests_needed: list[str]
    rollback_plan: str
    approval_requirements: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "title": self.title,
            "why": self.why,
            "risk_level": self.risk_level,
            "expected_files": self.expected_files,
            "tests_needed": self.tests_needed,
            "rollback_plan": self.rollback_plan,
            "approval_requirements": self.approval_requirements,
        }


def self_improvement_backlog(
    broker: ToolBroker,
    *,
    mode: str = "backlog",
    dry_run: bool = False,
    max_bytes_per_file: int = 250_000,
) -> dict[str, Any]:
    """Build a deterministic, read-only improvement backlog from approved project files."""

    reads = [_read_project_file(broker, path, max_bytes=max_bytes_per_file, dry_run=dry_run) for path in APPROVED_INSPECTION_FILES]
    successful_reads = [read for read in reads if read.get("allowed") and read.get("status") == "ok"]
    public_steps = [_public_read_step(read) for read in reads]
    read_failures = [
        {
            "path": read.get("path"),
            "error": read.get("error", "read failed"),
            "allowed": read.get("allowed", False),
        }
        for read in reads
        if not (read.get("allowed") and read.get("status") == "ok")
    ]
    corpus = "\n\n".join(str(read.get("content", "")) for read in successful_reads)
    improvements = _rank_improvements(_signals(corpus))
    payload: dict[str, Any] = {
        "status": "dry_run" if dry_run else "ok",
        "workflow": "self_improvement_backlog",
        "mode": mode,
        "read_only": True,
        "dry_run": dry_run,
        "tools_used": ["filesystem.read"],
        "safety_rules": {
            "edits_files": False,
            "installs_packages": False,
            "grants_permissions": False,
            "commits": False,
            "accesses_personal_data": False,
            "requires_tool_broker_for_reads": True,
            "audit_reads": True,
        },
        "files_planned": list(APPROVED_INSPECTION_FILES),
        "files_inspected": [str(read.get("path")) for read in successful_reads],
        "read_failures": read_failures,
        "blocked_suggestions": list(BLOCKED_SAFETY_WEAKENING_SUGGESTIONS),
        "improvements": [item.to_dict() for item in improvements],
        "steps": public_steps,
        "limitations": [
            "This is a deterministic backlog generator, not an implementation mode.",
            "It proposes edits but does not perform them.",
            "It reads only the approved project documentation, tests, config, workflow, and audit-log paths listed in files_planned.",
        ],
    }
    if mode == "propose":
        payload["proposal"] = payload["improvements"][0] if payload["improvements"] else None
    return payload


def _read_project_file(broker: ToolBroker, path: str, *, max_bytes: int, dry_run: bool) -> dict[str, Any]:
    tool_call = {
        "id": f"improve_read_{_safe_call_id(path)}",
        "type": "function",
        "function": {
            "name": "filesystem.read",
            "arguments": json.dumps({"path": path, "max_bytes": max_bytes}),
        },
    }
    result = broker.dry_run(tool_call) if dry_run else broker.execute(tool_call)
    try:
        content = json.loads(result.content)
    except json.JSONDecodeError:
        content = {"raw": result.content}
    status = "ok" if result.allowed and isinstance(content, dict) and "content" in content else "error"
    return {
        "tool_name": result.tool_name,
        "tool_call_id": result.tool_call_id,
        "allowed": result.allowed,
        "dry_run": dry_run,
        "status": status if not dry_run else "planned",
        "path": content.get("path", path) if isinstance(content, dict) else path,
        "trust_level": content.get("trust_level") if isinstance(content, dict) else None,
        "content": content.get("content", "") if status == "ok" else "",
        "error": _read_error(content, dry_run=dry_run),
        "debug": result.debug,
    }


def _read_error(content: dict[str, Any] | Any, *, dry_run: bool) -> str | None:
    if dry_run:
        return None
    if isinstance(content, dict):
        return content.get("error")
    return "invalid tool result"


def _public_read_step(read: dict[str, Any]) -> dict[str, Any]:
    content = str(read.get("content", ""))
    return {
        "tool_name": read.get("tool_name"),
        "tool_call_id": read.get("tool_call_id"),
        "allowed": read.get("allowed"),
        "dry_run": read.get("dry_run"),
        "status": read.get("status"),
        "path": read.get("path"),
        "trust_level": read.get("trust_level"),
        "bytes_read": len(content.encode("utf-8")) if content else 0,
        "error": read.get("error"),
        "debug": read.get("debug"),
    }


def _signals(corpus: str) -> dict[str, bool]:
    lowered = corpus.casefold()
    return {
        "dashboard_planned": "agent dashboard" in lowered and not _marked_complete(lowered, "agent dashboard"),
        "release_gate_due": "release gate" in lowered or "checkpoint" in lowered,
        "live_validation_needed": "live validation" in lowered or "live-validated" in lowered,
        "audit_verification_needed": "audit-log tampering" in lowered or "hash-chain" in lowered or "hash chain" in lowered,
        "web_research_present": "source-grounded web research" in lowered or "web search/fetch/research" in lowered,
        "personal_connectors_present": any(token in lowered for token in ("calendar read-only", "contacts read-only", "email draft-only")),
        "memory_present": "memory v2" in lowered or "memory" in lowered,
    }


def _marked_complete(corpus: str, feature_name: str) -> bool:
    pattern = re.compile(rf"{re.escape(feature_name)}[^\n|]*\|\s*complete", re.IGNORECASE)
    return bool(pattern.search(corpus))


def _rank_improvements(signals: dict[str, bool]) -> list[BacklogImprovement]:
    candidates: list[BacklogImprovement] = [
        BacklogImprovement(
            rank=1,
            title="Run a post-workflow release gate and checkpoint",
            why=(
                "Several workflow and connector layers have changed. A release gate should re-check tests, "
                "startup policy, capability manifest validation, audit coverage, and no-bypass guarantees before the next feature batch."
            ),
            risk_level=RiskLevel.LOW.value,
            expected_files=[
                "docs/COMPLETION_REPORT.md",
                "docs/PROJECT_STATE.md",
                "docs/RELEASE_CHECKLIST.md",
                "CHANGELOG.md",
            ],
            tests_needed=[
                "python -m pytest -q",
                "python -c \"from agent.safety.validation import validate_startup_policy; validate_startup_policy()\"",
            ],
            rollback_plan="Revert documentation-only checkpoint updates if any validation result was recorded incorrectly.",
            approval_requirements="No approval required for validation; ask before committing.",
        ),
        BacklogImprovement(
            rank=2,
            title="Add audit hash-chain verification command",
            why=(
                "Audit logging is central to the safety model, but users need a direct way to verify that the JSONL hash chain has not been tampered with."
            ),
            risk_level=RiskLevel.LOW.value,
            expected_files=[
                "agent/safety/audit.py",
                "agent/ui/cli_commands.py",
                "smart_agent.py",
                "tests/test_audit.py",
                "README.md",
            ],
            tests_needed=[
                "valid audit chain reports ok",
                "tampered audit line reports failure without rewriting logs",
                "missing audit file reports clear error",
            ],
            rollback_plan="Revert audit verification command and tests; audit write path remains unchanged.",
            approval_requirements="No approval required if read-only; do not add log mutation.",
        ),
        BacklogImprovement(
            rank=3,
            title="Build Agent Dashboard v1 as an inspect-only UX",
            why=(
                "Connector, maturity, project state, permissions, audit, and roadmap status are spread across commands and docs. "
                "An inspect-only dashboard would make the safety posture easier to understand without adding new authority."
            ),
            risk_level=RiskLevel.MEDIUM.value,
            expected_files=[
                "agent/ui/dashboard.py",
                "smart_agent.py",
                "tests/test_ux_packaging.py",
                "README.md",
                "docs/FEATURE_REGISTRY.md",
            ],
            tests_needed=[
                "dashboard loads without personal-data reads",
                "secrets redacted",
                "personal connectors shown disabled by default",
                "audit/status views are read-only",
            ],
            rollback_plan="Revert dashboard command and docs; no data migrations needed.",
            approval_requirements="No personal-data approval if status-only; require review before any browser/local web server mode.",
        ),
        BacklogImprovement(
            rank=4,
            title="Add live smoke scripts for mature non-personal features",
            why=(
                "Weather and LM Studio paths have unit coverage, but live validation remains environment-specific. "
                "A small smoke script can document what was live-tested without touching personal data."
            ),
            risk_level=RiskLevel.LOW.value,
            expected_files=[
                "scripts/smoke_safe.py",
                "README.md",
                "docs/TEST_PLAN.md",
                "docs/COMPLETION_REPORT.md",
            ],
            tests_needed=[
                "smoke --dry-run performs no network/model calls",
                "missing LM Studio reports clear error",
                "missing web/weather providers report clear limitations",
            ],
            rollback_plan="Remove smoke script and docs; no persistent state should be created.",
            approval_requirements="No approval required for dry-run; live network/model checks must be explicit flags.",
        ),
        BacklogImprovement(
            rank=5,
            title="Tighten workflow-level audit summaries",
            why=(
                "Many workflows audit each tool step. A separate read-only workflow summary event would make investigations easier without changing tool execution."
            ),
            risk_level=RiskLevel.LOW.value,
            expected_files=[
                "agent/workflows/",
                "agent/safety/audit.py",
                "tests/test_workflows.py",
                "docs/THREAT_MODEL.md",
            ],
            tests_needed=[
                "workflow summary logs contain no secrets",
                "tool-level audit entries remain unchanged",
                "denied steps are summarized accurately",
            ],
            rollback_plan="Revert summary event helper; existing per-tool audit entries remain authoritative.",
            approval_requirements="No approval required; do not weaken or replace tool-level audit logs.",
        ),
    ]
    if signals.get("personal_connectors_present"):
        candidates.append(
            BacklogImprovement(
                rank=6,
                title="Add selected-scope personal connector live-read checklist",
                why=(
                    "Calendar, contacts, email, and messages are safety-sensitive. A manual checklist can guide live testing without bulk reads or default enablement."
                ),
                risk_level=RiskLevel.MEDIUM.value,
                expected_files=[
                    "docs/checklists/personal_connector_live_validation.md",
                    "docs/RELEASE_CHECKLIST.md",
                    "README.md",
                ],
                tests_needed=[
                    "docs validation covers checklist existence",
                    "personal live tests skipped by default",
                ],
                rollback_plan="Remove checklist docs; no runtime changes.",
                approval_requirements="Require explicit user approval before any live personal-data read.",
            )
        )
    return sorted(candidates, key=lambda item: item.rank)


def _safe_call_id(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", path).strip("_")[:80] or "file"
