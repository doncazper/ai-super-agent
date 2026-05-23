from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from agent.config.runtime import RuntimeConfig
from agent.core.messages import MINIMAL_SYSTEM_PROMPT
from agent.core.router import Router
from agent.safety.policy import PolicyEngine
from agent.safety.redaction import SecretRedactor
from agent.tools.web.untrusted_content import UntrustedContentManager
from agent.config.loader import load_capabilities_config


CASES_PATH = Path("eval_cases/model_router_prompt_quality.json")
REPORT_PATH = Path("docs/PROMPT_QUALITY_REPORT.md")
RESULTS_PATH = Path("logs/model_router_prompt_quality.json")
REPORTS_DIR = Path("reports/evals")


@dataclass(frozen=True)
class QualityCase:
    case_id: str
    title: str
    benchmark_category: str
    input: str = ""
    expect: dict[str, Any] = field(default_factory=dict)
    prompt_text: str = ""
    live: bool = False
    personal_data: bool = False

    @classmethod
    def from_dict(cls, item: dict[str, Any]) -> "QualityCase":
        return cls(
            case_id=str(item["id"]),
            title=str(item["title"]),
            benchmark_category=str(item["benchmark_category"]),
            input=str(item.get("input", "")),
            expect=dict(item.get("expect") or {}),
            prompt_text=str(item.get("prompt_text", "")),
            live=bool(item.get("live", False)),
            personal_data=bool(item.get("personal_data", False)),
        )


def list_models(*, live: bool = False, runtime: RuntimeConfig | None = None) -> dict[str, Any]:
    config = runtime or RuntimeConfig.from_env()
    result: dict[str, Any] = {
        "status": "ok",
        "base_url": config.lmstudio_base_url,
        "configured_model": config.lmstudio_model or "",
        "live_requested": live,
        "prompt_sent": False,
        "models": [],
        "notes": [],
    }
    if config.lmstudio_model:
        result["models"].append({"id": config.lmstudio_model, "source": "LMSTUDIO_MODEL"})
    else:
        result["notes"].append("LMSTUDIO_MODEL is not set.")
    if not live:
        result["notes"].append("Live /v1/models lookup skipped; pass --live to query LM Studio without sending prompts.")
        return result
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{config.lmstudio_base_url}/models")
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        result["status"] = "warn"
        result["live_error"] = f"{type(exc).__name__}: {exc}"
        return result
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list):
        result["status"] = "warn"
        result["live_error"] = "LM Studio returned a malformed /v1/models response."
        return result
    result["models"] = [
        {"id": str(item.get("id", "")), "source": "lmstudio"} for item in data if isinstance(item, dict) and item.get("id")
    ]
    return result


def run_model_benchmark(
    *,
    safe: bool = False,
    live: bool = False,
    runtime: RuntimeConfig | None = None,
    cases_path: Path = CASES_PATH,
    report_path: Path = REPORT_PATH,
    results_path: Path = RESULTS_PATH,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Any]:
    if not safe:
        report = _base_report(runtime or RuntimeConfig.from_env(), "model_benchmark", [])
        report["status"] = "fail"
        report["checks"] = [
            _check(
                "benchmark.selection",
                "setup",
                "fail",
                "models benchmark requires --safe in v1",
            )
        ]
        _finish(report, report_path, results_path, reports_dir)
        return report
    cases = load_quality_cases(cases_path)
    checks = []
    checks.extend(_route_checks(cases))
    checks.extend(_policy_checks(cases, runtime=runtime))
    checks.extend(_prompt_checks(cases))
    checks.extend(_live_model_checks(cases, live=live, runtime=runtime))
    report = _base_report(runtime or RuntimeConfig.from_env(), "model_benchmark", checks)
    _finish(report, report_path, results_path, reports_dir)
    return report


def run_router_eval(
    *,
    runtime: RuntimeConfig | None = None,
    cases_path: Path = CASES_PATH,
    report_path: Path = REPORT_PATH,
    results_path: Path = RESULTS_PATH,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Any]:
    checks = _route_checks(load_quality_cases(cases_path))
    report = _base_report(runtime or RuntimeConfig.from_env(), "router_eval", checks)
    _finish(report, report_path, results_path, reports_dir)
    return report


def run_prompt_eval(
    *,
    runtime: RuntimeConfig | None = None,
    cases_path: Path = CASES_PATH,
    report_path: Path = REPORT_PATH,
    results_path: Path = RESULTS_PATH,
    reports_dir: Path = REPORTS_DIR,
) -> dict[str, Any]:
    checks = _prompt_checks(load_quality_cases(cases_path))
    report = _base_report(runtime or RuntimeConfig.from_env(), "prompt_eval", checks)
    _finish(report, report_path, results_path, reports_dir)
    return report


