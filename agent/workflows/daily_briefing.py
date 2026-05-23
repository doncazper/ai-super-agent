from __future__ import annotations

import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from agent.core.tool_broker import ToolBroker
from agent.safety.actions import ActionCenter
from agent.workflows.tasks import draft_task_create
from agent.tools.weather.formatter import format_weather_daily_briefing
from agent.tools.weather.preferences import configured_default_location
from agent.workflows.base import WorkflowReport, WorkflowRunner, WorkflowStep
from agent.workflows.research import safe_excerpt


BRIEFING_CONFIG_PATH_ENV = "BRIEFING_CONFIG_PATH"
DEFAULT_BRIEFING_CONFIG_PATH = "data/briefing_config.json"
BRIEFING_SECTIONS = {"weather", "calendar", "tasks", "email", "web", "memory", "suggested_actions"}


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


def daily_briefing_v1(
    broker: ToolBroker,
    *,
    include_weather: bool = False,
    weather_location: str | None = None,
    use_default_weather_location: bool = False,
    include_calendar: bool = False,
    include_email_metadata: bool = False,
    web_topic: str | None = None,
    dry_run: bool = False,
    briefing_date: date | None = None,
) -> dict[str, object]:
    """Build a safety-scoped daily briefing from explicitly selected sources."""
    today = briefing_date or date.today()
    tomorrow = today + timedelta(days=1)
    payload: dict[str, object] = {
        "status": "ok",
        "workflow": "daily_briefing_v1",
        "date": today.isoformat(),
        "dry_run": dry_run or broker.dry_run_mode,
        "memory_written": False,
        "writes_or_sends": False,
        "sections": [],
        "limitations": [],
        "source_policy": (
            "Each enabled section is checked by PolicyEngine and executed through ToolBroker. "
            "Calendar and email metadata are skipped unless approved. No sends, writes, message reads, "
            "email body reads, browser history reads, or memory writes are performed."
        ),
    }
    sections: list[dict[str, Any]] = []
    limitations: list[str] = []

    if include_weather:
        sections.append(
            _weather_section(
                broker,
                location=weather_location,
                use_default_location=use_default_weather_location,
                dry_run=dry_run,
            )
        )

    if include_calendar:
        sections.append(
            _single_tool_section(
                broker,
                name="calendar",
                tool_name="calendar.read_date_range",
                arguments={"start": today.isoformat(), "end": tomorrow.isoformat()},
                dry_run=dry_run,
                ok_summary=lambda content: (
                    f"{content.get('event_count', 0)} calendar events for the selected date range; "
                    "event notes/body omitted."
                ),
            )
        )

    if include_email_metadata:
        sections.append(
            _single_tool_section(
                broker,
                name="email_metadata",
                tool_name="email.list_metadata",
                arguments={"max_results": 5},
                dry_run=dry_run,
                ok_summary=lambda content: (
                    f"{len(content.get('messages', []))} email metadata items returned; email bodies not read."
                ),
            )
        )

    clean_topic = (web_topic or "").strip()
    if clean_topic:
        sections.append(
            _single_tool_section(
                broker,
                name="web_topic",
                tool_name="web.search",
                arguments={"query": clean_topic, "max_results": 3},
                dry_run=dry_run,
                ok_summary=lambda content: _web_topic_summary(content),
                transform_content=_sanitize_web_topic_content,
            )
        )

    sections.append(
        {
            "name": "reminders",
            "status": "skipped",
            "summary": "Reminders are not implemented in Daily Briefing v1.",
            "reason": "reminders connector is not implemented",
            "steps": [],
        }
    )

    if not any((include_weather, include_calendar, include_email_metadata, clean_topic)):
        limitations.append(
            "No briefing sources were selected. Use --weather, --calendar, --email-metadata, or --web-topic."
        )
    limitations.extend(str(section["summary"]) for section in sections if section.get("status") == "skipped")
    payload["sections"] = sections
    payload["limitations"] = limitations
    if payload["dry_run"]:
        payload["status"] = "dry_run"
    elif any(section.get("status") == "ok" for section in sections):
        payload["status"] = "limited" if any(section.get("status") in {"skipped", "error"} for section in sections) else "ok"
    else:
        payload["status"] = "limited"
    payload["briefing"] = format_daily_briefing_v1(payload)
    return payload


