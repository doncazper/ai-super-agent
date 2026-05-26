from __future__ import annotations

import json

from agent.natural_language.execution_plan import NaturalLanguageExecutionPlan, build_execution_plan


def preflight_request(request: str, *, no_tools: bool = False) -> NaturalLanguageExecutionPlan:
    return build_execution_plan(request, no_tools=no_tools)


def explain_request(request: str, *, no_tools: bool = False) -> dict[str, object]:
    plan = build_execution_plan(request, no_tools=no_tools)
    return {
        "plan_id": plan.plan_id,
        "intent": plan.intent,
        "reason": plan.reason,
        "risk_level": plan.risk_level,
        "approval_required": plan.approval_required,
        "dry_run_required": plan.dry_run_required,
        "safe_to_execute": plan.safe_to_execute,
        "missing_requirements": plan.missing_requirements,
        "notes": plan.notes,
    }


def suggest_request(request: str, *, no_tools: bool = False) -> dict[str, object]:
    plan = build_execution_plan(request, no_tools=no_tools)
    return {
        "plan_id": plan.plan_id,
        "command_id": plan.command_id,
        "command": plan.command,
        "args": plan.args,
        "safe_to_execute": plan.safe_to_execute,
        "approval_required": plan.approval_required,
        "dry_run_required": plan.dry_run_required,
        "missing_requirements": plan.missing_requirements,
    }


def format_plan_json(plan: NaturalLanguageExecutionPlan) -> str:
    return json.dumps(plan.to_dict(), indent=2, sort_keys=True)
