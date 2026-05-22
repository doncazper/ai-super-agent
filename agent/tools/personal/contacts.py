from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass, field
from typing import Protocol

from agent.config.runtime import env_bool, env_value, parse_int
from agent.safety.trust import TrustLevel
from agent.tools.errors import ToolError


DEFAULT_MAX_SEARCH_RESULTS = 5


@dataclass(frozen=True)
class ContactRecord:
    selected_scope_token: str
    display_name: str
    organization: str = ""
    job_title: str = ""
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    addresses: list[str] = field(default_factory=list)
    notes: str = ""


class ContactsConnector(Protocol):
    name: str

    def is_configured(self) -> bool:
        ...

    def search(self, *, query: str, max_results: int) -> list[ContactRecord]:
        ...

    def read_selected(self, *, selected_scope_token: str) -> ContactRecord | None:
        ...


class NotConfiguredContactsConnector:
    name = "not_configured"

    def __init__(self, reason: str | None = None) -> None:
        self.reason = reason or "contacts connector is not configured"

    def is_configured(self) -> bool:
        return False

    def search(self, *, query: str, max_results: int) -> list[ContactRecord]:
        raise ToolError(contacts_setup_error(self.reason)["error"])

    def read_selected(self, *, selected_scope_token: str) -> ContactRecord | None:
        raise ToolError(contacts_setup_error(self.reason)["error"])


class AppleScriptContactsConnector:
    """Read Contacts.app records through macOS Automation permissions.

    This does not scrape AddressBook databases and does not require Full Disk
    Access. macOS may show an Automation/Contacts privacy prompt when first
    used by the Python host process.
    """

    name = "applescript"

    def is_configured(self) -> bool:
        return sys.platform == "darwin"

    def search(self, *, query: str, max_results: int) -> list[ContactRecord]:
        script = _contacts_search_applescript(query, max_results)
        return [_contact_from_line(line) for line in _run_contacts_script(script).splitlines() if line.strip()]

    def read_selected(self, *, selected_scope_token: str) -> ContactRecord | None:
        script = _contacts_read_applescript(selected_scope_token)
        lines = [line for line in _run_contacts_script(script).splitlines() if line.strip()]
        if not lines:
            return None
        return _contact_from_line(lines[0])


def contacts_connector_from_env() -> ContactsConnector:
    provider = env_value("CONTACTS_CONNECTOR", default="").strip().casefold()
    if not provider:
        return NotConfiguredContactsConnector()
    if provider in {"applescript", "apple_script", "contacts_app"}:
        return AppleScriptContactsConnector()
    return NotConfiguredContactsConnector(f"unsupported contacts connector '{provider}'")


def contacts_setup_error(reason: str = "contacts connector is not configured") -> dict[str, object]:
    return {
        "status": "error",
        "configured": False,
        "connector": env_value("CONTACTS_CONNECTOR", default="") or "not_configured",
        "error": reason,
        "setup": [
            "Contacts tools are HIGH risk and disabled by default in config/capabilities.yaml.",
            "Enable only contacts.search and contacts.read_selected after review.",
            "Set CONTACTS_CONNECTOR=applescript to use Contacts.app through macOS Automation permissions.",
            "Do not grant Full Disk Access; this connector does not need it.",
        ],
    }


def search_contacts(
    connector: ContactsConnector,
    *,
    query: str,
    max_results: int | None = None,
) -> dict[str, object]:
    normalized_query = query.strip()
    if normalized_query.casefold() in {"*", "all", "export", "everyone", "all contacts"}:
        raise ToolError("contacts.search requires a specific selected-scope query; bulk export is denied")
    if len(normalized_query) < 2:
        raise ToolError("contacts.search query must be at least 2 characters")
    limit = _validate_max_results(max_results)
    if not connector.is_configured():
        return {
            **contacts_setup_error(),
            "query": normalized_query,
            "results": [],
            "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
            "stored_in_memory": False,
        }
    records = connector.search(query=normalized_query, max_results=limit)
    return {
        "status": "ok",
        "configured": True,
        "connector": connector.name,
        "query": normalized_query,
        "result_count": len(records),
        "results": [_contact_search_summary(record) for record in records[:limit]],
        "details_included": False,
        "notes_included": False,
        "stored_in_memory": False,
        "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
        "_audit": {"commands_run": [_audit_command(connector, "search")]},
    }


