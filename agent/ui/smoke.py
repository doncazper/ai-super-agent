from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, env_bool
from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig, LMStudioError
from agent.core.orchestrator import Orchestrator, new_session_id
from agent.core.router import RouteDecision
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.approvals import ApprovalManager
from agent.safety.policy import PolicyEngine, RiskLevel
from agent.tools.registry import ToolRegistry, default_registry
from agent.workflows.research import source_grounded_research


@dataclass(frozen=True)
class SmokeOptions:
    lmstudio: bool = False
    web: bool = False
    calendar: bool = False
    contacts: bool = False
    all_safe: bool = False
    dry_run: bool = False


@dataclass(frozen=True)
class SmokeCheck:
    name: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def run_smoke(
    options: SmokeOptions,
    *,
    runtime: RuntimeConfig | None = None,
    registry: ToolRegistry | None = None,
    client_factory: Callable[[LMStudioConfig], Any] = LMStudioClient,
) -> list[SmokeCheck]:
    config = runtime or RuntimeConfig.from_env()
    selected = _selected_options(options)
    checks: list[SmokeCheck] = [SmokeCheck("smoke_scope", "ok", ", ".join(selected) or "none")]
    if not selected:
        return checks + [SmokeCheck("smoke_selection", "fail", "select at least one smoke option")]

    policy_engine = PolicyEngine.from_config(load_capabilities_config(config.capabilities_path))
    active_registry = registry or default_registry()
    broker = ToolBroker(
        active_registry,
        policy_engine,
        AuditLogger(config.audit_log_path),
        session_id=new_session_id(),
        model=config.lmstudio_model,
        route="smoke",
        approval_manager=ApprovalManager(),
        dry_run=options.dry_run,
    )

    if "lmstudio" in selected:
        checks.extend(_lmstudio_smoke(config, active_registry, broker, client_factory=client_factory))
    if "web" in selected:
        checks.extend(_web_smoke(broker))
    if "calendar" in selected:
        checks.extend(_personal_smoke("calendar", broker, dry_run=True))
    if "contacts" in selected:
        checks.extend(_personal_smoke("contacts", broker, dry_run=True))
    return checks


def smoke_exit_code(checks: list[SmokeCheck]) -> int:
    return 1 if any(check.status == "fail" for check in checks) else 0


def format_smoke(checks: list[SmokeCheck]) -> str:
    return "\n".join(f"[{check.status}] {check.name}: {check.detail}" for check in checks)


def format_smoke_json(checks: list[SmokeCheck]) -> str:
    return json.dumps([check.to_dict() for check in checks], indent=2, sort_keys=True)


def _selected_options(options: SmokeOptions) -> list[str]:
    selected: list[str] = []
    if options.all_safe:
        selected.extend(["lmstudio", "web", "calendar", "contacts"])
    if options.lmstudio and "lmstudio" not in selected:
        selected.append("lmstudio")
    if options.web and "web" not in selected:
        selected.append("web")
    if options.calendar and "calendar" not in selected:
        selected.append("calendar")
    if options.contacts and "contacts" not in selected:
        selected.append("contacts")
    return selected


def _lmstudio_smoke(
    runtime: RuntimeConfig,
    registry: ToolRegistry,
    broker: ToolBroker,
    *,
    client_factory: Callable[[LMStudioConfig], Any],
) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    if not runtime.lmstudio_model:
        return [SmokeCheck("live_lmstudio_config", "skip", "LMSTUDIO_MODEL is not set")]
    try:
        client = client_factory(LMStudioConfig.from_runtime(runtime))
        orchestrator = Orchestrator(client, registry, broker, debug=True)
        no_tool_result = orchestrator.run("Explain RCS vs iMessage in one sentence.", no_tools=True)
        attached = _attached_tools(no_tool_result.debug_events)
        if attached:
            checks.append(SmokeCheck("lmstudio_no_tools", "fail", f"tools attached unexpectedly: {attached}"))
        else:
            checks.append(SmokeCheck("lmstudio_no_tools", "ok", "no-tool chat attached no tools"))
        checks.append(
            SmokeCheck(
                "lmstudio_no_tool_response",
                "ok" if no_tool_result.content.strip() else "fail",
                "model returned content" if no_tool_result.content.strip() else "empty model response",
            )
        )
        checks.append(
            SmokeCheck(
                "lmstudio_debug_events",
                "ok" if no_tool_result.debug_events else "fail",
                f"{len(no_tool_result.debug_events)} debug events",
            )
        )
        time_route = RouteDecision(
            name="smoke.time_tool",
            use_tools=True,
            tool_names={"time.get_current_time"},
            risk_level=RiskLevel.SAFE,
        )
        time_result = orchestrator.run("What time is it?", route=time_route)
        checks.append(
            SmokeCheck(
                "lmstudio_time_tool_path",
                "ok" if _tool_call_seen(time_result.debug_events, "time.get_current_time") else "skip",
                "model requested time tool" if _tool_call_seen(time_result.debug_events, "time.get_current_time") else "model did not request tool",
            )
        )
    except LMStudioError as exc:
        checks.append(SmokeCheck("live_lmstudio", "fail", str(exc)))
    except Exception as exc:
        checks.append(SmokeCheck("live_lmstudio", "fail", f"{type(exc).__name__}: {exc}"))
    return checks