def daily_briefing_v2(
    broker: ToolBroker,
    *,
    sections: list[str] | None = None,
    weather_location: str | None = None,
    use_default_weather_location: bool = False,
    web_topics: list[str] | None = None,
    dry_run: bool = False,
    briefing_date: date | None = None,
    action_center: ActionCenter | None = None,
) -> dict[str, object]:
    """Build a configurable briefing where every section is explicit or configured."""
    config = briefing_config_load()
    selected_sections = _normalize_sections(sections if sections is not None else config.get("sections", []))
    configured_topics = [str(topic).strip() for topic in config.get("web_topics", []) if str(topic).strip()]
    requested_topics = [topic.strip() for topic in web_topics or [] if topic.strip()]
    topics = requested_topics or configured_topics
    configured_location = str(config.get("weather_location") or "").strip()
    today = briefing_date or date.today()
    tomorrow = today + timedelta(days=1)
    effective_dry_run = dry_run or broker.dry_run_mode
    payload: dict[str, object] = {
        "status": "ok",
        "workflow": "daily_briefing_v2",
        "date": today.isoformat(),
        "dry_run": effective_dry_run,
        "configured_sections": selected_sections,
        "memory_written": False,
        "writes_or_sends": False,
        "sections": [],
        "suggested_actions": [],
        "limitations": [],
        "source_policy": (
            "Daily Briefing v2 only runs opt-in sections. Personal-data sections require approval. "
            "Email bodies and messages are not read. Suggested actions are queued in Action Center and "
            "never executed by the briefing."
        ),
    }
    built_sections: list[dict[str, Any]] = []
    limitations: list[str] = []

    if not selected_sections:
        limitations.append("No briefing sections are enabled. Use --sections or briefing config set sections=...")

    if "weather" in selected_sections:
        built_sections.append(
            _weather_section(
                broker,
                location=weather_location or configured_location,
                use_default_location=use_default_weather_location,
                dry_run=effective_dry_run,
            )
        )
    if "calendar" in selected_sections:
        built_sections.append(
            _single_tool_section(
                broker,
                name="calendar",
                tool_name="calendar.read_date_range",
                arguments={"start": today.isoformat(), "end": tomorrow.isoformat()},
                dry_run=effective_dry_run,
                ok_summary=lambda content: (
                    f"{content.get('event_count', 0)} calendar events for the selected date range; "
                    "event notes/body omitted."
                ),
            )
        )
    if "tasks" in selected_sections:
        built_sections.append(
            _single_tool_section(
                broker,
                name="tasks",
                tool_name="tasks.list",
                arguments={"max_results": 10},
                dry_run=effective_dry_run,
                ok_summary=lambda content: (
                    f"{content.get('task_count', 0)} selected-scope task/reminder items returned; "
                    "task notes omitted."
                ),
            )
        )
    if "email" in selected_sections:
        built_sections.append(
            _single_tool_section(
                broker,
                name="email_metadata",
                tool_name="email.list_metadata",
                arguments={"max_results": 5},
                dry_run=effective_dry_run,
                ok_summary=lambda content: (
                    f"{len(content.get('messages', []))} email metadata items returned; email bodies not read."
                ),
            )
        )
    if "web" in selected_sections:
        built_sections.append(_web_topics_section(broker, topics=topics, dry_run=effective_dry_run))
    if "memory" in selected_sections:
        built_sections.append(
            _single_tool_section(
                broker,
                name="memory_preferences",
                tool_name="memory.search",
                arguments={
                    "query": "daily briefing preferences",
                    "categories": ["user_preference"],
                    "limit": 5,
                },
                dry_run=effective_dry_run,
                ok_summary=lambda content: (
                    f"{len(content.get('results', []))} non-personal preference memory records found."
                ),
                transform_content=_sanitize_memory_content,
            )
        )
    if "suggested_actions" in selected_sections:
        suggestion_section = _suggested_actions_section(action_center, dry_run=effective_dry_run)
        built_sections.append(suggestion_section)
        if suggestion_section.get("actions"):
            payload["suggested_actions"] = suggestion_section["actions"]

    limitations.extend(str(section["summary"]) for section in built_sections if section.get("status") in {"skipped", "error"})
    payload["sections"] = built_sections
    payload["limitations"] = limitations
    if effective_dry_run:
        payload["status"] = "dry_run"
    elif any(section.get("status") == "ok" for section in built_sections):
        payload["status"] = "limited" if any(section.get("status") in {"skipped", "error"} for section in built_sections) else "ok"
    else:
        payload["status"] = "limited"
    payload["briefing"] = format_daily_briefing_v2(payload)
    return payload


