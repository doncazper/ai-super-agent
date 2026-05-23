from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig
from agent.core.router import Router
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.approvals import ApprovalManager
from agent.safety.policy import PolicyDecision, PolicyEngine, RiskLevel
from agent.tools.registry import ToolRegistry, default_registry


@dataclass(frozen=True)
class PreflightOptions:
    request: str
    project_root: str | Path = "."
    audit: bool = True
    no_tools: bool = False


def run_preflight(
    options: PreflightOptions,
    *,
    registry: ToolRegistry | None = None,
    policy_engine: PolicyEngine | None = None,
    audit_logger: AuditLogger | None = None,
    router: Router | None = None,
    runtime_config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    """Evaluate a request's likely tool path without executing tools.

    Preflight is intentionally conservative. Natural-language requests use the
    deterministic router. Exact tool or capability names are also accepted so a
    user can inspect high-risk capabilities before any connector is enabled.
    """

    request = options.request.strip()
    registry = registry or default_registry(project_root=options.project_root)
    runtime_config = runtime_config or RuntimeConfig.from_env()
    policy_engine = policy_engine or PolicyEngine.from_config(
        load_capabilities_config(runtime_config.capabilities_path)
    )
    audit_logger = audit_logger or AuditLogger(runtime_config.audit_log_path)
    router = router or Router()

    route = router.route(request, force_no_tools=options.no_tools)
    tool_names = _resolve_tool_names(request, registry, routed_tool_names=route.tool_names)
    broker = ToolBroker(
        registry,
        policy_engine,
        audit_logger,
        session_id="preflight-session",
        model="preflight",
        route="preflight",
        approval_manager=ApprovalManager(),
        dry_run=True,
    )

    tools: list[dict[str, Any]] = []
    for index, tool_name in enumerate(sorted(tool_names)):
        args, arguments_known = _preflight_args(tool_name, request, route.metadata)
        tool_call = {
            "id": f"preflight_{index}",
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(args),
            },
        }
        result = broker.dry_run(tool_call)
        payload = json.loads(result.content)
        tool = registry.get(tool_name)
        capability = tool.capability if tool else payload.get("capability", "unknown")
        policy = policy_engine.evaluate(capability)
        risk = _risk_from_policy_or_payload(policy, payload)
        tools.append(
            {
                "tool_name": tool_name,
                "capability": capability,
                "risk_level": risk,
                "policy_decision": policy.decision.value,
                "approval_required": _approval_required(policy, risk),
                "approval_type": _approval_type(policy, risk),
                "would_execute": bool(payload.get("would_execute", False)),
                "arguments_known": arguments_known,
                "sanitized_args": payload.get("sanitized_args", {}),
                "preview": payload.get("preview"),
                "error": payload.get("error"),
                "audit": result.debug if options.audit else None,
            }
        )

    return {
        "status": "ok",
        "dry_run": True,
        "request": request,
        "route": {
            "name": route.name,
            "use_tools": route.use_tools,
            "risk_level": route.risk_level.value,
            "metadata": route.metadata,
        },
        "tools": tools,
        "notes": _preflight_notes(route.use_tools, tools),
    }


def format_preflight(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True)


def _resolve_tool_names(
    request: str,
    registry: ToolRegistry,
    *,
    routed_tool_names: set[str],
) -> set[str]:
    normalized = request.strip().casefold()
    tool_names = set(routed_tool_names)
    for spec in registry.specs():
        if normalized in {spec.name.casefold(), spec.capability.casefold()}:
            tool_names.add(spec.name)
    return tool_names


def _preflight_args(tool_name: str, request: str, metadata: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    location = metadata.get("location")
    if tool_name.startswith("weather.") and isinstance(location, str) and location:
        args: dict[str, Any] = {"location": location}
        if tool_name == "weather.forecast":
            args["days"] = 1
        return args, True
    if tool_name == "web.search":
        return {"query": request}, True
    if tool_name == "web.fetch_url" and request.startswith(("http://", "https://")):
        return {"url": request}, True
    return {}, False


def _risk_from_policy_or_payload(policy: Any, payload: dict[str, Any]) -> str:
    if policy.capability is not None:
        return policy.capability.risk_level.value
    raw = payload.get("risk_level")
    if isinstance(raw, str):
        return raw
    return RiskLevel.FORBIDDEN.value


def _approval_required(policy: Any, risk: str) -> bool:
    if policy.decision is PolicyDecision.ASK:
        return True
    if policy.capability is None:
        return False
    return bool(policy.capability.approval_required or risk in {RiskLevel.HIGH.value, RiskLevel.CRITICAL.value})


def _approval_type(policy: Any, risk: str) -> str:
    if risk == RiskLevel.CRITICAL.value:
        return "per_action"
    if _approval_required(policy, risk):
        return "once"
    return "none"


def _preflight_notes(use_tools: bool, tools: list[dict[str, Any]]) -> list[str]:
    if not use_tools and not tools:
        return ["No tools would be attached for this request."]
    notes = ["No tools were executed; this is a policy and preview evaluation only."]
    if any(tool.get("risk_level") == RiskLevel.CRITICAL.value for tool in tools):
        notes.append("Critical actions require exact action details and per-action approval.")
    if any(tool.get("approval_required") for tool in tools):
        notes.append("Approval-required actions are denied in non-interactive mode unless a live approval prompt approves them.")
    return notes
