from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


RISK_ORDER = {"SAFE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4, "FORBIDDEN": 5}
PERSONAL_PATTERNS = (
    "email",
    "gmail",
    "message",
    "messages",
    "telegram",
    "calendar",
    "contact",
    "contacts",
    "task",
    "tasks",
    "reminder",
    "reminders",
    "personal",
    "private",
    "inbox",
    "author metadata",
    "LOCAL_PRIVATE_DATA",
)
DEFAULT_STORE = Path("reports/autonomy/skill_proposals.json")
REQUIRED_MANIFEST_FIELDS = ("risk_level", "trust_level", "memory_behavior", "audit_fields", "status")


@dataclass(frozen=True)
class CommandObservation:
    command: str
    group: str
    risk_level: str = "LOW"
    trust_level: str = "TRUSTED_USER metadata"
    source: str = "redacted_command_metadata"
    docs_link: str = ""
    count: int = 1
    redacted: bool = True
    contains_personal_data: bool = False

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "CommandObservation":
        text = str(raw.get("command") or raw.get("command_preview") or raw.get("argv_preview") or "")
        return cls(
            command=_redact_command(text),
            group=str(raw.get("group") or raw.get("category") or _command_group(text) or "Unknown"),
            risk_level=str(raw.get("risk_level") or raw.get("risk") or "LOW").upper(),
            trust_level=str(raw.get("trust_level") or "TRUSTED_USER metadata"),
            source=str(raw.get("source") or "redacted_command_metadata"),
            docs_link=str(raw.get("docs_link") or raw.get("docs") or ""),
            count=max(1, int(raw.get("count") or 1)),
            redacted=bool(raw.get("redacted", True)),
            contains_personal_data=bool(raw.get("contains_personal_data", False)),
        )


@dataclass(frozen=True)
class SkillProposal:
    proposal_id: str
    title: str
    observed_pattern: str
    sources: list[str]
    frequency: int
    user_value: str
    risk_level: str
    required_tools: list[str]
    required_capabilities: list[str]
    suggested_manifest: dict[str, Any]
    suggested_tests: list[str]
    suggested_docs: list[str]
    privacy_review: dict[str, Any]
    approval_required: bool
    status: str = "candidate_unreviewed"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    creates_enabled_skill: bool = False
    skill_vetting_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def proposal_store_path(project_root: str | Path = ".") -> Path:
    override = os.getenv("SKILL_PROPOSAL_STORE_PATH")
    if override:
        return Path(override).expanduser().resolve()
    return Path(project_root).resolve() / DEFAULT_STORE


def propose_from_command_observations(
    observations: Iterable[CommandObservation | dict[str, Any]],
    *,
    min_frequency: int = 2,
    include_personal: bool = False,
) -> dict[str, Any]:
    normalized = [obs if isinstance(obs, CommandObservation) else CommandObservation.from_mapping(obs) for obs in observations]
    skipped: list[dict[str, str]] = []
    buckets: dict[str, list[CommandObservation]] = {}
    for obs in normalized:
        if not obs.command:
            continue
        if not obs.redacted:
            skipped.append({"source": obs.source, "reason": "unredacted metadata skipped"})
            continue
        if _is_personal_observation(obs) and not include_personal:
            skipped.append({"source": obs.source, "reason": "personal-data pattern skipped by default"})
            continue
        buckets.setdefault(_pattern_key(obs), []).append(obs)

    proposals: list[SkillProposal] = []
    for key, items in sorted(buckets.items()):
        frequency = sum(item.count for item in items)
        if frequency < min_frequency:
            continue
        proposals.append(_proposal_for_bucket(key, items, frequency))

    return {
        "status": "ok",
        "proposal_count": len(proposals),
        "proposals": [proposal.to_dict() for proposal in proposals],
        "skipped": skipped,
        "default_personal_data_policy": "skip_without_explicit_approval",
        "creates_enabled_skills": False,
        "skill_vetting_required": True,
    }


def propose_from_command_registry(project_root: str | Path = ".") -> dict[str, Any]:
    from agent.ui.command_registry import COMMANDS

    observations = [
        CommandObservation(
            command=record.command,
            group=record.group,
            risk_level=record.risk_level.split("/")[0].upper(),
            trust_level=record.trust_level,
            source=f"COMMAND_REGISTRY:{record.command_id}",
            docs_link=record.docs_link,
            redacted=True,
            contains_personal_data=_contains_personal_terms(record.trust_level) or _contains_personal_terms(record.group),
        )
        for record in COMMANDS
        if record.status == "active"
    ]
    report = propose_from_command_observations(observations)
    return _persist_report(report, project_root=project_root, source_mode="command_registry")


def propose_from_sessions(project_root: str | Path = ".") -> dict[str, Any]:
    observations, skipped_files = _load_redacted_session_observations(Path(project_root))
    report = propose_from_command_observations(observations)
    report["session_files_skipped"] = skipped_files
    return _persist_report(report, project_root=project_root, source_mode="redacted_sessions")


def list_proposals(project_root: str | Path = ".") -> dict[str, Any]:
    payload = _load_store(project_root)
    proposals = payload.get("proposals", [])
    return {
        "status": "ok",
        "proposal_count": len(proposals),
        "proposals": [
            {
                "proposal_id": proposal.get("proposal_id"),
                "title": proposal.get("title"),
                "risk_level": proposal.get("risk_level"),
                "approval_required": proposal.get("approval_required"),
                "status": proposal.get("status"),
                "frequency": proposal.get("frequency"),
            }
            for proposal in proposals
        ],
        "store_path": str(proposal_store_path(project_root)),
        "creates_enabled_skills": False,
    }


def show_proposal(proposal_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    payload = _load_store(project_root)
    for proposal in payload.get("proposals", []):
        if proposal.get("proposal_id") == proposal_id:
            return {"status": "ok", "proposal": proposal, "creates_enabled_skills": False}
    return {"status": "not_found", "proposal_id": proposal_id, "setup_hint": "Run skills propose-from-commands or skills propose-from-sessions first."}


def approve_proposal_dry_run(proposal_id: str, *, project_root: str | Path = ".") -> dict[str, Any]:
    result = show_proposal(proposal_id, project_root=project_root)
    if result["status"] != "ok":
        return result
    proposal = result["proposal"]
    return {
        "status": "dry_run_only",
        "proposal_id": proposal_id,
        "would_change_status_to": "needs_human_vetting",
        "would_create_enabled_skill": False,
        "would_import_skill": False,
        "would_enable_skill": False,
        "required_next_steps": [
            "Review proposal evidence.",
            "Create a separate vetted native skill prompt if approved.",
            "Run skill inspection/vetting before import or enablement.",
            "Update command registry, feature maturity, docs, and tests in that future prompt.",
        ],
        "approval_required": bool(proposal.get("approval_required")),
        "skill_vetting_required": True,
    }


def _persist_report(report: dict[str, Any], *, project_root: str | Path, source_mode: str) -> dict[str, Any]:
    payload = {
        **report,
        "source_mode": source_mode,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "store_policy": "redacted proposal metadata only; no skill files created or enabled",
    }
    path = proposal_store_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    payload["report_path"] = str(path)
    return payload


def _load_store(project_root: str | Path) -> dict[str, Any]:
    path = proposal_store_path(project_root)
    if not path.exists():
        return {
            "status": "requires_setup",
            "proposal_count": 0,
            "proposals": [],
            "setup_hint": "Run skills propose-from-commands or skills propose-from-sessions first.",
            "store_path": str(path),
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _load_redacted_session_observations(project_root: Path) -> tuple[list[CommandObservation], list[dict[str, str]]]:
    session_dir = project_root / "reports" / "sessions"
    if not session_dir.exists():
        return [], [{"path": str(session_dir), "reason": "no redacted session directory found"}]
    observations: list[CommandObservation] = []
    skipped: list[dict[str, str]] = []
    for path in sorted(session_dir.glob("*.json"))[:100]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            skipped.append({"path": str(path), "reason": "malformed or unreadable session metadata"})
            continue
        if not _payload_is_redacted(payload):
            skipped.append({"path": str(path), "reason": "session metadata is not marked redacted"})
            continue
        for item in payload.get("commands", []):
            if not isinstance(item, dict):
                continue
            observations.append(
                CommandObservation.from_mapping(
                    {
                        "command": item.get("command_preview") or item.get("command") or item.get("argv_preview") or "",
                        "group": item.get("group") or "Session command",
                        "risk_level": item.get("risk_level") or "LOW",
                        "trust_level": item.get("trust_level") or "TRUSTED_USER metadata",
                        "source": f"redacted_session:{path.name}",
                        "redacted": True,
                    }
                )
            )
    return observations, skipped


def _payload_is_redacted(payload: dict[str, Any]) -> bool:
    privacy = payload.get("privacy") if isinstance(payload.get("privacy"), dict) else {}
    return bool(payload.get("redacted") or payload.get("is_redacted") or privacy.get("redacted"))


def _proposal_for_bucket(key: str, observations: list[CommandObservation], frequency: int) -> SkillProposal:
    risk = _max_risk(observations)
    title = f"{_humanize_key(key)} workflow helper"
    capability_root = _capability_root(key)
    sources = sorted({obs.source for obs in observations})
    proposal_id = _proposal_id(title, sources)
    docs = sorted({obs.docs_link for obs in observations if obs.docs_link})
    review_required = RISK_ORDER.get(risk, 1) >= RISK_ORDER["HIGH"]
    suggested_manifest = {
        "skill_id": proposal_id.replace("proposal_", "candidate_"),
        "title": title,
        "status": "candidate_unreviewed",
        "risk_level": risk,
        "trust_level": "TRUSTED_USER metadata",
        "default_enabled": False,
        "approval_required": review_required,
        "required_capabilities": [f"{capability_root}.inspect_metadata"],
        "memory_behavior": "no_store",
        "audit_fields": ["timestamp", "proposal_id", "sources", "risk_level", "decision"],
        "docs_reference": "docs/native_skills/SKILL_PROPOSAL_PROCESS.md",
    }
    return SkillProposal(
        proposal_id=proposal_id,
        title=title,
        observed_pattern=f"{frequency} redacted metadata observations in `{_humanize_key(key)}`.",
        sources=sources,
        frequency=frequency,
        user_value=f"Reduce repeated manual steps for {_humanize_key(key).casefold()} after human review.",
        risk_level=risk,
        required_tools=[],
        required_capabilities=suggested_manifest["required_capabilities"],
        suggested_manifest=suggested_manifest,
        suggested_tests=[
            "proposal remains disabled by default",
            "manifest validation requires risk/trust/memory/audit metadata",
            "ToolBroker mapping exists before execution",
            "personal-data access remains disabled unless explicitly approved",
        ],
        suggested_docs=docs + ["docs/native_skills/SKILL_PROPOSAL_PROCESS.md"],
        privacy_review={
            "uses_redacted_metadata_only": True,
            "personal_data_skipped_by_default": True,
            "stores_raw_session_content": False,
            "stores_command_history": False,
        },
        approval_required=review_required,
        status="needs_review" if review_required else "candidate_unreviewed",
    )


def _max_risk(observations: Iterable[CommandObservation]) -> str:
    risk = "LOW"
    for obs in observations:
        candidate = obs.risk_level.upper().split("/")[0]
        if RISK_ORDER.get(candidate, 1) > RISK_ORDER.get(risk, 1):
            risk = candidate
    return risk


def _pattern_key(obs: CommandObservation) -> str:
    group = obs.group.strip() or _command_group(obs.command)
    return re.sub(r"[^a-z0-9]+", "_", group.casefold()).strip("_") or "general"


def _command_group(command: str) -> str:
    parts = command.split()
    if len(parts) >= 3 and parts[0].endswith("python") or (parts and parts[0] == "python"):
        return parts[2] if len(parts) > 2 else "command"
    if len(parts) >= 2:
        return parts[1]
    return "command"


def _proposal_id(title: str, sources: list[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.casefold()).strip("_")[:48]
    digest = hashlib.sha256((title + "\n" + "\n".join(sources)).encode("utf-8")).hexdigest()[:10]
    return f"proposal_{slug}_{digest}"


def _humanize_key(key: str) -> str:
    return re.sub(r"\s+", " ", key.replace("_", " ")).strip().title()


def _capability_root(key: str) -> str:
    root = key.replace("_", ".").strip(".")
    if not root:
        return "candidate_skill"
    return f"candidate_skill.{root}"


def _redact_command(command: str) -> str:
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password)=\\S+", r"\1=[REDACTED]", command)
    text = re.sub(r"(?i)(--(?:api-key|token|secret|password))\\s+\\S+", r"\1 [REDACTED]", text)
    quoted = re.sub(r'"[^"]{32,}"', '"[REDACTED_LONG_ARG]"', text)
    return quoted[:240]


def _is_personal_observation(obs: CommandObservation) -> bool:
    return obs.contains_personal_data or _contains_personal_terms(obs.group) or _contains_personal_terms(obs.trust_level) or _contains_personal_terms(obs.command)


def _contains_personal_terms(value: str) -> bool:
    lowered = value.casefold()
    return any(pattern.casefold() in lowered for pattern in PERSONAL_PATTERNS)


def validate_suggested_manifest(manifest: dict[str, Any]) -> list[str]:
    return [field for field in REQUIRED_MANIFEST_FIELDS if not manifest.get(field)]