def briefing_config_load(path: str | Path | None = None) -> dict[str, Any]:
    config_path = _briefing_config_path(path)
    default = {
        "sections": [],
        "weather_location": "",
        "web_topics": [],
        "suggested_actions": False,
    }
    if not config_path.exists():
        return default
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default
    if not isinstance(raw, dict):
        return default
    merged = dict(default)
    merged.update(raw)
    merged["sections"] = _normalize_sections(merged.get("sections", []))
    merged["web_topics"] = [str(topic).strip() for topic in merged.get("web_topics", []) if str(topic).strip()]
    merged["suggested_actions"] = bool(merged.get("suggested_actions", False))
    return merged


def briefing_config_set(updates: dict[str, Any], path: str | Path | None = None) -> dict[str, Any]:
    config = briefing_config_load(path)
    for key, value in updates.items():
        if key == "sections":
            config[key] = _normalize_sections(_split_csv(value))
        elif key == "weather_location":
            config[key] = str(value).strip()
        elif key == "web_topics":
            config[key] = [topic.strip() for topic in _split_csv(value) if topic.strip()]
        elif key == "suggested_actions":
            config[key] = _parse_bool(value)
        else:
            raise ValueError(f"unsupported briefing config key: {key}")
    config_path = _briefing_config_path(path)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    return config


def format_daily_briefing_v1(payload: dict[str, object]) -> str:
    lines = [
        f"Daily briefing ({payload.get('date', 'unknown date')})",
        f"Status: {payload.get('status')}",
    ]
    for section in payload.get("sections", []):
        if not isinstance(section, dict):
            continue
        lines.append("")
        lines.append(f"{str(section.get('name', 'section')).replace('_', ' ').title()}: {section.get('status')}")
        summary = section.get("summary")
        if summary:
            lines.append(str(summary))
    limitations = payload.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.append("")
        lines.append("Limitations:")
        lines.extend(f"- {item}" for item in limitations)
    lines.append("")
    lines.append(str(payload.get("source_policy", "")))
    return "\n".join(line for line in lines if line is not None)


def format_daily_briefing_v2(payload: dict[str, object]) -> str:
    lines = [
        f"Daily briefing v2 ({payload.get('date', 'unknown date')})",
        f"Status: {payload.get('status')}",
    ]
    configured = payload.get("configured_sections")
    if isinstance(configured, list) and configured:
        lines.append("Sections: " + ", ".join(str(section) for section in configured))
    for section in payload.get("sections", []):
        if not isinstance(section, dict):
            continue
        lines.append("")
        lines.append(f"{str(section.get('name', 'section')).replace('_', ' ').title()}: {section.get('status')}")
        summary = section.get("summary")
        if summary:
            lines.append(str(summary))
    actions = payload.get("suggested_actions")
    if isinstance(actions, list) and actions:
        lines.append("")
        lines.append("Suggested Actions:")
        for action in actions:
            if isinstance(action, dict):
                lines.append(f"- {action.get('action_id')}: {action.get('summary')}")
    limitations = payload.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.append("")
        lines.append("Skipped / Limitations:")
        lines.extend(f"- {item}" for item in limitations)
    lines.append("")
    lines.append(str(payload.get("source_policy", "")))
    return "\n".join(line for line in lines if line is not None)


def _first_error(report: WorkflowReport) -> str:
    for step in report.steps:
        content = step.get("content", {})
        if isinstance(content, dict) and content.get("error"):
            return str(content["error"])
    return "weather briefing failed"


