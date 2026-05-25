from __future__ import annotations

from agent.web_acquisition.models import ProviderDecision, SourceType


def acquisition_audit_summary(source_type: SourceType, decision: ProviderDecision | None) -> str:
    selected = decision.selected_provider if decision else None
    return (
        f"web_acquisition source_type={source_type.value} "
        f"selected_provider={selected or 'unavailable'} "
        f"paid_api_used={str(bool(decision and decision.paid_api_used)).lower()}"
    )


def audit_payload(
    *,
    source_type: SourceType,
    provider: str | None,
    network_domains: list[str] | None = None,
    decision: ProviderDecision | None = None,
) -> dict[str, object]:
    return {
        "network_domains": sorted(set(network_domains or [])),
        "result_summary": acquisition_audit_summary(source_type, decision)
        if decision is not None
        else f"web_acquisition source_type={source_type.value} provider={provider or 'unavailable'}",
    }