def read_prompt_quality_report(path: Path = REPORT_PATH) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "\n".join(
        [
            "# Model Router and Prompt Quality Report",
            "",
            f"No report exists yet at `{path}`.",
            "",
            "Run one of:",
            "",
            "```bash",
            "python smart_agent.py models benchmark --safe",
            "python smart_agent.py router eval",
            "python smart_agent.py prompts eval",
            "```",
            "",
        ]
    )


def format_quality_json(report: dict[str, Any]) -> str:
    return json.dumps(SecretRedactor().redact(report), indent=2, sort_keys=True)


def format_quality_summary(report: dict[str, Any]) -> str:
    lines = [
        f"Run: {report.get('run_id')}",
        f"Status: {report.get('status')} | suite: {report.get('suite')}",
        f"Summary: pass={report.get('summary', {}).get('pass')} fail={report.get('summary', {}).get('fail')} skipped={report.get('summary', {}).get('skipped')}",
        f"Quality score: {report.get('quality_score')}",
    ]
    for check in report.get("checks", []):
        lines.append(f"[{check.get('status')}] {check.get('name')}: {check.get('reason')}")
    lines.append(f"Report: {report.get('report_path')}")
    return "\n".join(lines)


def load_quality_cases(path: Path = CASES_PATH) -> list[QualityCase]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError(f"{path} must contain a cases list")
    seen: set[str] = set()
    cases: list[QualityCase] = []
    for item in raw_cases:
        if not isinstance(item, dict):
            raise ValueError(f"{path} contains a non-object case")
        case = QualityCase.from_dict(item)
        if case.case_id in seen:
            raise ValueError(f"duplicate quality case id: {case.case_id}")
        seen.add(case.case_id)
        cases.append(case)
    return cases


def _route_checks(cases: list[QualityCase]) -> list[dict[str, Any]]:
    router = Router()
    checks: list[dict[str, Any]] = []
    for case in cases:
        if "route_name" not in case.expect and "use_tools" not in case.expect:
            continue
        force_no_tools = bool(case.expect.get("force_no_tools", False))
        decision = router.route(case.input, force_no_tools=force_no_tools)
        expected_tools = set(str(tool) for tool in case.expect.get("tool_names", []))
        actual_tools = set(decision.tool_names)
        exact_tools = bool(case.expect.get("exact_tools", True))
        tools_ok = actual_tools == expected_tools if exact_tools else expected_tools.issubset(actual_tools)
        route_ok = case.expect.get("route_name") in {None, decision.name}
        use_tools_ok = case.expect.get("use_tools") in {None, decision.use_tools}
        no_tool_ok = not (case.expect.get("no_tools_attached") and decision.use_tools)
        status = "pass" if route_ok and use_tools_ok and tools_ok and no_tool_ok else "fail"
        checks.append(
            _check(
                case.case_id,
                case.benchmark_category,
                status,
                case.title if status == "pass" else "router expectation mismatch",
                input=case.input,
                expected_route=case.expect.get("route_name"),
                actual_route=decision.name,
                expected_use_tools=case.expect.get("use_tools"),
                actual_use_tools=decision.use_tools,
                expected_tools=sorted(expected_tools),
                actual_tools=sorted(actual_tools),
                metadata=decision.metadata,
            )
        )
    return checks


def _policy_checks(cases: list[QualityCase], *, runtime: RuntimeConfig | None) -> list[dict[str, Any]]:
    config = runtime or RuntimeConfig.from_env()
    policy = PolicyEngine.from_config(load_capabilities_config(config.capabilities_path))
    checks: list[dict[str, Any]] = []
    for case in cases:
        capability = case.expect.get("policy_capability")
        if not capability:
            continue
        expected_decision = str(case.expect.get("policy_decision", ""))
        result = policy.evaluate(str(capability))
        actual_decision = result.decision.value
        status = "pass" if actual_decision == expected_decision else "fail"
        checks.append(
            _check(
                f"{case.case_id}.policy",
                case.benchmark_category,
                status,
                case.title if status == "pass" else f"expected policy {expected_decision}, got {actual_decision}",
                capability=str(capability),
                expected_policy_decision=expected_decision,
                actual_policy_decision=actual_decision,
                risk_level=result.capability.risk_level.value if result.capability else "FORBIDDEN",
                approval_reuse_allowed=result.capability.approval_reuse_allowed if result.capability else None,
            )
        )
    return checks


