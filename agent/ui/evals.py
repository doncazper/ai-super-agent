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
from agent.core.router import RouteDecision, Router
from agent.core.tool_broker import ToolBroker
from agent.safety.audit import AuditLogger
from agent.safety.approvals import ApprovalManager
from agent.safety.policy import PolicyEngine, RiskLevel
from agent.tools.registry import ToolRegistry, default_registry
from agent.tools.web.untrusted_content import UntrustedContentManager
from agent.prompts.evidence import audit_prompt_evidence


REPORT_PATH = Path("docs/EVAL_REPORT.md")
RESULTS_PATH = Path("logs/eval_results.json")
REPORTS_DIR = Path("reports/evals")
EVAL_CASES_PATH = Path("eval_cases")
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
class EvalCase:
    case_id: str
    category: str
    title: str
    input: str = ""
    expect: dict[str, Any] = field(default_factory=dict)
    risk_level: str = "SAFE"
    personal_data: bool = False
    live: bool = False
    tags: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, item: dict[str, Any], *, fallback_category: str) -> "EvalCase":
        return cls(
            case_id=str(item["id"]),
            category=str(item.get("category") or fallback_category),
            title=str(item["title"]),
            input=str(item.get("input", "")),
            expect=dict(item.get("expect") or {}),
            risk_level=str(item.get("risk_level") or "SAFE"),
            personal_data=bool(item.get("personal_data", False)),
            live=bool(item.get("live", False)),
            tags=[str(tag) for tag in item.get("tags", [])],
        )


@dataclass(frozen=True)
class EvalOptions:
    safe: bool = False
    lmstudio: bool = False
    lmstudio_live: bool = False
    routing: bool = False
    policy: bool = False
    tools: bool = False
    workflows: bool = False
    prompt_injection: bool = False
    internet: bool = False
    forums: bool = False
    native_skills: bool = False
    web: bool = False
    weather: bool = False
    workspace: bool = False
    memory: bool = False
    prompt_tracker: bool = False
    report_path: Path = REPORT_PATH
    results_path: Path = RESULTS_PATH
    reports_dir: Path = REPORTS_DIR
    cases_path: Path = EVAL_CASES_PATH
    weather_location: str = DEFAULT_WEATHER_LOCATION


EVAL_DEFINITIONS: tuple[EvalDefinition, ...] = (
    EvalDefinition("routing.intent_cases", "routing", "Data-driven deterministic router intent classification.", default_safe=True),
    EvalDefinition("policy.decision_cases", "policy", "Data-driven policy allow/ask/deny regression checks.", default_safe=True),
    EvalDefinition("toolbroker.safe_and_denied", "tools", "ToolBroker allow/deny behavior for safe and unknown tools.", default_safe=True),
    EvalDefinition("audit.tool_execution", "tools", "Tool executions produce audit evidence.", default_safe=True),
    EvalDefinition("prompt_injection.untrusted_wrappers", "prompt_injection", "Untrusted content wrappers keep hostile text as data.", default_safe=True),
    EvalDefinition("internet.source_grounding", "internet", "Fixture-backed internet source grounding, provider policy, and audit checks.", default_safe=True),
    EvalDefinition("forums.source_grounding", "forums", "Fixture-backed forum source grounding, translation labels, retention, no-bypass, and audit checks.", default_safe=True),
    EvalDefinition("native_skills.harness", "native_skills", "Fixture-backed native skill harness and dogfood safety checks.", default_safe=True),
    EvalDefinition("workflows.dry_run_cases", "workflows", "Workflow dry-run checks do not execute risky actions.", default_safe=True),
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
    EvalDefinition("prompt_tracker.queue_integrity", "prompt_tracker", "Prompt queue, evidence, and recovery metadata checks.", default_safe=True),
    EvalDefinition("calendar.read", "calendar", "Selected-scope calendar read.", personal_data=True),
    EvalDefinition("contacts.read", "contacts", "Selected-scope contact read.", personal_data=True),
    EvalDefinition("email.metadata", "email", "Email metadata read.", personal_data=True),
    EvalDefinition("email.draft", "email", "Selected-thread email draft-only flow.", personal_data=True),
    EvalDefinition("messages.draft_from_text", "messages", "Messages draft-only fallback.", personal_data=True),
)


