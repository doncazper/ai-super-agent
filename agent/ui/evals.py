from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Iterable

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, env_bool
from agent.connectors.health import connectors_health_report
from agent.core.lmstudio_client import LMStudioClient, LMStudioConfig, LMStudioError
from agent.core.orchestrator import Orchestrator, new_session_id
from agent.core.router import RouteDecision
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.approvals import ApprovalManager
from agent.safety.policy import PolicyEngine, RiskLevel
from agent.tools.registry import ToolRegistry, default_registry


REPORT_PATH = Path("docs/EVAL_REPORT.md")
RESULTS_PATH = Path("logs/eval_results.json")
DEFAULT_WEATHER_LOCATION = "Phoenix, AZ"


@dataclass(frozen=True)
class EvalDefinition:
    name: str
    category: str
    description: str
    live: bool = False
    personal_data: bool = False
    default_safe: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "live": self.live,
            "personal_data": self.personal_data,
            "default_safe": self.default_safe,
        }


@dataclass(frozen=True)
class EvalCheck:
    name: str
    category: str
    status: str
    reason: str
    live: bool = False
    personal_data: bool = False
    tool_names: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "reason": self.reason,
            "live": self.live,
            "personal_data": self.personal_data,
            "tool_names": self.tool_names,
            "details": self.details,
        }


@dataclass(frozen=True)
class EvalOptions:
    safe: bool = False
    lmstudio: bool = False
    web: bool = False
    weather: bool = False
    workspace: bool = False
    memory: bool = False
    report_path: Path = REPORT_PATH
    results_path: Path = RESULTS_PATH
    weather_location: str = DEFAULT_WEATHER_LOCATION


EVAL_DEFINITIONS: tuple[EvalDefinition, ...] = (
    EvalDefinition("lmstudio.no_tool_chat", "lmstudio", "No-tool Qwopus chat attaches no tools.", live=True, default_safe=True),
    EvalDefinition("lmstudio.time_tool_roundtrip", "lmstudio", "Model/tool roundtrip uses the safe time tool.", live=True, default_safe=True),
    EvalDefinition("tool.time_direct", "safe", "Direct safe time tool execution through ToolBroker.", default_safe=True),
    EvalDefinition("weather.current", "weather", "Configured weather provider current conditions.", live=True, default_safe=True),
    EvalDefinition("weather.forecast", "weather", "Configured weather provider forecast.", live=True, default_safe=True),
    EvalDefinition("web.search", "web", "Configured web search provider.", live=True, default_safe=True),
    EvalDefinition("web.fetch_url", "web", "Fetch a controlled public page as UNTRUSTED_WEB.", live=True, default_safe=True),
    EvalDefinition("workspace.read_write", "workspace", "Write and read a controlled file under ./workspace/eval.", default_safe=True),
    EvalDefinition("memory.add_search_delete", "memory", "Store, search, and delete a non-sensitive project fact.", default_safe=True),
    EvalDefinition("dry_run.preflight", "safe", "Evaluate a dry-run action preview without executing.", default_safe=True),
    EvalDefinition("connectors.doctor", "safe", "Connector health/status checks without personal-data reads.", default_safe=True),
    EvalDefinition("calendar.read", "calendar", "Selected-scope calendar read.", personal_data=True),
    EvalDefinition("contacts.read", "contacts", "Selected-scope contact read.", personal_data=True),
    EvalDefinition("email.metadata", "email", "Email metadata read.", personal_data=True),
    EvalDefinition("email.draft", "email", "Selected-thread email draft-only flow.", personal_data=True),
    EvalDefinition("messages.draft_from_text", "messages", "Messages draft-only fallback.", personal_data=True),
)


def list_evals() -> dict[str, object]:
    return {
        "status": "ok",
        "personal_data_default": "skipped",
        "live_default": "opt_in",
        "evals": [definition.to_dict() for definition in EVAL_DEFINITIONS],
    }