def _web_smoke(broker: ToolBroker) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    if not env_bool("WEB_ACCESS_ENABLED", default=True):
        return [SmokeCheck("live_web_config", "skip", "WEB_ACCESS_ENABLED=false")]
    search_result = broker.execute(_tool_call("web.search", {"query": "example domain", "max_results": 2}))
    search_payload = _json(search_result.content)
    search_ok = search_result.allowed and search_payload.get("status") == "ok"
    if search_payload.get("dry_run") is True:
        checks.append(
            SmokeCheck(
                "web_search",
                "ok" if search_payload.get("would_execute") is True else "skip",
                f"dry_run policy={search_payload.get('policy_decision')}",
            )
        )
    elif search_ok:
        checks.append(SmokeCheck("web_search", "ok", str(search_payload.get("provider") or "configured")))
    elif search_payload.get("configured") is False:
        checks.append(SmokeCheck("web_search", "skip", str(search_payload.get("error") or "provider not configured")))
    else:
        checks.append(
            SmokeCheck(
                "web_search",
                "fail",
                str(search_payload.get("provider") or search_payload.get("error") or "no detail"),
            )
        )
    fetch_result = broker.execute(_tool_call("web.fetch_url", {"url": "https://example.com", "max_chars": 2000}))
    fetch_payload = _json(fetch_result.content)
    if fetch_payload.get("dry_run") is True:
        checks.append(
            SmokeCheck(
                "web_fetch_url",
                "ok" if fetch_payload.get("would_execute") is True else "skip",
                f"dry_run policy={fetch_payload.get('policy_decision')}",
            )
        )
        checks.append(SmokeCheck("research_workflow", "skip", "dry-run mode"))
        return checks
    checks.append(
        SmokeCheck(
            "web_fetch_url",
            "ok" if fetch_result.allowed and fetch_payload.get("trust_level") == "UNTRUSTED_WEB" else "fail",
            str(fetch_payload.get("url") or fetch_payload.get("error") or "no detail"),
        )
    )
    if search_ok:
        try:
            report = source_grounded_research(broker, "example domain", max_results=1, fetch_pages=False)
            checks.append(
                SmokeCheck(
                    "research_workflow",
                    "ok" if report.get("status") == "ok" else "fail",
                    str(report.get("status")),
                )
            )
        except Exception as exc:
            checks.append(SmokeCheck("research_workflow", "fail", f"{type(exc).__name__}: {exc}"))
    else:
        checks.append(SmokeCheck("research_workflow", "skip", "search provider not configured; mocked in unit tests"))
    return checks


def _personal_smoke(kind: str, broker: ToolBroker, *, dry_run: bool) -> list[SmokeCheck]:
    if kind == "calendar":
        connector_var = "CALENDAR_CONNECTOR"
        calls = [
            ("calendar.read_date_range", {"start": "2026-05-22", "end": "2026-05-23"}),
            ("calendar.find_availability", {"start": "2026-05-22", "end": "2026-05-23", "duration_minutes": 30}),
        ]
    else:
        connector_var = "CONTACTS_CONNECTOR"
        calls = [
            ("contacts.search", {"query": "Example", "max_results": 1}),
            ("contacts.read_selected", {"selected_scope_token": "example-selected-token", "requested_fields": ["display_name"]}),
        ]
    connector = os.getenv(connector_var, "").strip() or "not_configured"
    checks = [
        SmokeCheck(f"{kind}_mode", "ok", "dry-run only; no personal data read"),
        SmokeCheck(f"{kind}_connector", "ok" if connector != "not_configured" else "skip", connector),
    ]
    for tool_name, args in calls:
        result = broker.dry_run(_tool_call(tool_name, args)) if dry_run else broker.execute(_tool_call(tool_name, args))
        payload = _json(result.content)
        safe_dry_run = (
            payload.get("dry_run") is True
            and payload.get("would_execute") is False
            and payload.get("policy_decision") in {"DENY", "ASK"}
        )
        checks.append(
            SmokeCheck(
                f"{tool_name}_dry_run",
                "ok" if safe_dry_run else "fail",
                f"policy={payload.get('policy_decision')} approval_required={payload.get('approval_required')}",
            )
        )
    return checks


def _tool_call(tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": f"smoke_{tool_name.replace('.', '_')}",
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _json(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "malformed JSON content"}
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def _attached_tools(debug_events: list[dict[str, Any]]) -> list[str]:
    for event in debug_events:
        if event.get("event") == "route":
            attached = event.get("tools_attached") or []
            return [str(item) for item in attached]
    return []


def _tool_call_seen(debug_events: list[dict[str, Any]], tool_name: str) -> bool:
    return any(event.get("event") == "tool_call" and event.get("tool_name") == tool_name for event in debug_events)