def _weather_section(
    broker: ToolBroker,
    *,
    location: str | None,
    use_default_location: bool,
    dry_run: bool,
) -> dict[str, Any]:
    resolved_location = (location or "").strip()
    default_location_used = False
    if not resolved_location and use_default_location:
        default_location = configured_default_location()
        resolved_location = default_location.location if default_location else ""
        default_location_used = bool(resolved_location)
    if not resolved_location:
        return {
            "name": "weather",
            "status": "skipped",
            "summary": (
                "Weather skipped because no location was provided and no explicit WEATHER_DEFAULT_LOCATION "
                "is configured."
            ),
            "default_location_used": False,
            "steps": [],
        }
    steps = [
        _execute_step(broker, "briefing_weather_current", "weather.current", {"location": resolved_location}, dry_run=dry_run),
        _execute_step(
            broker,
            "briefing_weather_forecast",
            "weather.forecast",
            {"location": resolved_location, "days": 1},
            dry_run=dry_run,
        ),
        _execute_step(broker, "briefing_weather_alerts", "weather.alerts", {"location": resolved_location}, dry_run=dry_run),
    ]
    if any(_is_dry_run_step(step) for step in steps):
        return {
            "name": "weather",
            "status": "planned",
            "summary": f"Would fetch current weather, forecast, and alerts for {resolved_location}.",
            "location": resolved_location,
            "default_location_used": default_location_used,
            "steps": steps,
        }
    current = steps[0]["content"]
    forecast = dict(steps[1]["content"])
    alerts = steps[2]["content"]
    if alerts.get("status") == "ok" and isinstance(alerts.get("alerts"), list):
        forecast["alerts"] = alerts["alerts"]
    failed = [step for step in steps[:2] if not step["allowed"] or step["content"].get("status") != "ok"]
    if failed:
        reason = failed[0]["content"].get("error") or "weather unavailable"
        return {
            "name": "weather",
            "status": "skipped" if not failed[0]["allowed"] else "error",
            "summary": f"Weather skipped: {reason}",
            "location": resolved_location,
            "default_location_used": default_location_used,
            "steps": steps,
        }
    return {
        "name": "weather",
        "status": "ok",
        "summary": format_weather_daily_briefing(current, forecast),
        "location": resolved_location,
        "default_location_used": default_location_used,
        "steps": steps,
    }


def _single_tool_section(
    broker: ToolBroker,
    *,
    name: str,
    tool_name: str,
    arguments: dict[str, Any],
    dry_run: bool,
    ok_summary: Any,
    transform_content: Any | None = None,
) -> dict[str, Any]:
    step = _execute_step(broker, f"briefing_{name}", tool_name, arguments, dry_run=dry_run)
    content = step["content"]
    if _is_dry_run_step(step):
        return {
            "name": name,
            "status": "planned",
            "summary": _dry_run_summary(content),
            "approval_required": bool(content.get("approval_required")),
            "steps": [step],
        }
    if not step["allowed"]:
        return {
            "name": name,
            "status": "skipped",
            "summary": f"{name.replace('_', ' ').title()} skipped: {content.get('error', 'tool denied')}",
            "approval_required": content.get("decision") == "ask" or content.get("approval_result") not in {None, "not_required"},
            "steps": [step],
        }
    if content.get("status") == "error":
        return {
            "name": name,
            "status": "error",
            "summary": f"{name.replace('_', ' ').title()} unavailable: {content.get('error', 'unknown error')}",
            "steps": [step],
        }
    if transform_content is not None:
        step["content"] = transform_content(content)
        content = step["content"]
    return {
        "name": name,
        "status": "ok",
        "summary": ok_summary(content),
        "steps": [step],
    }