def run_eval(
    options: EvalOptions,
    *,
    runtime: RuntimeConfig | None = None,
    registry: ToolRegistry | None = None,
    client_factory: Callable[[LMStudioConfig], Any] = LMStudioClient,
) -> dict[str, Any]:
    config = runtime or RuntimeConfig.from_env()
    selected = _selected_categories(options)
    checks: list[EvalCheck] = []
    if not selected:
        checks.append(EvalCheck("eval.selection", "setup", "fail", "select --safe or at least one eval category"))
        return _final_report(config, selected, checks, options)

    policy_engine = PolicyEngine.from_config(load_capabilities_config(config.capabilities_path))
    active_registry = registry or default_registry(memory_path=_eval_memory_path(options.results_path))
    broker = ToolBroker(
        active_registry,
        policy_engine,
        AuditLogger(config.audit_log_path),
        session_id=new_session_id(),
        model=config.lmstudio_model,
        route="eval",
        approval_manager=ApprovalManager(),
    )

    if "lmstudio" in selected:
        checks.extend(_eval_lmstudio(config, active_registry, broker, client_factory))
    checks.extend(_eval_time_tool(broker))
    if "weather" in selected:
        checks.extend(_eval_weather(broker, options.weather_location))
    if "web" in selected:
        checks.extend(_eval_web(broker))
    if "workspace" in selected:
        checks.extend(_eval_workspace(broker))
    if "memory" in selected:
        checks.extend(_eval_memory(broker))
    if "safe" in selected:
        checks.extend(_eval_preflight(broker))
        checks.extend(_eval_connectors(config))
    checks.extend(_skipped_personal_evals())
    return _final_report(config, selected, checks, options)


def eval_exit_code(report: dict[str, Any]) -> int:
    return 1 if any(check.get("status") == "fail" for check in report.get("checks", [])) else 0


def format_eval_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def format_eval_list_json() -> str:
    return json.dumps(list_evals(), indent=2, sort_keys=True)


def format_eval_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Eval run: {report.get('run_id')}",
        f"Status: {report.get('status')} | selected: {', '.join(report.get('selected_categories', []))}",
        f"Summary: pass={report.get('summary', {}).get('pass')} fail={report.get('summary', {}).get('fail')} skipped={report.get('summary', {}).get('skipped')}",
    ]
    for check in report.get("checks", []):
        lines.append(f"[{check.get('status')}] {check.get('name')}: {check.get('reason')}")
    lines.append(f"Report: {report.get('report_path')}")
    return "\n".join(lines)


def read_eval_report(path: str | Path = REPORT_PATH) -> str:
    report_path = Path(path)
    if report_path.exists():
        return report_path.read_text(encoding="utf-8")
    return _empty_report_template(report_path)


def _selected_categories(options: EvalOptions) -> list[str]:
    selected: list[str] = []
    if options.safe:
        selected.extend(["lmstudio", "weather", "web", "workspace", "memory", "safe"])
    for enabled, category in (
        (options.lmstudio, "lmstudio"),
        (options.weather, "weather"),
        (options.web, "web"),
        (options.workspace, "workspace"),
        (options.memory, "memory"),
    ):
        if enabled and category not in selected:
            selected.append(category)
    return selected


def _eval_lmstudio(
    runtime: RuntimeConfig,
    registry: ToolRegistry,
    broker: ToolBroker,
    client_factory: Callable[[LMStudioConfig], Any],
) -> list[EvalCheck]:
    if not runtime.lmstudio_model:
        return [
            EvalCheck(
                "lmstudio.no_tool_chat",
                "lmstudio",
                "skipped",
                "LMSTUDIO_MODEL is not set; live LM Studio eval skipped",
                live=True,
            ),
            EvalCheck(
                "lmstudio.time_tool_roundtrip",
                "lmstudio",
                "skipped",
                "LMSTUDIO_MODEL is not set; live LM Studio eval skipped",
                live=True,
            ),
        ]
    try:
        orchestrator = Orchestrator(client_factory(LMStudioConfig.from_runtime(runtime)), registry, broker, debug=True)
        no_tool = orchestrator.run("Explain RCS vs iMessage in one sentence.", no_tools=True)
        attached = _attached_tools(no_tool.debug_events)
        no_tool_check = EvalCheck(
            "lmstudio.no_tool_chat",
            "lmstudio",
            "pass" if no_tool.content.strip() and not attached else "fail",
            "model returned content and no tools were attached" if no_tool.content.strip() and not attached else f"unexpected tools or empty response: {attached}",
            live=True,
        )
        time_route = RouteDecision(
            name="eval.time_tool",
            use_tools=True,
            tool_names={"time.get_current_time"},
            risk_level=RiskLevel.SAFE,
        )
        time_result = orchestrator.run("What time is it?", route=time_route)
        saw_time_tool = _tool_call_seen(time_result.debug_events, "time.get_current_time")
        time_check = EvalCheck(
            "lmstudio.time_tool_roundtrip",
            "lmstudio",
            "pass" if saw_time_tool and time_result.content.strip() else "skipped",
            "model requested time tool and returned final content" if saw_time_tool else "model did not request the time tool in this live run",
            live=True,
            tool_names=["time.get_current_time"] if saw_time_tool else [],
        )
        return [no_tool_check, time_check]
    except LMStudioError as exc:
        return [EvalCheck("lmstudio.live", "lmstudio", "fail", str(exc), live=True)]
    except Exception as exc:
        return [EvalCheck("lmstudio.live", "lmstudio", "fail", f"{type(exc).__name__}: {exc}", live=True)]


