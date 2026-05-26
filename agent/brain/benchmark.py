from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agent.brain.config import BrainRuntimeConfig
from agent.brain.models import BrainMessage
from agent.brain.mock_provider import MockBrainProvider
from agent.brain.registry import BrainProviderRegistry, default_registry, make_mock_registration


REPORT_DIR = Path("reports/brain")


@dataclass(frozen=True)
class BrainBenchmarkOptions:
    provider_id: str | None = None
    safe: bool = True
    live: bool = False


def run_benchmark(
    options: BrainBenchmarkOptions | None = None,
    *,
    registry: BrainProviderRegistry | None = None,
) -> dict[str, object]:
    active_options = options or BrainBenchmarkOptions()
    active_registry = registry or _safe_registry()
    provider_ids = [active_options.provider_id] if active_options.provider_id else list(active_registry.ordered_provider_ids())
    results = [_benchmark_provider(active_registry, provider_id, active_options) for provider_id in provider_ids if provider_id]
    report = {
        "status": "ok",
        "report_type": "brain_benchmark",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "safe": active_options.safe,
        "live": active_options.live,
        "personal_data_used": False,
        "high_risk_tools_used": False,
        "results": results,
    }
    report["report_path"] = str(write_report(report))
    return report


def write_report(report: Mapping[str, Any]) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORT_DIR / f"{report.get('report_type', 'brain_report')}_{stamp}.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def read_last_report() -> dict[str, object]:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    reports = sorted(REPORT_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not reports:
        return {"status": "not_found", "setup_hint": "Run brain benchmark or brain eval first."}
    return json.loads(reports[0].read_text(encoding="utf-8"))


def _benchmark_provider(
    registry: BrainProviderRegistry,
    provider_id: str,
    options: BrainBenchmarkOptions,
) -> dict[str, object]:
    provider = registry.get_provider(provider_id)
    if provider is None:
        return {"provider": provider_id, "status": "skip", "reason": "unknown_provider"}
    if provider.provider_id() != "mock" and not options.live:
        health = provider.health_check()
        return {
            "provider": provider.provider_id(),
            "model": "",
            "status": "skip",
            "reason": "live_provider_eval_not_enabled",
            "latency_ms": None,
            "health": health.to_dict(),
        }
    start = time.perf_counter()
    response = provider.chat([BrainMessage(role="user", content="Say hello in one short sentence.")])
    latency_ms = round((time.perf_counter() - start) * 1000, 3)
    return {
        "provider": provider.provider_id(),
        "model": response.model,
        "status": "pass" if response.ok else "fail",
        "latency_ms": latency_ms,
        "success": response.ok,
        "error": response.error.to_dict() if response.error else None,
    }


def _safe_registry() -> BrainProviderRegistry:
    return BrainProviderRegistry(
        [make_mock_registration(MockBrainProvider(response_text="Hello from the mock provider."))],
        config=BrainRuntimeConfig(default_provider="mock", provider_order=("mock",), mock_provider_enabled=True),
    )