def _prompt_checks(cases: list[QualityCase]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    manager = UntrustedContentManager(max_chars=4000)
    for case in cases:
        prompt_expect = case.expect.get("prompt")
        if not isinstance(prompt_expect, dict):
            continue
        target = str(prompt_expect.get("target", "system"))
        text = MINIMAL_SYSTEM_PROMPT if target == "system" else manager.wrap_webpage(case.prompt_text or case.input)
        must_contain = [str(item) for item in prompt_expect.get("must_contain", [])]
        must_not_contain_first_line = [str(item) for item in prompt_expect.get("must_not_contain_first_line", [])]
        first_line = text.splitlines()[0] if text else ""
        ok = all(item in text for item in must_contain) and all(item not in first_line for item in must_not_contain_first_line)
        checks.append(
            _check(
                case.case_id,
                case.benchmark_category,
                "pass" if ok else "fail",
                case.title if ok else "prompt guardrail expectation failed",
                target=target,
                prompt_excerpt=text[:240],
            )
        )
    return checks


def _live_model_checks(cases: list[QualityCase], *, live: bool, runtime: RuntimeConfig | None) -> list[dict[str, Any]]:
    live_cases = [case for case in cases if case.live]
    if not live_cases:
        return []
    config = runtime or RuntimeConfig.from_env()
    checks: list[dict[str, Any]] = []
    for case in live_cases:
        if not live:
            checks.append(
                _check(case.case_id, case.benchmark_category, "skipped", "live LM Studio benchmark skipped; pass --live after setting LMSTUDIO_MODEL")
            )
        elif not config.lmstudio_model:
            checks.append(_check(case.case_id, case.benchmark_category, "skipped", "LMSTUDIO_MODEL is not set"))
        else:
            checks.append(_check(case.case_id, case.benchmark_category, "skipped", "live answer-quality scoring is a smoke placeholder in v1"))
    return checks


def _base_report(runtime: RuntimeConfig, suite: str, checks: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {"pass": 0, "fail": 0, "skipped": 0}
    for check in checks:
        if check["status"] in summary:
            summary[check["status"]] += 1
    scored = summary["pass"] + summary["fail"]
    quality_score = round((summary["pass"] / scored) * 100, 1) if scored else 0.0
    return {
        "status": "fail" if summary["fail"] else "ok",
        "suite": suite,
        "run_id": f"model-quality-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at": datetime.now(UTC).isoformat(),
        "model": runtime.lmstudio_model or "",
        "base_url": runtime.lmstudio_base_url,
        "prompt_sent": False,
        "personal_data_accessed": False,
        "summary": summary,
        "quality_score": quality_score,
        "checks": checks,
    }


def _finish(report: dict[str, Any], report_path: Path, results_path: Path, reports_dir: Path) -> None:
    report["report_path"] = str(report_path)
    report["results_path"] = str(results_path)
    redacted = SecretRedactor().redact(report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(redacted, indent=2, sort_keys=True) + "\n"
    results_path.write_text(payload, encoding="utf-8")
    reports_dir.joinpath(f"{report['run_id']}.json").write_text(payload, encoding="utf-8")
    report_path.write_text(_markdown(redacted), encoding="utf-8")


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Model Router and Prompt Quality Report",
        "",
        "This report is generated by model/router/prompt-quality eval commands. It must not contain secrets or private personal data.",
        "",
        f"- Run ID: `{report.get('run_id')}`",
        f"- Generated at: `{report.get('generated_at')}`",
        f"- Suite: `{report.get('suite')}`",
        f"- Status: `{report.get('status')}`",
        f"- Prompt sent: `{report.get('prompt_sent')}`",
        f"- Personal data accessed: `{report.get('personal_data_accessed')}`",
        f"- Quality score: `{report.get('quality_score')}`",
        f"- Summary: pass `{report.get('summary', {}).get('pass')}`, fail `{report.get('summary', {}).get('fail')}`, skipped `{report.get('summary', {}).get('skipped')}`",
        "",
        "## Checks",
        "",
        "| Check | Category | Status | Reason | Expected route | Actual route | Expected policy | Actual policy | Tools |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for check in report.get("checks", []):
        tools = ", ".join(str(tool) for tool in check.get("actual_tools", []))
        lines.append(
            "| "
            + " | ".join(
                _md(str(value))
                for value in (
                    check.get("name", ""),
                    check.get("category", ""),
                    check.get("status", ""),
                    check.get("reason", ""),
                    check.get("expected_route", ""),
                    check.get("actual_route", ""),
                    check.get("expected_policy_decision", ""),
                    check.get("actual_policy_decision", ""),
                    tools,
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Safety Notes",
            "",
            "- Default benchmark and prompt evals do not send prompts to LM Studio.",
            "- Live answer-quality checks are opt-in and skipped unless explicitly requested.",
            "- Personal-data requests are measured as routing/policy cases only; no personal connectors are read.",
            "- Prompt-injection fixture text is treated as untrusted data.",
            "",
        ]
    )
    return "\n".join(lines)


def _check(name: str, category: str, status: str, reason: str, **details: Any) -> dict[str, Any]:
    return {"name": name, "category": category, "status": status, "reason": reason, **details}


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
