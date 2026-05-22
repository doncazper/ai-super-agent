from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Protocol

from agent.config.runtime import env_bool, env_value, parse_int
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError


DEFAULT_MAX_RANGE_DAYS = 31


@dataclass(frozen=True)
class CalendarEvent:
    title: str
    start: str
    end: str
    calendar_name: str = ""
    attendee_count: int = 0
    location: str = ""
    notes: str = ""


class CalendarConnector(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    def read_events(
        self,
        *,
        start: datetime,
        end: datetime,
        calendar_filters: list[str],
    ) -> list[CalendarEvent]:
        ...


class NotConfiguredCalendarConnector:
    name = "not_configured"

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason or "calendar connector is not configured"

    def is_configured(self) -> bool:
        return False

    def read_events(
        self,
        *,
        start: datetime,
        end: datetime,
        calendar_filters: list[str],
    ) -> list[CalendarEvent]:
        raise ToolError(calendar_setup_error(self.reason)["error"])


class AppleScriptCalendarConnector:
    """Read Calendar.app events through macOS Automation permissions.

    This does not scrape Calendar databases and does not require Full Disk
    Access. macOS may show an Automation/Calendar privacy prompt when first
    used by the Python host process.
    """

    name = "applescript"

    def is_configured(self) -> bool:
        return sys.platform == "darwin"

    def read_events(
        self,
        *,
        start: datetime,
        end: datetime,
        calendar_filters: list[str],
    ) -> list[CalendarEvent]:
        if not self.is_configured():
            raise ToolError("AppleScript calendar connector is available only on macOS")
        script = _calendar_applescript(start, end, calendar_filters)
        completed = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "Calendar.app access failed"
            raise ToolError(
                "calendar connector failed. Grant macOS Calendar/Automation permission if prompted. "
                f"Detail: {detail[:300]}"
            )
        return [_event_from_line(line) for line in completed.stdout.splitlines() if line.strip()]


def calendar_connector_from_env() -> CalendarConnector:
    provider = env_value("CALENDAR_CONNECTOR", default="").strip().casefold()
    if not provider:
        return NotConfiguredCalendarConnector()
    if provider in {"applescript", "apple_script", "calendar_app"}:
        return AppleScriptCalendarConnector()
    return NotConfiguredCalendarConnector(f"unsupported calendar connector '{provider}'")


def calendar_setup_error(reason: str = "calendar connector is not configured") -> dict[str, object]:
    return {
        "status": "error",
        "configured": False,
        "connector": env_value("CALENDAR_CONNECTOR", default="") or "not_configured",
        "error": reason,
        "setup": [
            "Calendar tools are HIGH risk and disabled by default in config/capabilities.yaml.",
            "Enable only calendar.read_date_range and calendar.find_availability after review.",
            "Set CALENDAR_CONNECTOR=applescript to use Calendar.app through macOS Automation permissions.",
            "Do not grant Full Disk Access; this connector does not need it.",
        ],
    }


def read_date_range(
    connector: CalendarConnector,
    *,
    start: str | None = None,
    end: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    calendar_filters: list[str] | None = None,
) -> dict[str, object]:
    start_dt, end_dt = validate_selected_range(start or start_date, end or end_date)
    filters = _clean_filters(calendar_filters)
    if not connector.is_configured():
        return {
            **calendar_setup_error(),
            "start": _iso(start_dt),
            "end": _iso(end_dt),
            "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
            "stored_in_memory": False,
        }
    events = connector.read_events(start=start_dt, end=end_dt, calendar_filters=filters)
    allow_locations = env_bool("CALENDAR_INCLUDE_LOCATIONS", default=False)
    summaries = [_event_summary(event, allow_locations=allow_locations) for event in events]
    return {
        "status": "ok",
        "configured": True,
        "connector": connector.name,
        "start": _iso(start_dt),
        "end": _iso(end_dt),
        "selected_range_days": round((end_dt - start_dt).total_seconds() / 86400, 4),
        "calendar_filters": filters,
        "event_count": len(summaries),
        "events": summaries,
        "notes_included": False,
        "locations_included": allow_locations,
        "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
        "stored_in_memory": False,
        "_audit": {"commands_run": [_audit_command(connector)]},
    }


def find_availability(
    connector: CalendarConnector,
    *,
    start: str | None = None,
    end: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    duration_minutes: int = 30,
    working_hours_start: str = "09:00",
    working_hours_end: str = "17:00",
    calendar_filters: list[str] | None = None,
) -> dict[str, object]:
    start_dt, end_dt = validate_selected_range(start or start_date, end or end_date)
    duration = _validate_duration(duration_minutes)
    filters = _clean_filters(calendar_filters)
    if not connector.is_configured():
        return {
            **calendar_setup_error(),
            "start": _iso(start_dt),
            "end": _iso(end_dt),
            "duration_minutes": duration,
            "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
            "stored_in_memory": False,
        }
    work_start = _parse_hhmm(working_hours_start, "working_hours_start")
    work_end = _parse_hhmm(working_hours_end, "working_hours_end")
    if work_end <= work_start:
        raise ToolError("working_hours_end must be after working_hours_start")
    events = connector.read_events(start=start_dt, end=end_dt, calendar_filters=filters)
    slots = _availability_slots(
        start_dt,
        end_dt,
        events,
        duration=timedelta(minutes=duration),
        work_start=work_start,
        work_end=work_end,
    )
    return {
        "status": "ok",
        "configured": True,
        "connector": connector.name,
        "start": _iso(start_dt),
        "end": _iso(end_dt),
        "duration_minutes": duration,
        "working_hours": {"start": working_hours_start, "end": working_hours_end},
        "available_slots": slots,
        "busy_event_count": len(events),
        "event_details_included": False,
        "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
        "stored_in_memory": False,
        "_audit": {"commands_run": [_audit_command(connector)]},
    }


def validate_selected_range(start_value: str | None, end_value: str | None) -> tuple[datetime, datetime]:
    if not start_value or not end_value:
        raise ToolError("start and end are required for selected calendar range")
    start = _parse_datetime(start_value, boundary="start")
    end = _parse_datetime(end_value, boundary="end")
    if end <= start:
        raise ToolError("calendar end must be after start")
    max_days = parse_int(
        "CALENDAR_MAX_RANGE_DAYS",
        env_value("CALENDAR_MAX_RANGE_DAYS", default=str(DEFAULT_MAX_RANGE_DAYS)),
        minimum=1,
        maximum=366,
    )
    if end - start > timedelta(days=max_days):
        raise ToolError(f"calendar date range exceeds maximum selected range of {max_days} days")
    return start, end


def _parse_datetime(value: str, *, boundary: str) -> datetime:
    stripped = value.strip()
    try:
        if len(stripped) == 10 and stripped[4] == "-" and stripped[7] == "-":
            return datetime.fromisoformat(stripped)
        return datetime.fromisoformat(stripped.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ToolError("calendar datetimes must be ISO format, for example 2026-05-22 or 2026-05-22T09:00:00") from exc


def _event_summary(event: CalendarEvent, *, allow_locations: bool) -> dict[str, object]:
    summary: dict[str, object] = {
        "title": event.title,
        "start": event.start,
        "end": event.end,
        "calendar_name": event.calendar_name,
        "attendee_count": max(0, int(event.attendee_count)),
    }
    if event.location:
        summary["location"] = event.location if allow_locations else "[REDACTED]"
    return summary


def _availability_slots(
    start: datetime,
    end: datetime,
    events: list[CalendarEvent],
    *,
    duration: timedelta,
    work_start: time,
    work_end: time,
) -> list[dict[str, str]]:
    busy: list[tuple[datetime, datetime]] = []
    for event in events:
        try:
            busy_start = _parse_datetime(event.start, boundary="start")
            busy_end = _parse_datetime(event.end, boundary="end")
        except ToolError:
            continue
        if busy_end > start and busy_start < end:
            busy.append((max(start, busy_start), min(end, busy_end)))
    busy.sort(key=lambda item: item[0])

    slots: list[dict[str, str]] = []
    day = datetime.combine(start.date(), time.min)
    while day < end and len(slots) < 50:
        window_start = max(start, datetime.combine(day.date(), work_start))
        window_end = min(end, datetime.combine(day.date(), work_end))
        cursor = window_start
        for busy_start, busy_end in busy:
            if busy_end <= cursor or busy_start >= window_end:
                continue
            if busy_start - cursor >= duration:
                slots.append({"start": _iso(cursor), "end": _iso(busy_start)})
            cursor = max(cursor, busy_end)
        if window_end - cursor >= duration:
            slots.append({"start": _iso(cursor), "end": _iso(window_end)})
        day = day + timedelta(days=1)
    return slots[:50]


def _validate_duration(duration_minutes: int) -> int:
    try:
        parsed = int(duration_minutes)
    except (TypeError, ValueError) as exc:
        raise ToolError("duration_minutes must be an integer") from exc
    if parsed < 5 or parsed > 480:
        raise ToolError("duration_minutes must be between 5 and 480")
    return parsed


def _parse_hhmm(value: str, field: str) -> time:
    try:
        hour, minute = value.split(":", 1)
        return time(int(hour), int(minute))
    except (ValueError, TypeError) as exc:
        raise ToolError(f"{field} must be HH:MM") from exc


def _clean_filters(calendar_filters: list[str] | None) -> list[str]:
    return [item.strip() for item in calendar_filters or [] if item and item.strip()]


def _iso(value: datetime) -> str:
    return value.isoformat(timespec="seconds")


def _audit_command(connector: CalendarConnector) -> str:
    if connector.name == "applescript":
        return "osascript Calendar.app read-only selected-range query"
    return f"calendar connector {connector.name} read-only selected-range query"


def _event_from_line(line: str) -> CalendarEvent:
    parts = (line.split("\t") + [""] * 6)[:6]
    attendee_count = 0
    try:
        attendee_count = int(parts[4] or "0")
    except ValueError:
        attendee_count = 0
    return CalendarEvent(
        calendar_name=parts[0],
        start=parts[1],
        end=parts[2],
        title=parts[3],
        attendee_count=attendee_count,
        location=parts[5],
    )


def _calendar_applescript(start: datetime, end: datetime, calendar_filters: list[str]) -> str:
    filter_items = ", ".join(_applescript_quote(item) for item in calendar_filters)
    return f"""
set startDate to my makeDate({start.year}, {start.month}, {start.day}, {start.hour}, {start.minute}, {start.second})
set endDate to my makeDate({end.year}, {end.month}, {end.day}, {end.hour}, {end.minute}, {end.second})
set allowedCalendars to {{{filter_items}}}
set outputLines to {{}}
tell application "Calendar"
    repeat with cal in calendars
        set calName to name of cal as text
        if (count of allowedCalendars) is 0 or allowedCalendars contains calName then
            set matchingEvents to every event of cal whose start date is greater than or equal to startDate and start date is less than endDate
            repeat with ev in matchingEvents
                set attendeeCount to 0
                try
                    set attendeeCount to count of attendees of ev
                end try
                set eventLocation to ""
                try
                    set eventLocation to location of ev as text
                end try
                set end of outputLines to calName & tab & my isoLike(start date of ev) & tab & my isoLike(end date of ev) & tab & my cleanText(summary of ev as text) & tab & attendeeCount & tab & my cleanText(eventLocation)
            end repeat
        end if
    end repeat
end tell
set AppleScript's text item delimiters to linefeed
return outputLines as text

on makeDate(y, m, d, h, min, s)
    set newDate to current date
    set year of newDate to y
    set month of newDate to m
    set day of newDate to d
    set hours of newDate to h
    set minutes of newDate to min
    set seconds of newDate to s
    return newDate
end makeDate

on two(n)
    if n < 10 then return "0" & n
    return n as text
end two

on isoLike(d)
    return (year of d as text) & "-" & my two(month of d as integer) & "-" & my two(day of d as integer) & "T" & my two(hours of d) & ":" & my two(minutes of d) & ":" & my two(seconds of d)
end isoLike

on cleanText(t)
    set AppleScript's text item delimiters to tab
    set itemsList to text items of t
    set AppleScript's text item delimiters to " "
    set t to itemsList as text
    set AppleScript's text item delimiters to linefeed
    set itemsList to text items of t
    set AppleScript's text item delimiters to " "
    return itemsList as text
end cleanText
"""


def _applescript_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