def read_selected_contact(
    connector: ContactsConnector,
    *,
    selected_scope_token: str | None = None,
    requested_fields: list[str] | None = None,
) -> dict[str, object]:
    token = (selected_scope_token or "").strip()
    if not token:
        raise ToolError("selected_scope_token is required for contacts.read_selected")
    if not connector.is_configured():
        return {
            **contacts_setup_error(),
            "selected_scope_token": token,
            "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
            "stored_in_memory": False,
        }
    record = connector.read_selected(selected_scope_token=token)
    if record is None:
        raise ToolError("selected contact was not found")
    fields = _validate_requested_fields(requested_fields)
    include_emails = env_bool("CONTACTS_INCLUDE_EMAILS", default=False)
    include_phones = env_bool("CONTACTS_INCLUDE_PHONES", default=False)
    include_addresses = env_bool("CONTACTS_INCLUDE_ADDRESSES", default=False)
    return {
        "status": "ok",
        "configured": True,
        "connector": connector.name,
        "contact": _contact_detail(
            record,
            requested_fields=fields,
            include_emails=include_emails,
            include_phones=include_phones,
            include_addresses=include_addresses,
        ),
        "requested_fields": fields,
        "notes_included": False,
        "emails_included": include_emails and "emails" in fields,
        "phones_included": include_phones and "phones" in fields,
        "addresses_included": include_addresses,
        "stored_in_memory": False,
        "trust_level": TrustLevel.LOCAL_PRIVATE_DATA.value,
        "_audit": {"commands_run": [_audit_command(connector, "read_selected")]},
    }


def _validate_max_results(max_results: int | None) -> int:
    default_limit = parse_int(
        "CONTACTS_MAX_SEARCH_RESULTS",
        env_value("CONTACTS_MAX_SEARCH_RESULTS", default=str(DEFAULT_MAX_SEARCH_RESULTS)),
        minimum=1,
        maximum=10,
    )
    if max_results is None:
        return default_limit
    try:
        parsed = int(max_results)
    except (TypeError, ValueError) as exc:
        raise ToolError("max_results must be an integer") from exc
    if parsed < 1 or parsed > 10:
        raise ToolError("max_results must be between 1 and 10")
    return min(parsed, default_limit)


def _validate_requested_fields(requested_fields: list[str] | None) -> list[str]:
    allowed = {
        "display_name",
        "organization",
        "job_title",
        "emails",
        "phones",
        "addresses",
    }
    defaults = ["display_name", "organization", "job_title"]
    if not requested_fields:
        return defaults
    cleaned = []
    for item in requested_fields:
        field_name = item.strip()
        if not field_name:
            continue
        if field_name in {"*", "all", "notes"}:
            raise ToolError("contacts.read_selected requested fields must be explicit and may not include notes or all fields")
        if field_name not in allowed:
            raise ToolError(f"unsupported contacts.read_selected field: {field_name}")
        if field_name not in cleaned:
            cleaned.append(field_name)
    return cleaned or defaults


def _contact_search_summary(record: ContactRecord) -> dict[str, object]:
    return {
        "selected_scope_token": record.selected_scope_token,
        "display_name": record.display_name,
        "organization": record.organization,
        "job_title": record.job_title,
        "email_count": len(record.emails),
        "phone_count": len(record.phones),
        "has_address": bool(record.addresses),
    }