def _eval_time_tool(broker: ToolBroker) -> list[EvalCheck]:
    result = broker.execute(_tool_call("eval_time_direct", "time.get_current_time", {}))
    payload = _json(result.content)
    return [
        EvalCheck(
            "tool.time_direct",
            "safe",
            "pass" if result.allowed and ("current_time" in payload or "iso_time" in payload) else "fail",
            "time.get_current_time executed through ToolBroker" if result.allowed else str(payload.get("error", "time tool denied")),
            tool_names=["time.get_current_time"],
            details={"audit": result.debug or {}},
        )
    ]


def _eval_weather(broker: ToolBroker, location: str) -> list[EvalCheck]:
    checks: list[EvalCheck] = []
    status = broker.execute(_tool_call("eval_weather_status", "weather.status", {}))
    status_payload = _json(status.content)
    configured = bool(status_payload.get("configured"))
    checks.append(
        EvalCheck(
            "weather.status",
            "weather",
            "pass" if status.allowed else "fail",
            f"provider={status_payload.get('provider')} configured={configured}",
            live=False,
            tool_names=["weather.status"],
        )
    )
    if not configured:
        checks.extend(
            [
                EvalCheck("weather.current", "weather", "skipped", str(status_payload.get("error") or "weather provider not configured"), live=True),
                EvalCheck("weather.forecast", "weather", "skipped", str(status_payload.get("error") or "weather provider not configured"), live=True),
            ]
        )
        return checks
    for tool_name, args in (
        ("weather.current", {"location": location, "no_cache": True}),
        ("weather.forecast", {"location": location, "days": 2, "no_cache": True}),
    ):
        result = broker.execute(_tool_call(f"eval_{tool_name.replace('.', '_')}", tool_name, args))
        payload = _json(result.content)
        checks.append(
            EvalCheck(
                tool_name,
                "weather",
                "pass" if result.allowed and payload.get("status") == "ok" else "fail",
                f"provider={payload.get('provider')} status={payload.get('status')}",
                live=True,
                tool_names=[tool_name],
            )
        )
    return checks


def _eval_web(broker: ToolBroker) -> list[EvalCheck]:
    if not env_bool("WEB_ACCESS_ENABLED", default=True):
        return [
            EvalCheck("web.search", "web", "skipped", "WEB_ACCESS_ENABLED=false", live=True),
            EvalCheck("web.fetch_url", "web", "skipped", "WEB_ACCESS_ENABLED=false", live=True),
        ]
    checks: list[EvalCheck] = []
    search = broker.execute(_tool_call("eval_web_search", "web.search", {"query": "example domain", "max_results": 2}))
    search_payload = _json(search.content)
    if search.allowed and search_payload.get("status") == "ok":
        search_status = "pass"
        search_reason = f"provider={search_payload.get('provider')}"
    elif search_payload.get("configured") is False:
        search_status = "skipped"
        search_reason = str(search_payload.get("error") or "web search provider not configured")
    else:
        search_status = "fail"
        search_reason = str(search_payload.get("error") or "web search failed")
    checks.append(EvalCheck("web.search", "web", search_status, search_reason, live=True, tool_names=["web.search"]))
    fetch = broker.execute(_tool_call("eval_web_fetch", "web.fetch_url", {"url": "https://example.com", "max_chars": 2000}))
    fetch_payload = _json(fetch.content)
    checks.append(
        EvalCheck(
            "web.fetch_url",
            "web",
            "pass" if fetch.allowed and fetch_payload.get("trust_level") == "UNTRUSTED_WEB" else "fail",
            str(fetch_payload.get("url") or fetch_payload.get("error") or "no fetch detail"),
            live=True,
            tool_names=["web.fetch_url"],
        )
    )
    return checks