def list_evals() -> dict[str, object]:
    cases = load_eval_cases()
    return {
        "status": "ok",
        "personal_data_default": "skipped",
        "live_default": "opt_in",
        "case_files_path": str(EVAL_CASES_PATH),
        "case_count": len(cases),
        "evals": [definition.to_dict() for definition in EVAL_DEFINITIONS],
        "cases": [case.__dict__ for case in cases],
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
    cases = load_eval_cases(options.cases_path)
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

    if "routing" in selected:
        checks.extend(_eval_routing_cases(cases))
    if "policy" in selected:
        checks.extend(_eval_policy_cases(cases, policy_engine))
    if "tools" in selected:
        checks.extend(_eval_toolbroker_cases(cases, broker))
    if "prompt_injection" in selected:
        checks.extend(_eval_prompt_injection_cases(cases))
    if "internet" in selected:
        checks.extend(_eval_internet_cases(cases))
    if "forums" in selected:
        checks.extend(_eval_forum_cases(cases))
    if "native_skills" in selected:
        checks.extend(_eval_native_skill_cases(cases))
    if "workflows" in selected:
        checks.extend(_eval_workflow_cases(cases, broker))
    if "lmstudio" in selected:
        checks.extend(_eval_lmstudio(config, active_registry, broker, client_factory))
    if "safe" in selected and "tools" not in selected:
        checks.extend(_eval_time_tool(broker))
    if "weather" in selected:
        checks.extend(_eval_weather(broker, options.weather_location))
    if "web" in selected:
        checks.extend(_eval_web(broker))
    if "workspace" in selected:
        checks.extend(_eval_workspace(broker))
    if "memory" in selected:
        checks.extend(_eval_memory(broker))
    if "prompt_tracker" in selected:
        checks.extend(_eval_prompt_tracker())
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
        selected.extend(["routing", "policy", "tools", "prompt_injection", "internet", "forums", "native_skills", "workflows", "lmstudio", "weather", "web", "workspace", "memory", "safe"])
    for enabled, category in (
        (options.lmstudio or options.lmstudio_live, "lmstudio"),
        (options.routing, "routing"),
        (options.policy, "policy"),
        (options.tools, "tools"),
        (options.workflows, "workflows"),
        (options.prompt_injection, "prompt_injection"),
        (options.internet, "internet"),
        (options.forums, "forums"),
        (options.native_skills, "native_skills"),
        (options.weather, "weather"),
        (options.web, "web"),
        (options.workspace, "workspace"),
        (options.memory, "memory"),
        (options.prompt_tracker, "prompt_tracker"),
    ):
        if enabled and category not in selected:
            selected.append(category)
    return selected


def load_eval_cases(cases_path: str | Path = EVAL_CASES_PATH) -> list[EvalCase]:
    root = Path(cases_path)
    if not root.exists():
        return []
    cases: list[EvalCase] = []
    seen: set[str] = set()
    for path in sorted(root.rglob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        category = str(payload.get("category") or path.stem)
        raw_cases = payload.get("cases")
        if not isinstance(raw_cases, list):
            raise ValueError(f"{path} must contain a cases list")
        for item in raw_cases:
            if not isinstance(item, dict):
                raise ValueError(f"{path} contains a non-object eval case")
            case = EvalCase.from_dict(item, fallback_category=category)
            if case.case_id in seen:
                raise ValueError(f"duplicate eval case id: {case.case_id}")
            if case.risk_level not in {level.value for level in RiskLevel}:
                raise ValueError(f"invalid risk level for {case.case_id}: {case.risk_level}")
            seen.add(case.case_id)
            cases.append(case)
    return cases


def _cases(cases: Iterable[EvalCase], category: str) -> list[EvalCase]:
    return [case for case in cases if case.category == category]


def _eval_routing_cases(cases: Iterable[EvalCase]) -> list[EvalCheck]:
    router = Router()
    checks: list[EvalCheck] = []
    for case in _cases(cases, "routing"):
        decision = router.route(case.input, force_no_tools=bool(case.expect.get("force_no_tools", False)))
        expected_tools = set(str(tool) for tool in case.expect.get("tool_names", []))
        actual_tools = set(decision.tool_names)
        expected_use_tools = bool(case.expect.get("use_tools"))
        expected_route = case.expect.get("route_name")
        route_ok = expected_route in {None, decision.name}
        tools_ok = expected_tools.issubset(actual_tools) if expected_tools else True
        use_tools_ok = decision.use_tools is expected_use_tools
        ok = route_ok and tools_ok and use_tools_ok
        checks.append(
            EvalCheck(
                case.case_id,
                "routing",
                "pass" if ok else "fail",
                case.title if ok else f"expected route={expected_route} use_tools={expected_use_tools} tools={sorted(expected_tools)}; got route={decision.name} use_tools={decision.use_tools} tools={sorted(actual_tools)}",
                details={
                    "input": case.input,
                    "route": decision.name,
                    "use_tools": decision.use_tools,
                    "tool_names": sorted(actual_tools),
                    "metadata": decision.metadata,
                },
            )
        )
    return checks


def _eval_policy_cases(cases: Iterable[EvalCase], policy_engine: PolicyEngine) -> list[EvalCheck]:
    checks: list[EvalCheck] = []
    for case in _cases(cases, "policy"):
        capability = str(case.expect.get("capability", ""))
        expected_decision = str(case.expect.get("decision", ""))
        expected_risk = case.expect.get("risk_level")
        result = policy_engine.evaluate(capability)
        actual_decision = result.decision.value
        actual_risk = result.capability.risk_level.value if result.capability else "FORBIDDEN"
        reuse_allowed = result.capability.approval_reuse_allowed if result.capability else None
        reuse_ok = True
        if "approval_reuse_allowed" in case.expect:
            reuse_ok = reuse_allowed is bool(case.expect["approval_reuse_allowed"])
        ok = actual_decision == expected_decision and (expected_risk in {None, actual_risk}) and reuse_ok
        checks.append(
            EvalCheck(
                case.case_id,
                "policy",
                "pass" if ok else "fail",
                case.title if ok else f"expected decision={expected_decision} risk={expected_risk}; got decision={actual_decision} risk={actual_risk} reason={result.reason}",
                details={
                    "capability": capability,
                    "decision": actual_decision,
                    "risk_level": actual_risk,
                    "reason": result.reason,
                    "approval_reuse_allowed": reuse_allowed,
                },
            )
        )
    return checks


def _eval_toolbroker_cases(cases: Iterable[EvalCase], broker: ToolBroker) -> list[EvalCheck]:
    checks = _eval_time_tool(broker)
    for case in _cases(cases, "tools"):
        tool_name = str(case.expect.get("tool_name", ""))
        mode = str(case.expect.get("mode", "execute"))
        args = dict(case.expect.get("args") or {})
        result = broker.dry_run(_tool_call(case.case_id, tool_name, args)) if mode == "dry_run" else broker.execute(_tool_call(case.case_id, tool_name, args))
        payload = _json(result.content)
        expected_allowed = bool(case.expect.get("allowed"))
        expected_decision = case.expect.get("policy_decision")
        actual_decision = payload.get("policy_decision") or (result.debug or {}).get("policy_decision")
        decision_ok = expected_decision in {None, actual_decision}
        ok = result.allowed is expected_allowed and decision_ok
        checks.append(
            EvalCheck(
                case.case_id,
                "tools",
                "pass" if ok else "fail",
                case.title if ok else f"expected allowed={expected_allowed} decision={expected_decision}; got allowed={result.allowed} payload={payload}",
                tool_names=[tool_name] if tool_name else [],
                details={"payload": payload, "audit": result.debug or {}},
            )
        )
    return checks


def _eval_prompt_injection_cases(cases: Iterable[EvalCase]) -> list[EvalCheck]:
    checks: list[EvalCheck] = []
    manager = UntrustedContentManager(max_chars=4000)
    for case in _cases(cases, "prompt_injection"):
        wrapped = manager.wrap_webpage(case.input)
        expected_prefix = str(case.expect.get("starts_with", ""))
        forbidden_action = str(case.expect.get("forbidden_action", ""))
        ok = bool(expected_prefix and wrapped.startswith(expected_prefix)) and forbidden_action not in wrapped.splitlines()[0]
        checks.append(
            EvalCheck(
                case.case_id,
                "prompt_injection",
                "pass" if ok else "fail",
                case.title if ok else "untrusted content warning missing or hostile action leaked into warning",
                details={"wrapped_prefix": wrapped[:160], "source_treated_as": "UNTRUSTED_WEB"},
            )
        )
    return checks


def _eval_internet_cases(cases: Iterable[EvalCase]) -> list[EvalCheck]:
    internet_cases = _cases(cases, "internet")
    if not internet_cases:
        return [EvalCheck("internet.cases_present", "internet", "fail", "no internet eval cases found")]

    checks: list[EvalCheck] = []
    paid_providers = {"brave", "serpapi", "newsapi", "mediacloud"}
    for case in internet_cases:
        fixture = dict(case.expect.get("fixture") or {})
        sources = [item for item in fixture.get("sources", []) if isinstance(item, dict)]
        source_ids = {str(item.get("source_id")) for item in sources if item.get("source_id")}
        citations = [str(item) for item in fixture.get("citations", [])]
        failed_sources = [item for item in fixture.get("fetch_failures", []) if isinstance(item, dict)]
        failed_ids = {str(item.get("source_id")) for item in failed_sources if item.get("source_id")}
        provider_decision = dict(fixture.get("provider_decision") or {})
        memory = dict(fixture.get("memory") or {})
        audit = dict(fixture.get("audit") or {})
        answer = str(fixture.get("answer") or "")
        forbidden_phrases = [str(item).lower() for item in fixture.get("forbidden_phrases", [])]

        failures: list[str] = []
        if case.expect.get("source_list_present", True) and not sources:
            failures.append("source list missing")
        if case.expect.get("no_fabricated_citations", True):
            missing = sorted(citation for citation in citations if citation not in source_ids)
            if missing:
                failures.append(f"citations without source records: {missing}")
            cited_failed = sorted(citation for citation in citations if citation in failed_ids)
            if cited_failed:
                failures.append(f"failed sources cited as support: {cited_failed}")
        if case.expect.get("retrieved_at_present", True):
            missing_retrieved = sorted(str(item.get("source_id")) for item in sources if not item.get("retrieved_at"))
            if missing_retrieved:
                failures.append(f"sources missing retrieved_at: {missing_retrieved}")
        if case.expect.get("untrusted_web", True):
            bad_trust = sorted(str(item.get("source_id")) for item in sources if item.get("trust_level") != "UNTRUSTED_WEB")
            if bad_trust:
                failures.append(f"sources not labeled UNTRUSTED_WEB: {bad_trust}")
        if case.expect.get("failed_fetches_reported", False) and not failed_sources:
            failures.append("fetch failures not reported")
        if case.expect.get("prompt_injection_ignored", False):
            leaked = sorted(phrase for phrase in forbidden_phrases if phrase and phrase in answer.lower())
            if leaked:
                failures.append(f"prompt injection phrase leaked into answer: {leaked}")
            if fixture.get("source_text_can_request_tools") is not False:
                failures.append("fixture does not assert source text is data-only")
        if case.expect.get("provider_policy_respected", True):
            if provider_decision.get("cost_mode") != "free_first":
                failures.append("provider policy is not free_first")
            if provider_decision.get("paid_api_used") is not False:
                failures.append("paid API used by default")
        if case.expect.get("paid_provider_not_default", True):
            selected_provider = str(provider_decision.get("selected_provider") or "").lower()
            if selected_provider in paid_providers and provider_decision.get("explicit_provider") is not True:
                failures.append(f"paid provider selected by default: {selected_provider}")
        if case.expect.get("no_query_history_storage", True):
            if memory.get("query_history_persisted") is not False or memory.get("web_content_persisted") is not False:
                failures.append("query history or web content persisted")
        if case.expect.get("network_calls_audited", True):
            if not audit.get("provider_decision_audited"):
                failures.append("provider decision not audited")
            if case.expect.get("fetch_audited", False) and not audit.get("fetch_audited"):
                failures.append("fetch not audited")
            if case.expect.get("network_domains_present", False) and not audit.get("network_domains"):
                failures.append("network domains missing from audit fixture")

        checks.append(
            EvalCheck(
                case.case_id,
                "internet",
                "fail" if failures else "pass",
                "; ".join(failures) if failures else case.title,
                details={
                    "source_count": len(sources),
                    "citation_count": len(citations),
                    "failed_fetch_count": len(failed_sources),
                    "selected_provider": provider_decision.get("selected_provider"),
                    "paid_api_used": provider_decision.get("paid_api_used"),
                    "network_domains": audit.get("network_domains", []),
                },
            )
        )
    return checks


def _eval_forum_cases(cases: Iterable[EvalCase]) -> list[EvalCheck]:
    forum_cases = _cases(cases, "forums")
    if not forum_cases:
        return [EvalCheck("forums.cases_present", "forums", "fail", "no forum eval cases found")]

    checks: list[EvalCheck] = []
    paid_providers = {"brave", "serpapi", "newsapi", "mediacloud"}
    for case in forum_cases:
        fixture = dict(case.expect.get("fixture") or {})
        sources = [item for item in fixture.get("sources", []) if isinstance(item, dict)]
        source_ids = {str(item.get("source_id")) for item in sources if item.get("source_id")}
        citations = [str(item) for item in fixture.get("citations", [])]
        excluded_sources = [item for item in fixture.get("excluded_sources", []) if isinstance(item, dict)]
        excluded_ids = {str(item.get("source_id")) for item in excluded_sources if item.get("source_id")}
        unavailable_sources = [item for item in fixture.get("unavailable_sources", []) if isinstance(item, dict)]
        provider_policy = dict(fixture.get("provider_policy") or {})
        access_policy = dict(fixture.get("access_policy") or {})
        memory = dict(fixture.get("memory") or {})
        audit = dict(fixture.get("audit") or {})
        retention = dict(fixture.get("retention") or {})
        answer = str(fixture.get("answer") or "")
        forbidden_phrases = [str(item).lower() for item in fixture.get("forbidden_phrases", [])]

        failures: list[str] = []
        if case.expect.get("source_list_present", True) and not sources:
            failures.append("source list missing")
        if case.expect.get("no_fabricated_sources", True):
            missing = sorted(citation for citation in citations if citation not in source_ids)
            if missing:
                failures.append(f"citations without source records: {missing}")
            cited_excluded = sorted(citation for citation in citations if citation in excluded_ids)
            if cited_excluded:
                failures.append(f"excluded sources cited as support: {cited_excluded}")
        if case.expect.get("source_ids_preserved", False):
            missing_ids = sorted(str(item.get("title") or item.get("url") or "<unknown>") for item in sources if not item.get("source_id"))
            if missing_ids:
                failures.append(f"sources missing source_id: {missing_ids}")
            missing_links = sorted(str(item.get("source_id")) for item in sources if not (item.get("url") or item.get("permalink")))
            if missing_links:
                failures.append(f"sources missing url/permalink: {missing_links}")
        if case.expect.get("retrieved_at_present", True):
            missing_retrieved = sorted(str(item.get("source_id")) for item in sources if not item.get("retrieved_at"))
            if missing_retrieved:
                failures.append(f"sources missing retrieved_at: {missing_retrieved}")
        bad_trust = sorted(str(item.get("source_id")) for item in sources if item.get("trust_level") != "UNTRUSTED_WEB")
        if bad_trust:
            failures.append(f"sources not labeled UNTRUSTED_WEB: {bad_trust}")
        if case.expect.get("translation_labeled_generated", False):
            missing_labels = sorted(
                str(item.get("source_id"))
                for item in sources
                if item.get("translation") and dict(item.get("translation") or {}).get("label") != "MODEL_GENERATED_TRANSLATION"
            )
            translated_sources = [item for item in sources if item.get("translation")]
            if not translated_sources:
                failures.append("no translated sources present")
            if missing_labels:
                failures.append(f"translations missing generated label: {missing_labels}")
        if case.expect.get("original_snippets_preserved", False):
            missing_snippets = sorted(str(item.get("source_id")) for item in sources if item.get("language") and not item.get("original_snippet"))
            if missing_snippets:
                failures.append(f"translated sources missing original snippet: {missing_snippets}")
        if case.expect.get("prompt_injection_ignored", False):
            leaked = sorted(phrase for phrase in forbidden_phrases if phrase and phrase in answer.lower())
            if leaked:
                failures.append(f"prompt injection phrase leaked into answer: {leaked}")
            if fixture.get("source_text_can_request_tools") is not False:
                failures.append("fixture does not assert forum source text is data-only")
        if case.expect.get("deleted_removed_ignored", False):
            removed = [item for item in excluded_sources if item.get("reason") == "deleted_or_removed"]
            if not removed:
                failures.append("deleted/removed exclusion missing")
        if case.expect.get("no_scraping_bypass", False):
            if access_policy.get("cookies_used") is not False:
                failures.append("cookies used in discovery/fetch fixture")
            if access_policy.get("browser_session_used") is not False:
                failures.append("browser session used in discovery/fetch fixture")
            if access_policy.get("captcha_bypass_attempted") is not False:
                failures.append("CAPTCHA bypass attempted")
            if access_policy.get("platform_scraper_used") is not False:
                failures.append("platform scraper used")
        if case.expect.get("blocked_sources_reported", False) and not unavailable_sources:
            failures.append("blocked/unavailable sources not reported")
        if case.expect.get("no_paid_provider_default", True):
            if provider_policy.get("cost_mode", "free_first") != "free_first":
                failures.append("provider policy is not free_first")
            if provider_policy.get("paid_api_used") is not False:
                failures.append("paid API used by default")
            selected = {str(item).lower() for item in provider_policy.get("selected_providers", [])}
            if selected & paid_providers and provider_policy.get("explicit_paid_provider") is not True:
                failures.append(f"paid provider selected by default: {sorted(selected & paid_providers)}")
        if case.expect.get("no_memory_write", True):
            if memory.get("summary_persisted") is not False or memory.get("query_history_persisted") is not False or memory.get("forum_content_persisted") is not False:
                failures.append("forum summary/query/content persisted")
        if case.expect.get("cache_retention_enforced", False):
            if not retention.get("cache_ttl_seconds"):
                failures.append("cache TTL missing")
            if retention.get("content_hash_present") is not True:
                failures.append("content hash missing")
            if retention.get("author_metadata_default_enabled") is not False:
                failures.append("author metadata enabled by default")
            if retention.get("deleted_removed_content_retained") is not False:
                failures.append("deleted/removed content retained")
            if retention.get("query_history_stored") is not False:
                failures.append("query history stored")
            if retention.get("privacy_report_raw_content_returned") is not False:
                failures.append("privacy report returned raw content")
        if case.expect.get("audit_provider_calls", True):
            if audit.get("provider_calls_audited") is not True:
                failures.append("provider calls not audited")

        checks.append(
            EvalCheck(
                case.case_id,
                "forums",
                "fail" if failures else "pass",
                "; ".join(failures) if failures else case.title,
                details={
                    "source_count": len(sources),
                    "citation_count": len(citations),
                    "excluded_count": len(excluded_sources),
                    "unavailable_count": len(unavailable_sources),
                    "paid_api_used": provider_policy.get("paid_api_used"),
                    "domains": audit.get("domains", []),
                },
            )
        )
    return checks


def _eval_native_skill_cases(cases: Iterable[EvalCase]) -> list[EvalCheck]:
    native_cases = _cases(cases, "native_skills")
    if not native_cases:
        return [EvalCheck("native_skills.cases_present", "native_skills", "fail", "no native skill eval cases found")]

    checks: list[EvalCheck] = []
    for case in native_cases:
        fixture = dict(case.expect.get("fixture") or {})
        failures: list[str] = []
        expectations = {
            "safe_only_default": "safe-only default missing",
            "high_critical_skipped": "high/critical skip missing",
            "personal_data_skipped": "personal-data skip missing",
            "external_scripts_never_run": "external script non-execution missing",
            "prompt_injection_caught": "prompt-injection fixture not caught",
            "secret_fixture_caught": "secret fixture not caught",
            "missing_dependency_reported": "missing dependency not reported",
            "dogfood_suite_present": "dogfood suite missing",
            "command_registry_updated": "command registry update missing",
        }
        for field, message in expectations.items():
            if case.expect.get(field, False) and fixture.get(field) is not True:
                failures.append(message)
        if case.expect.get("no_plugin_runtime_execution", True) and fixture.get("plugin_runtime_executed") is not False:
            failures.append("plugin runtime execution not explicitly false")
        if case.expect.get("no_memory_write", True) and fixture.get("memory_written") is not False:
            failures.append("memory write not explicitly false")
        checks.append(
            EvalCheck(
                case.case_id,
                "native_skills",
                "fail" if failures else "pass",
                "; ".join(failures) if failures else case.title,
                details={
                    "safe_only_default": fixture.get("safe_only_default"),
                    "dogfood_suite_present": fixture.get("dogfood_suite_present"),
                    "command_registry_updated": fixture.get("command_registry_updated"),
                },
            )
        )
    return checks


def _eval_workflow_cases(cases: Iterable[EvalCase], broker: ToolBroker) -> list[EvalCheck]:
    checks: list[EvalCheck] = []
    for case in _cases(cases, "workflows"):
        tool_name = str(case.expect.get("tool_name", "filesystem.write"))
        args = dict(case.expect.get("args") or {"path": "workspace/eval/workflow_dry_run.txt", "content": "dry-run only", "overwrite": True})
        result = broker.dry_run(_tool_call(case.case_id, tool_name, args))
        payload = _json(result.content)
        ok = payload.get("dry_run") is True and payload.get("would_execute") is bool(case.expect.get("would_execute", True))
        checks.append(
            EvalCheck(
                case.case_id,
                "workflows",
                "pass" if ok else "fail",
                case.title if ok else str(payload.get("error") or "workflow dry-run expectation failed"),
                tool_names=[tool_name],
                details={"payload": payload},
            )
        )
    return checks


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


def _eval_prompt_tracker() -> list[EvalCheck]:
    root = Path(".")
    audit = audit_prompt_evidence(root)
    required_docs = [
        root / "docs/PROMPT_QUEUE.md",
        root / "docs/PROMPT_LEDGER.md",
        root / "docs/PROMPT_AUDIT.md",
        root / "docs/prompt_tracker/PROMPT_TRACKER_AUDIT.md",
        root / "docs/prompt_tracker/PROMPT_TRACKER_GAP_MATRIX.md",
    ]
    missing_docs = [path.relative_to(root).as_posix() for path in required_docs if not path.exists()]
    active_count = sum(1 for item in audit.get("evidence", []) if item.get("status") == "active")
    return [
        EvalCheck(
            "prompt_tracker.docs_exist",
            "prompt_tracker",
            "pass" if not missing_docs else "fail",
            "prompt tracker docs exist" if not missing_docs else f"missing docs: {', '.join(missing_docs)}",
        ),
        EvalCheck(
            "prompt_tracker.one_active",
            "prompt_tracker",
            "pass" if active_count <= 1 else "fail",
            f"active prompt count={active_count}",
        ),
        EvalCheck(
            "prompt_tracker.evidence_audit",
            "prompt_tracker",
            "pass" if audit.get("total", 0) > 0 else "fail",
            f"audited {audit.get('total', 0)} prompt records",
            details={"counts": audit.get("counts", {})},
        ),
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
    scorecards = _scorecards(checks)
    total_scored = status_counts["pass"] + status_counts["fail"]
    quality_score = round((status_counts["pass"] / total_scored) * 100, 1) if total_scored else 0.0
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
        "quality_score": quality_score,
        "scorecards": scorecards,
        "checks": [check.to_dict() for check in checks],
        "report_path": str(options.report_path),
        "results_path": str(options.results_path),
    }
    _write_report(report, options.report_path, options.results_path, options.reports_dir)
    return report


def _scorecards(checks: Iterable[EvalCheck]) -> dict[str, dict[str, Any]]:
    by_category: dict[str, dict[str, Any]] = {}
    for check in checks:
        bucket = by_category.setdefault(check.category, {"pass": 0, "fail": 0, "skipped": 0, "score": 0.0})
        if check.status in {"pass", "fail", "skipped"}:
            bucket[check.status] += 1
    for bucket in by_category.values():
        scored = bucket["pass"] + bucket["fail"]
        bucket["score"] = round((bucket["pass"] / scored) * 100, 1) if scored else 0.0
    return dict(sorted(by_category.items()))


def _write_report(report: dict[str, Any], report_path: Path, results_path: Path, reports_dir: Path) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    results_path.write_text(payload, encoding="utf-8")
    (reports_dir / f"{report['run_id']}.json").write_text(payload, encoding="utf-8")
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
        f"- Quality score: `{report.get('quality_score')}`",
        "",
        "## Scorecards",
        "",
        "| Category | Score | Pass | Fail | Skipped |",
        "|---|---:|---:|---:|---:|",
    ]
    for category, scorecard in report.get("scorecards", {}).items():
        lines.append(
            f"| {_md(str(category))} | {scorecard.get('score')} | {scorecard.get('pass')} | {scorecard.get('fail')} | {scorecard.get('skipped')} |"
        )
    lines.extend(
        [
        "",
        "## Checks",
        "",
        "| Check | Category | Status | Reason | Tools |",
        "|---|---|---|---|---|",
        ]
    )
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
            "- Internet evals are fixture-backed unless the explicit live `--web` category is selected.",
            "- Forum evals are fixture-backed and do not call Reddit, V2EX, Chinese forum sites, search providers, or translation providers.",
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
            "python smart_agent.py eval run --routing",
            "python smart_agent.py eval run --policy",
            "python smart_agent.py eval run --tools",
            "python smart_agent.py eval run --workflows",
            "python smart_agent.py eval run --prompt-injection",
            "python smart_agent.py eval run --internet",
            "python smart_agent.py eval run --forums",
            "python smart_agent.py eval run --lmstudio-live",
            "python smart_agent.py eval run --lmstudio",
            "python smart_agent.py eval run --web",
            "python smart_agent.py eval run --weather",
            "python smart_agent.py eval run --workspace",
            "python smart_agent.py eval run --memory",
            "python smart_agent.py eval run --prompt-tracker",
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