def _contact_detail(
    record: ContactRecord,
    *,
    requested_fields: list[str],
    include_emails: bool,
    include_phones: bool,
    include_addresses: bool,
) -> dict[str, object]:
    detail: dict[str, object] = {"selected_scope_token": record.selected_scope_token}
    if "display_name" in requested_fields:
        detail["display_name"] = record.display_name
    if "organization" in requested_fields:
        detail["organization"] = record.organization
    if "job_title" in requested_fields:
        detail["job_title"] = record.job_title
    if "emails" in requested_fields:
        detail["emails"] = list(record.emails) if include_emails else ["[REDACTED]"] * len(record.emails)
    if "phones" in requested_fields:
        detail["phones"] = list(record.phones) if include_phones else ["[REDACTED]"] * len(record.phones)
    if "addresses" in requested_fields and record.addresses:
        detail["addresses"] = list(record.addresses) if include_addresses else ["[REDACTED]"] * len(record.addresses)
    return detail


def _audit_command(connector: ContactsConnector, action: str) -> str:
    if connector.name == "applescript":
        return f"osascript Contacts.app read-only selected-scope {action}"
    return f"contacts connector {connector.name} read-only selected-scope {action}"


def _run_contacts_script(script: str) -> str:
    if sys.platform != "darwin":
        raise ToolError("AppleScript contacts connector is available only on macOS")
    completed = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "Contacts.app access failed"
        raise ToolError(
            "contacts connector failed. Grant macOS Contacts/Automation permission if prompted. "
            f"Detail: {detail[:300]}"
        )
    return completed.stdout


def _contact_from_line(line: str) -> ContactRecord:
    parts = (line.split("\t") + [""] * 7)[:7]
    return ContactRecord(
        selected_scope_token=parts[0],
        display_name=parts[1],
        organization=parts[2],
        job_title=parts[3],
        emails=_split_values(parts[4]),
        phones=_split_values(parts[5]),
        addresses=_split_values(parts[6]),
    )


def _split_values(value: str) -> list[str]:
    return [item for item in value.split(" | ") if item]


def _contacts_search_applescript(query: str, max_results: int) -> str:
    return f"""
set needle to {_applescript_quote(query)}
set maxResults to {max_results}
set outputLines to {{}}
tell application "Contacts"
    repeat with p in people
        if (count of outputLines) is greater than or equal to maxResults then exit repeat
        set displayName to my cleanText(name of p as text)
        if displayName contains needle then
            set end of outputLines to my contactLine(p)
        end if
    end repeat
end tell
set AppleScript's text item delimiters to linefeed
return outputLines as text
{_CONTACTS_HELPERS}
"""


def _contacts_read_applescript(selected_scope_token: str) -> str:
    return f"""
set selectedId to {_applescript_quote(selected_scope_token)}
set outputLines to {{}}
tell application "Contacts"
    repeat with p in people
        if (id of p as text) is selectedId then
            set end of outputLines to my contactLine(p)
            exit repeat
        end if
    end repeat
end tell
set AppleScript's text item delimiters to linefeed
return outputLines as text
{_CONTACTS_HELPERS}
"""


_CONTACTS_HELPERS = """
on contactLine(p)
    set contactId to id of p as text
    set displayName to my cleanText(name of p as text)
    set orgName to ""
    try
        set orgName to my cleanText(organization of p as text)
    end try
    set jobName to ""
    try
        set jobName to my cleanText(job title of p as text)
    end try
    set emailValues to {}
    try
        repeat with e in emails of p
            set end of emailValues to value of e as text
        end repeat
    end try
    set phoneValues to {}
    try
        repeat with ph in phones of p
            set end of phoneValues to value of ph as text
        end repeat
    end try
    set addressValues to {}
    try
        repeat with a in addresses of p
            set end of addressValues to formatted address of a as text
        end repeat
    end try
    return contactId & tab & displayName & tab & orgName & tab & jobName & tab & my joinList(emailValues) & tab & my joinList(phoneValues) & tab & my joinList(addressValues)
end contactLine

on joinList(valuesList)
    set AppleScript's text item delimiters to " | "
    set joined to valuesList as text
    set AppleScript's text item delimiters to ""
    return my cleanText(joined)
end joinList

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