def _execute_step(
    broker: ToolBroker,
    call_id: str,
    tool_name: str,
    arguments: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    tool_call = {
        "id": call_id,
        "type": "function",
        "function": {"name": tool_name, "arguments": json.dumps(arguments)},
    }
    result = broker.dry_run(tool_call) if dry_run else broker.execute(tool_call)
    try:
        content = json.loads(result.content)
    except json.JSONDecodeError:
        content = {"raw": result.content}
    return {
        "tool_name": result.tool_name,
        "tool_call_id": result.tool_call_id,
        "allowed": result.allowed,
        "content": content,
    }


def _is_dry_run_step(step: dict[str, Any]) -> bool:
    content = step.get("content")
    return isinstance(content, dict) and content.get("dry_run") is True


def _dry_run_summary(content: dict[str, Any]) -> str:
    decision = str(content.get("policy_decision", "")).upper()
    if decision == "DENY":
        approval = "blocked by policy"
    else:
        approval = "approval required" if content.get("approval_required") else "no approval required"
    would = "would execute" if content.get("would_execute") else "would not execute"
    return f"Dry-run: {content.get('tool_name', 'tool')} {would}; {approval}."


def _web_topic_summary(content: dict[str, Any]) -> str:
    results = content.get("results")
    if not isinstance(results, list) or not results:
        return "No web topic results returned; no sources fabricated."
    urls = [str(item.get("url")) for item in results[:3] if isinstance(item, dict) and item.get("url")]
    return f"{len(results)} web topic results returned. Sources: " + "; ".join(urls)


def _sanitize_web_topic_content(content: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(content)
    results = []
    for item in content.get("results", []):
        if not isinstance(item, dict):
            continue
        cleaned = dict(item)
        if "snippet" in cleaned:
            cleaned["snippet"] = safe_excerpt(str(cleaned["snippet"]), max_chars=300)
        results.append(cleaned)
    sanitized["results"] = results
    return sanitized


def _web_topics_section(broker: ToolBroker, *, topics: list[str], dry_run: bool) -> dict[str, Any]:
    if not topics:
        return {
            "name": "web",
            "status": "skipped",
            "summary": "Web section skipped because no web topics were configured or requested.",
            "steps": [],
        }
    steps = [
        _execute_step(
            broker,
            f"briefing_web_{index}",
            "web.search",
            {"query": topic, "max_results": 3},
            dry_run=dry_run,
        )
        for index, topic in enumerate(topics, start=1)
    ]
    if any(_is_dry_run_step(step) for step in steps):
        return {
            "name": "web",
            "status": "planned",
            "summary": f"Would search public web sources for {len(topics)} topic(s).",
            "topics": topics,
            "steps": steps,
        }
    ok_steps = [step for step in steps if step["allowed"] and step["content"].get("status") != "error"]
    if not ok_steps:
        first = steps[0]["content"] if steps else {}
        return {
            "name": "web",
            "status": "skipped" if steps and not steps[0]["allowed"] else "error",
            "summary": f"Web section unavailable: {first.get('error', 'no web results available')}",
            "topics": topics,
            "steps": steps,
        }
    sources: list[str] = []
    for step in ok_steps:
        step["content"] = _sanitize_web_topic_content(step["content"])
        for item in step["content"].get("results", [])[:3]:
            if isinstance(item, dict) and item.get("url"):
                sources.append(str(item["url"]))
    return {
        "name": "web",
        "status": "limited" if len(ok_steps) != len(steps) else "ok",
        "summary": f"Web searches completed for {len(ok_steps)}/{len(topics)} topic(s). Sources: " + "; ".join(sources[:5]),
        "topics": topics,
        "steps": steps,
    }


def _sanitize_memory_content(content: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(content)
    results = []
    for item in content.get("results", []):
        if not isinstance(item, dict):
            continue
        cleaned = dict(item)
        cleaned["content"] = safe_excerpt(str(cleaned.get("content", "")), max_chars=220)
        results.append(cleaned)
    sanitized["results"] = results
    return sanitized


def _suggested_actions_section(action_center: ActionCenter | None, *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "name": "suggested_actions",
            "status": "planned",
            "summary": "Would queue suggested follow-up actions in Action Center; no actions created during dry-run.",
            "actions": [],
            "steps": [],
        }
    if action_center is None:
        return {
            "name": "suggested_actions",
            "status": "skipped",
            "summary": "Suggested actions skipped because Action Center is unavailable.",
            "actions": [],
            "steps": [],
        }
    record = draft_task_create(
        action_center,
        title="Review today's briefing and choose any follow-up actions",
        notes="Created by Daily Briefing v2 as a pending suggestion only; it has not been written to a task provider.",
        source_workflow="daily_briefing_v2",
        allow_notes=False,
    )
    return {
        "name": "suggested_actions",
        "status": "ok",
        "summary": "Queued 1 suggested follow-up action in Action Center; no task was created.",
        "actions": [
            {
                "action_id": record.action_id,
                "action_type": record.action_type,
                "status": record.status.value,
                "summary": str(record.preview.get("summary") or record.sanitized_args.get("title")),
            }
        ],
        "steps": [],
    }


def _normalize_sections(raw_sections: Any) -> list[str]:
    sections = _split_csv(raw_sections)
    normalized: list[str] = []
    aliases = {"email_metadata": "email", "web_topic": "web", "preferences": "memory"}
    for section in sections:
        value = aliases.get(section.strip().lower(), section.strip().lower())
        if value in BRIEFING_SECTIONS and value not in normalized:
            normalized.append(value)
    return normalized


def _split_csv(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _briefing_config_path(path: str | Path | None = None) -> Path:
    return Path(path or os.environ.get(BRIEFING_CONFIG_PATH_ENV, DEFAULT_BRIEFING_CONFIG_PATH))
