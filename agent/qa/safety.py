from __future__ import annotations

from agent.qa.models import CommandInventoryItem


PERSONAL_MARKERS = (
    "calendar",
    "contact",
    "email",
    "message",
    "gmail",
    "telegram",
    "reddit",
    "lead",
    "privacy delete",
)
WRITE_MARKERS = (
    "write",
    "delete",
    "clear",
    "restore",
    "send",
    "commit",
    "create",
    "update",
    "patch",
    "copy",
    "save",
)
READ_ONLY_MARKERS = (
    " status",
    " doctor",
    " list",
    " show",
    " explain",
    " providers",
    " capabilities",
    " matrix",
    " validate",
    " policy",
    " report",
    " search",
    " next",
)


def risk_parts(risk_level: str) -> set[str]:
    return {part.strip() for part in risk_level.split("/") if part.strip()}


def is_high_or_critical(item: CommandInventoryItem) -> bool:
    parts = risk_parts(item.risk_level)
    return bool(parts & {"HIGH", "CRITICAL", "FORBIDDEN"})


def requires_personal_data(item: CommandInventoryItem) -> bool:
    haystack = " ".join(
        [
            item.command,
            item.group,
            item.description,
            item.requires_connector,
            item.requires_provider,
            item.trust_level,
            item.side_effects,
        ]
    ).lower()
    return any(marker in haystack for marker in PERSONAL_MARKERS) and "metadata" not in item.trust_level.lower()


def has_write_or_send_side_effect(item: CommandInventoryItem) -> bool:
    haystack = " ".join([item.command, item.description, item.side_effects]).lower()
    if "metadata-only" in haystack or "read metadata" in haystack:
        return False
    return any(marker in haystack for marker in WRITE_MARKERS)


def requires_provider_setup(item: CommandInventoryItem) -> bool:
    provider = item.requires_provider.lower()
    connector = item.requires_connector.lower()
    return not provider in {"none", "n/a", ""} or any(word in connector for word in ("lm studio", "web", "brain", "reddit", "v2ex", "weather"))


def missing_metadata(item: CommandInventoryItem) -> list[str]:
    missing: list[str] = []
    for field_name in ("example", "risk_level", "docs_link", "test_coverage"):
        value = getattr(item, field_name)
        if not value or str(value).strip().lower() in {"n/a", "none", "planned only"}:
            missing.append(field_name)
    return missing


def classify_qa_tier(item: CommandInventoryItem) -> tuple[int, bool, str]:
    if item.status in {"planned", "stubbed", "deprecated", "legacy", "removed", "blocked"}:
        return 0, False, f"status_{item.status}"
    if is_high_or_critical(item):
        return 6 if "HIGH" in risk_parts(item.risk_level) else 7, False, "high_or_critical_manual_only"
    if requires_personal_data(item):
        return 4, False, "personal_data_dry_run_only"
    if has_write_or_send_side_effect(item):
        return 3, False, "requires_disposable_workspace_or_manual_review"
    command = f" {item.command.lower()}"
    if requires_provider_setup(item):
        return 2, True, ""
    if any(marker in command for marker in READ_ONLY_MARKERS):
        return 1, True, ""
    return 1 if risk_parts(item.risk_level) <= {"SAFE", "LOW"} else 2, risk_parts(item.risk_level) <= {"SAFE", "LOW"}, ""
