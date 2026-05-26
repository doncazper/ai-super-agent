from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent.media.models import MediaLicenseInfo
from agent.media.provider_registry import MediaProviderRegistry, default_media_provider_registry


@dataclass(frozen=True)
class MediaProviderLicenseRecord:
    provider_id: str
    status: str
    license_name: str
    commercial_use: str
    attribution_required: bool
    setup_hint: str
    docs_path: str
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "license_name": self.license_name,
            "commercial_use": self.commercial_use,
            "attribution_required": self.attribution_required,
            "setup_hint": self.setup_hint,
            "docs_path": self.docs_path,
            "notes": list(self.notes),
        }

    def to_license_info(self) -> MediaLicenseInfo:
        return MediaLicenseInfo(
            status=self.status,
            license_name=self.license_name,
            usage=self.commercial_use,
            attribution_required=self.attribution_required,
            source=self.docs_path,
            notes=self.notes,
        )


def provider_license_records(
    registry: MediaProviderRegistry | None = None,
) -> tuple[MediaProviderLicenseRecord, ...]:
    active_registry = registry or default_media_provider_registry()
    records: list[MediaProviderLicenseRecord] = []
    for provider in active_registry.list_providers():
        if provider.provider_id == "mock":
            records.append(
                MediaProviderLicenseRecord(
                    provider_id=provider.provider_id,
                    status="test_only",
                    license_name="fixture-only",
                    commercial_use="not for production output",
                    attribution_required=False,
                    setup_hint=provider.setup_hint,
                    docs_path=provider.docs_path,
                    notes=("Mock provider produces no real media and grants no usage rights.",),
                )
            )
        elif provider.paid_api or provider.provider_id == "external_paid":
            records.append(
                MediaProviderLicenseRecord(
                    provider_id=provider.provider_id,
                    status="blocked",
                    license_name="unknown",
                    commercial_use="blocked until explicit provider terms are reviewed",
                    attribution_required=False,
                    setup_hint=provider.setup_hint,
                    docs_path=provider.docs_path,
                    notes=("Paid/cloud provider use is disabled by default.",),
                )
            )
        else:
            records.append(
                MediaProviderLicenseRecord(
                    provider_id=provider.provider_id,
                    status="requires_review",
                    license_name="unknown",
                    commercial_use="requires model/provider license review before use",
                    attribution_required=False,
                    setup_hint=provider.setup_hint,
                    docs_path=provider.docs_path,
                    notes=("Do not claim commercial rights without model/provider evidence.",),
                )
            )
    return tuple(records)


def build_license_report(registry: MediaProviderRegistry | None = None) -> dict[str, Any]:
    records = provider_license_records(registry)
    return {
        "status": "ok",
        "legal_advice": False,
        "provider_count": len(records),
        "providers": [record.to_dict() for record in records],
        "commercial_use_requires_evidence": True,
        "paid_apis_enabled": False,
        "generation_performed": False,
        "warnings": [
            "This report is operational risk metadata, not legal advice.",
            "Commercial-use status must come from provider/model license evidence before generation.",
            "Mock/test provider records grant no production usage rights.",
        ],
    }
