from __future__ import annotations

from typing import Any


SENSITIVE_CONTACT_FIELD_TOKENS = {
    "address",
    "email",
    "mail",
    "mobile",
    "note",
    "phone",
    "postal",
    "street",
}

CONTACT_FIELD_REDACTION = "[CONTACT_FIELD_REDACTED]"
CONTACT_SCOPE_REDACTION = "[CONTACT_SELECTED_SCOPE_REDACTED]"


def is_sensitive_contact_field(field_name: str) -> bool:
    normalized = field_name.casefold()
    return any(token in normalized for token in SENSITIVE_CONTACT_FIELD_TOKENS)


def redact_contact_value(field_name: str, value: Any) -> Any:
    if is_sensitive_contact_field(field_name) and value not in (None, "", []):
        return CONTACT_FIELD_REDACTION
    return value


def redact_contact_changes(changes: Any) -> Any:
    if not isinstance(changes, dict):
        return changes
    redacted: dict[str, Any] = {}
    for field, value in changes.items():
        field_name = str(field)
        if isinstance(value, dict) and ("old" in value or "new" in value):
            redacted[field_name] = {
                "old": redact_contact_value(field_name, value.get("old")),
                "new": redact_contact_value(field_name, value.get("new")),
            }
        else:
            redacted[field_name] = redact_contact_value(field_name, value)
    return redacted


def redact_contact_field_diff(field_diff: Any) -> Any:
    if isinstance(field_diff, list):
        return [_redact_diff_item(item) for item in field_diff]
    if isinstance(field_diff, dict):
        return {
            str(field): {
                "old": redact_contact_value(str(field), values.get("old") if isinstance(values, dict) else None),
                "new": redact_contact_value(str(field), values.get("new") if isinstance(values, dict) else values),
            }
            for field, values in field_diff.items()
        }
    return field_diff


def redact_contact_args(args: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(args)
    for key in ("selected_scope_token", "contact_id"):
        if key in redacted:
            redacted[key] = CONTACT_SCOPE_REDACTION
    if "changes" in redacted:
        redacted["changes"] = redact_contact_changes(redacted["changes"])
    if "field_diff" in redacted:
        redacted["field_diff"] = redact_contact_field_diff(redacted["field_diff"])
    if "fields" in redacted and isinstance(redacted["fields"], dict):
        redacted["fields"] = redact_contact_changes(redacted["fields"])
    return redacted


def _redact_diff_item(item: Any) -> Any:
    if not isinstance(item, dict):
        return item
    field_name = str(item.get("field", ""))
    redacted = dict(item)
    redacted["old"] = redact_contact_value(field_name, redacted.get("old"))
    redacted["new"] = redact_contact_value(field_name, redacted.get("new"))
    return redacted
