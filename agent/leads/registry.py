from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from agent.leads.models import LeadRecord


class LeadProvider(Protocol):
    provider_id: str

    def list_leads(self, *, max_results: int = 20) -> list[LeadRecord]:
        ...

    def read_lead(self, lead_id: str) -> LeadRecord:
        ...


@dataclass(frozen=True)
class LeadSourceDefinition:
    source: str
    display_name: str
    enabled_by_default: bool = False
    provider_status: str = "planned"
    setup_hint: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "display_name": self.display_name,
            "enabled_by_default": self.enabled_by_default,
            "provider_status": self.provider_status,
            "setup_hint": self.setup_hint,
        }


LEAD_SOURCES: tuple[LeadSourceDefinition, ...] = (
    LeadSourceDefinition("gmail", "Gmail", setup_hint="Future selected-thread adapter only; no inbox bulk ingestion."),
    LeadSourceDefinition("telegram", "Telegram", setup_hint="Future selected-chat adapter only; no reads or sends by token presence."),
    LeadSourceDefinition("apple_messages_for_business", "Apple Messages for Business", setup_hint="Future business/provider path."),
    LeadSourceDefinition("personal_imessage_manual", "Personal iMessage manual handoff", setup_hint="Manual selected text only; no Messages database scraping."),
    LeadSourceDefinition("web_form", "Web form", setup_hint="Future explicit inbound form adapter."),
    LeadSourceDefinition("manual", "Manual", provider_status="available", setup_hint="User-entered or workspace-bounded lead records."),
    LeadSourceDefinition("mock", "Mock", enabled_by_default=True, provider_status="tests_only", setup_hint="Synthetic local test data."),
)


class LeadProviderRegistry:
    def __init__(self, providers: dict[str, LeadProvider] | None = None) -> None:
        self._providers = dict(providers or {})

    def list_sources(self) -> list[LeadSourceDefinition]:
        return list(LEAD_SOURCES)

    def register(self, provider: LeadProvider) -> None:
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> LeadProvider | None:
        return self._providers.get(provider_id)
