from __future__ import annotations

import json
from agent.core.tool_broker import ToolBroker
from agent.tools.weather.formatter import format_weather_daily_briefing
from agent.tools.weather.preferences import configured_default_location
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep


def daily_briefing(broker: ToolBroker, timezone: str = "UTC") -> WorkflowReport:
    return WorkflowRunner(broker).run(
        "daily_briefing",
        [WorkflowStep("time.get_current_time", {"timezone": timezone})],
    )


def weather_daily_briefing(
    broker: ToolBroker,
    *,
    location: str | None = None,
    use_default_location: bool = False,
) -> dict[str, object]:
    resolved_location = (location or "").strip()
    default_location_used = False
    if not resolved_location and use_default_location:
        default_location = configured_default_location()
        resolved_location = default_location.location if default_location else ""
        default_location_used = bool(resolved_location)
    if not resolved_location:
        return {
            "status": "error",
            "error": "weather location is required; pass --weather \"City, Region\" or set WEATHER_DEFAULT_LOCATION and use --weather-default",
            "default_location_used": False,
            "steps": [],
        }

    report = WorkflowRunner(broker).run(
        "daily_weather_briefing",
        [
            WorkflowStep("weather.current", {"location": resolved_location}),
            WorkflowStep("weather.forecast", {"location": resolved_location, "days": 1}),
        ],
    )
    payload: dict[str, object] = {
        "status": "ok" if report.allowed else "error",
        "location": resolved_location,
        "default_location_used": default_location_used,
        "steps": report.steps,
    }
    if not report.allowed or len(report.steps) < 2:
        payload["error"] = _first_error(report)
        return payload
    current_payload = report.steps[0]["content"]
    forecast_payload = report.steps[1]["content"]
    payload["current"] = current_payload
    payload["forecast"] = forecast_payload
    if current_payload.get("status") != "ok" or forecast_payload.get("status") != "ok":
        payload["status"] = "error"
        payload["error"] = current_payload.get("error") or forecast_payload.get("error") or "weather briefing failed"
        return payload
    payload["briefing"] = format_weather_daily_briefing(current_payload, forecast_payload)
    return payload


def weather_daily_briefing_json(
    broker: ToolBroker,
    *,
    location: str | None = None,
    use_default_location: bool = False,
) -> str:
    return json.dumps(
        weather_daily_briefing(broker, location=location, use_default_location=use_default_location),
        indent=2,
        sort_keys=True,
    )


def _first_error(report: WorkflowReport) -> str:
    for step in report.steps:
        content = step.get("content", {})
        if isinstance(content, dict) and content.get("error"):
            return str(content["error"])
    return "weather briefing failed"
