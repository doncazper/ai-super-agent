from __future__ import annotations

import importlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import httpx

from agent.config.loader import load_capabilities_config
from agent.config.runtime import RuntimeConfig, RuntimeConfigError
from agent.config.schema import validate_capabilities_config
from agent.connectors.registry import default_connector_registry
from agent.core.tool_broker import ToolBroker
from agent.native_skills.registry import NativeSkillRegistry
from agent.safety.audit import AuditLogger
from agent.safety.policy import PolicyEngine
from agent.safety.validation import validate_startup_policy
from agent.tools.registry import default_registry


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def run_doctor(
    *,
    config: RuntimeConfig | None = None,
    get_json: Callable[[str], dict[str, Any]] | None = None,
) -> list[DoctorCheck]:
    checks: list[DoctorCheck] = []
    runtime: RuntimeConfig | None = config

    checks.append(
        DoctorCheck(
            "python_version",
            "ok" if sys.version_info >= (3, 11) else "fail",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        )
    )

    for module_name in ("httpx", "yaml"):
        try:
            importlib.import_module(module_name)
            checks.append(DoctorCheck(f"import_{module_name}", "ok", "available"))
        except ImportError as exc:
            checks.append(DoctorCheck(f"import_{module_name}", "fail", str(exc)))

    if runtime is None:
        try:
            runtime = RuntimeConfig.from_env()
            checks.append(DoctorCheck("config_loaded", "ok", "runtime config loaded"))
        except RuntimeConfigError as exc:
            checks.append(DoctorCheck("config_loaded", "fail", str(exc)))
            return checks
    else:
        checks.append(DoctorCheck("config_loaded", "ok", "runtime config supplied"))

    checks.append(DoctorCheck("lmstudio_base_url", "ok", runtime.lmstudio_base_url))
    checks.append(
        DoctorCheck(
            "lmstudio_model",
            "ok" if runtime.lmstudio_model else "fail",
            runtime.lmstudio_model or "LMSTUDIO_MODEL is not set",
        )
    )

    models_payload: dict[str, Any] | None = None
    fetch_json = get_json or _http_get_json
    try:
        models_payload = fetch_json(f"{runtime.lmstudio_base_url}/models")
        checks.append(DoctorCheck("lmstudio_server", "ok", "server reachable"))
        checks.append(DoctorCheck("lmstudio_models_endpoint", "ok", "/v1/models reachable"))
    except Exception as exc:
        checks.append(
            DoctorCheck(
                "lmstudio_server",
                "fail",
                f"LM Studio server not reachable at {runtime.lmstudio_base_url}: {type(exc).__name__}",
            )
        )
        checks.append(DoctorCheck("lmstudio_models_endpoint", "fail", "not reachable"))

    if models_payload is not None and runtime.lmstudio_model:
        model_ids = [item.get("id") for item in models_payload.get("data", []) if isinstance(item, dict)]
        if runtime.lmstudio_model in model_ids:
            checks.append(DoctorCheck("selected_model_available", "ok", runtime.lmstudio_model))
        else:
            checks.append(
                DoctorCheck(
                    "selected_model_available",
                    "warn",
                    f"model not listed by /v1/models: {runtime.lmstudio_model}",
                )
            )

    try:
        validate_startup_policy(runtime.capabilities_path)
        checks.append(DoctorCheck("startup_policy", "ok", "capabilities config valid"))
    except Exception as exc:
        checks.append(DoctorCheck("startup_policy", "fail", str(exc)))

    config_data: dict[str, Any] | None = None
    try:
        config_data = load_capabilities_config(runtime.capabilities_path)
        validate_capabilities_config(config_data)
        checks.append(DoctorCheck("capability_manifest", "ok", "normalized capability manifest valid"))
    except Exception as exc:
        checks.append(DoctorCheck("capability_manifest", "fail", str(exc)))

    checks.append(_check_audit_path(runtime.audit_log_path))

    tool_registry = None
    try:
        tool_registry = default_registry()
        checks.append(DoctorCheck("tools_registry", "ok", f"{len(tool_registry.schemas())} tools registered"))
    except Exception as exc:
        checks.append(DoctorCheck("tools_registry", "fail", str(exc)))

    try:
        connector_registry = default_connector_registry()
        checks.append(
            DoctorCheck("connector_registry", "ok", ", ".join(connector_registry.names()))
        )
    except Exception as exc:
        checks.append(DoctorCheck("connector_registry", "fail", str(exc)))

    try:
        skill_report = NativeSkillRegistry().validate_all(runtime.capabilities_path)
        checks.append(
            DoctorCheck(
                "native_skill_registry",
                "ok" if skill_report["status"] == "ok" else "fail",
                f"{skill_report['manifest_count']} manifests validated",
            )
        )
    except Exception as exc:
        checks.append(DoctorCheck("native_skill_registry", "fail", str(exc)))

    if tool_registry is not None and config_data is not None:
        try:
            ToolBroker(
                tool_registry,
                PolicyEngine.from_config(config_data),
                AuditLogger(Path(runtime.audit_log_path).parent / ".doctor-broker-audit.jsonl"),
                session_id="doctor",
                model=runtime.lmstudio_model,
                route="doctor",
            )
            checks.append(DoctorCheck("toolbroker_loads", "ok", "ToolBroker initialized without executing tools"))
        except Exception as exc:
            checks.append(DoctorCheck("toolbroker_loads", "fail", str(exc)))

    try:
        config_data = config_data or load_capabilities_config(runtime.capabilities_path)
        enabled_personal = [
            name
            for name, entry in config_data.get("tools", {}).items()
            if entry.get("connector_name") in {"email", "messages", "contacts", "calendar", "browser"}
            and bool(entry.get("default_enabled"))
        ]
        if enabled_personal:
            checks.append(
                DoctorCheck(
                    "personal_tools_disabled",
                    "fail",
                    "enabled personal tools: " + ", ".join(enabled_personal),
                )
            )
        else:
            checks.append(DoctorCheck("personal_tools_disabled", "ok", "all personal tools disabled by default"))
    except Exception as exc:
        checks.append(DoctorCheck("personal_tools_disabled", "fail", str(exc)))

    try:
        config_data = config_data or load_capabilities_config(runtime.capabilities_path)
        enabled_critical = [
            name
            for name, entry in config_data.get("tools", {}).items()
            if entry.get("risk_level") == "CRITICAL" and bool(entry.get("default_enabled"))
        ]
        if enabled_critical:
            checks.append(
                DoctorCheck(
                    "critical_actions_disabled",
                    "fail",
                    "enabled CRITICAL actions: " + ", ".join(enabled_critical),
                )
            )
        else:
            checks.append(DoctorCheck("critical_actions_disabled", "ok", "no CRITICAL actions enabled by default"))
    except Exception as exc:
        checks.append(DoctorCheck("critical_actions_disabled", "fail", str(exc)))

    return checks


def doctor_exit_code(checks: list[DoctorCheck]) -> int:
    return 1 if any(check.status == "fail" for check in checks) else 0


def format_doctor(checks: list[DoctorCheck]) -> str:
    return "\n".join(f"[{check.status}] {check.name}: {check.detail}" for check in checks)


def format_doctor_json(checks: list[DoctorCheck]) -> str:
    return json.dumps([check.to_dict() for check in checks], indent=2, sort_keys=True)


def _http_get_json(url: str) -> dict[str, Any]:
    with httpx.Client(timeout=2.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


def _check_audit_path(path: str) -> DoctorCheck:
    audit_path = Path(path)
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=audit_path.parent, prefix=".audit-check.", delete=True):
            pass
        return DoctorCheck("audit_log_path_writable", "ok", str(audit_path))
    except OSError as exc:
        return DoctorCheck("audit_log_path_writable", "fail", f"{audit_path}: {exc.strerror}")