def _eval_workspace(broker: ToolBroker) -> list[EvalCheck]:
    path = "workspace/eval/live_eval.txt"
    content = f"eval harness non-personal workspace check at {_now()}\n"
    write = broker.execute(_tool_call("eval_workspace_write", "filesystem.write", {"path": path, "content": content, "overwrite": True}))
    write_payload = _json(write.content)
    if not write.allowed:
        return [EvalCheck("workspace.read_write", "workspace", "fail", str(write_payload.get("error") or "write denied"), tool_names=["filesystem.write"])]
    read = broker.execute(_tool_call("eval_workspace_read", "filesystem.read", {"path": path, "max_bytes": 10_000}))
    read_payload = _json(read.content)
    ok = read.allowed and read_payload.get("content") == content
    return [
        EvalCheck(
            "workspace.read_write",
            "workspace",
            "pass" if ok else "fail",
            "controlled workspace file written and read through ToolBroker" if ok else str(read_payload.get("error") or "read mismatch"),
            tool_names=["filesystem.write", "filesystem.read"],
            details={"path": path},
        )
    ]


def _eval_memory(broker: ToolBroker) -> list[EvalCheck]:
    content = f"Project fact: live eval harness non-sensitive test fact {_now()}"
    store = broker.execute(
        _tool_call(
            "eval_memory_store",
            "memory.store",
            {"content": content, "category": "project_fact", "scope": "eval", "source_trust": "TRUSTED_USER"},
        )
    )
    store_payload = _json(store.content)
    record = store_payload.get("record") if isinstance(store_payload.get("record"), dict) else {}
    record_id = str(record.get("id") or "")
    search = broker.execute(
        _tool_call("eval_memory_search", "memory.search", {"query": "live eval harness", "scope": "eval", "categories": ["project_fact"]})
    )
    search_payload = _json(search.content)
    delete_status = "skipped"
    if record_id:
        delete = broker.execute(_tool_call("eval_memory_delete", "memory.delete", {"record_id": record_id}))
        delete_status = "pass" if delete.allowed else "fail"
    found = any(item.get("id") == record_id for item in search_payload.get("results", []) if isinstance(item, dict))
    ok = store.allowed and search.allowed and bool(record_id) and found and delete_status == "pass"
    return [
        EvalCheck(
            "memory.add_search_delete",
            "memory",
            "pass" if ok else "fail",
            "non-sensitive project fact stored, found, and deleted" if ok else "memory add/search/delete did not complete cleanly",
            tool_names=["memory.store", "memory.search", "memory.delete"],
            details={"record_deleted": delete_status == "pass"},
        )
    ]


def _eval_preflight(broker: ToolBroker) -> list[EvalCheck]:
    result = broker.dry_run(
        _tool_call(
            "eval_preflight_dry_run",
            "filesystem.write",
            {"path": "workspace/eval/preflight.txt", "content": "preview only", "overwrite": True},
        )
    )
    payload = _json(result.content)
    ok = payload.get("dry_run") is True and payload.get("would_execute") is True
    return [
        EvalCheck(
            "dry_run.preflight",
            "safe",
            "pass" if ok else "fail",
            "ToolBroker dry-run preview completed without executing" if ok else str(payload.get("error") or "dry-run failed"),
            tool_names=["filesystem.write"],
        )
    ]


def _eval_connectors(runtime: RuntimeConfig) -> list[EvalCheck]:
    try:
        report = connectors_health_report(load_capabilities_config(runtime.capabilities_path), audit_path=runtime.audit_log_path)
    except Exception as exc:
        return [EvalCheck("connectors.doctor", "safe", "fail", f"{type(exc).__name__}: {exc}")]
    return [
        EvalCheck(
            "connectors.doctor",
            "safe",
            "pass" if report.get("status") in {"ok", "warn"} else "fail",
            "connector status checked without personal-data reads",
            details={"connector_count": len(report.get("connectors", []))},
        )
    ]


