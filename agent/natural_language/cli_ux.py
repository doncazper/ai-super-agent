from __future__ import annotations

from agent.natural_language.preflight import preflight_request


def render_nl_response(request: str, *, no_tools: bool = False) -> str:
    plan = preflight_request(request, no_tools=no_tools)
    lines = [
        f"Understood intent: {plan.intent}",
        f"Matched command: {plan.command}",
        (
            "Safety: "
            f"risk={plan.risk_level}, approval_required={plan.approval_required}, "
            f"dry_run_required={plan.dry_run_required}, safe_to_execute={plan.safe_to_execute}"
        ),
    ]
    if plan.args:
        lines.append("Extracted args: " + ", ".join(plan.args))
    if plan.provider_requirements:
        lines.append("Provider/setup requirements:")
        lines.extend(f"- {requirement}" for requirement in plan.provider_requirements)
    if plan.missing_requirements:
        lines.append("Missing requirements:")
        lines.extend(f"- {requirement}" for requirement in plan.missing_requirements)
    if plan.intent in {"ambiguous", "unknown"}:
        lines.append('Next: clarify the request or run `python smart_agent.py commands search "<query>"`.')
    elif plan.safe_to_execute:
        lines.append("Next: run the exact command manually if this is what you intended.")
    elif plan.approval_required or plan.dry_run_required:
        lines.append("Next: use preflight/preview and the existing approval path before any execution.")
    else:
        lines.append("Next: resolve setup or clarification requirements before execution.")
    lines.append("No commands have been executed.")
    return "\n".join(lines)