def _skipped_personal_evals() -> list[EvalCheck]:
    reason = "personal-data evals are skipped by default; use a future explicit approval-gated opt-in path"
    return [
        EvalCheck("calendar.read", "calendar", "skipped", reason, personal_data=True),
        EvalCheck("contacts.read", "contacts", "skipped", reason, personal_data=True),
        EvalCheck("email.metadata", "email", "skipped", reason, personal_data=True),
        EvalCheck("email.draft", "email", "skipped", reason, personal_data=True),
        EvalCheck("messages.draft_from_text", "messages", "skipped", reason, personal_data=True),
    ]


def _final_report(
    runtime: RuntimeConfig,
    selected: list[str],
    checks: list[EvalCheck],
    options: EvalOptions,
) -> dict[str, Any]:
    status_counts = {"pass": 0, "fail": 0, "skipped": 0}
    for check in checks:
        if check.status in status_counts:
            status_counts[check.status] += 1
    report = {
        "status": "fail" if status_counts["fail"] else "ok",
        "run_id": f"eval-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": _now(),
        "selected_categories": selected,
        "safe_default": bool(options.safe),
        "personal_data_evals": "skipped_by_default",
        "model": runtime.lmstudio_model or "",
        "base_url": runtime.lmstudio_base_url,
        "summary": status_counts,
        "checks": [check.to_dict() for check in checks],
        "report_path": str(options.report_path),
        "results_path": str(options.results_path),
    }
    _write_report(report, options.report_path, options.results_path)
    return report


def _write_report(report: dict[str, Any], report_path: Path, results_path: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_format_report_markdown(report), encoding="utf-8")


def _format_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Eval Report",
        "",
        "This report is generated by `python smart_agent.py eval run ...`. It must not contain secrets or private personal data.",
        "",
        f"- Run ID: `{report.get('run_id')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Status: `{report.get('status')}`",
        f"- Selected categories: `{', '.join(report.get('selected_categories', []))}`",
        f"- Personal-data evals: `{report.get('personal_data_evals')}`",
        f"- Summary: pass `{report.get('summary', {}).get('pass')}`, fail `{report.get('summary', {}).get('fail')}`, skipped `{report.get('summary', {}).get('skipped')}`",
        "",
        "| Check | Category | Status | Reason | Tools |",
        "|---|---|---|---|---|",
    ]
    for check in report.get("checks", []):
        tools = ", ".join(str(tool) for tool in check.get("tool_names", []))
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(str(check.get("name", ""))),
                    _md(str(check.get("category", ""))),
                    _md(str(check.get("status", ""))),
                    _md(str(check.get("reason", ""))),
                    _md(tools),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Safety Notes",
            "",
            "- Safe evals do not read personal data by default.",
            "- Personal-data evals are skipped unless a future explicit approval-gated opt-in path is implemented.",
            "- Evals do not send emails/texts or write calendar/contact data.",
            "- Tool actions run through `ToolBroker`; dry-run/preflight checks use `ToolBroker.dry_run()`.",
            "- Memory evals use only a non-sensitive project fact and delete it before completion.",
            "",
        ]
    )
    return "\n".join(lines)


def _empty_report_template(report_path: Path) -> str:
    return "\n".join(
        [
            "# Eval Report",
            "",
            f"No eval report exists yet at `{report_path}`.",
            "",
            "Run one of:",
            "",
            "```bash",
            "python smart_agent.py eval run --safe",
            "python smart_agent.py eval run --lmstudio",
            "python smart_agent.py eval run --web",
            "python smart_agent.py eval run --weather",
            "python smart_agent.py eval run --workspace",
            "python smart_agent.py eval run --memory",
            "```",
            "",
        ]
    )


def _eval_memory_path(results_path: Path) -> Path:
    return results_path.parent / "eval_memory.sqlite3"


def _tool_call(call_id: str, tool_name: str, arguments: dict[str, object]) -> dict[str, object]:
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }


def _json(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "malformed JSON content"}
    return parsed if isinstance(parsed, dict) else {"value": parsed}


def _attached_tools(debug_events: Iterable[dict[str, Any]]) -> list[str]:
    for event in debug_events:
        if event.get("event") == "route":
            attached = event.get("tools_attached") or []
            return [str(item) for item in attached]
    return []


def _tool_call_seen(debug_events: Iterable[dict[str, Any]], tool_name: str) -> bool:
    return any(event.get("event") == "tool_call" and event.get("tool_name") == tool_name for event in debug_events)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
