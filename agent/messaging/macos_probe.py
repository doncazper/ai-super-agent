from __future__ import annotations

import json
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

from agent.safety.policy import RiskLevel
from agent.tools.errors import ToolError


ProbeRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]

DEFAULT_MESSAGES_APP_PATHS: tuple[str, ...] = (
    "/System/Applications/Messages.app",
    "/Applications/Messages.app",
)
PROBE_RESULT_PATH = Path("data/macos_messages_probe.json")


@dataclass(frozen=True)
class MacOSMessagesProbeResult:
    supported: bool | str
    platform: str
    messages_app_found: bool
    automation_permission_status: str
    send_capability_known: bool = False
    limitations: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_user_setup: bool = False
    messages_app_path: str = ""
    applescript_available: bool = False
    applescript_read_only_probe_ok: bool = False
    applescript_bundle_id: str = ""
    applescript_version: str = ""
    full_disk_access_required: bool = False
    private_messages_db_accessed: bool = False
    message_content_read: bool = False
    send_executed: bool = False
    commands_run: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        return payload


def run_macos_messages_probe(
    *,
    project_root: str | Path = ".",
    platform_name: str | None = None,
    app_paths: Sequence[str] = DEFAULT_MESSAGES_APP_PATHS,
    runner: ProbeRunner | None = None,
    explain_permissions: bool = False,
) -> tuple[MacOSMessagesProbeResult, str]:
    current_platform = platform_name or platform.system()
    commands_run: list[str] = []
    if current_platform != "Darwin":
        result = MacOSMessagesProbeResult(
            supported=False,
            platform=current_platform,
            messages_app_found=False,
            automation_permission_status="unsupported_non_macos",
            limitations=["macOS Messages automation is available only on macOS."],
            next_steps=["Use manual handoff or iOS user-confirmed compose on non-macOS platforms."],
            requires_user_setup=True,
            commands_run=commands_run,
        )
        return result, _save_probe_result(project_root, result)

    app_path = _first_existing_path(app_paths)
    if not app_path:
        result = MacOSMessagesProbeResult(
            supported=False,
            platform=current_platform,
            messages_app_found=False,
            automation_permission_status="not_checked_app_missing",
            limitations=["Messages.app was not found in the standard macOS application locations."],
            next_steps=["Confirm Messages.app is installed before any future automation feasibility work."],
            requires_user_setup=True,
            commands_run=commands_run,
        )
        return result, _save_probe_result(project_root, result)

    osascript = shutil.which("osascript")
    if not osascript:
        result = MacOSMessagesProbeResult(
            supported="unknown",
            platform=current_platform,
            messages_app_found=True,
            messages_app_path=app_path,
            automation_permission_status="unknown_osascript_unavailable",
            limitations=["The `osascript` command is unavailable, so AppleScript metadata probing could not run."],
            next_steps=["Install or restore macOS AppleScript tooling before future automation probes."],
            requires_user_setup=True,
            commands_run=commands_run,
        )
        return result, _save_probe_result(project_root, result)

    run = runner or _run_command
    bundle_command = [osascript, "-e", 'id of application "Messages"']
    version_command = [osascript, "-e", 'version of application "Messages"']
    bundle = _run_probe_command(bundle_command, run, commands_run)
    version = _run_probe_command(version_command, run, commands_run)
    denied = _is_automation_denied(bundle.stderr) or _is_automation_denied(version.stderr)
    read_only_ok = bundle.returncode == 0 and bool(bundle.stdout.strip())
    permission_status = "not_required_for_launchservices_metadata"
    limitations = [
        "This probe does not prove that sending is safe or supported.",
        "No Messages account status, message content, thread list, or private database was read.",
        "No send verb was executed.",
    ]
    next_steps = [
        "Keep macOS Messages send adapters blocked until a future explicit send decision and Action Center release gate.",
        "If a future live automation probe is approved, use a harmless selected-scope check first and stop at any permission prompt.",
    ]
    requires_setup = False
    if denied:
        permission_status = "denied_or_not_granted"
        limitations.append("macOS Automation permission appears denied or not granted for this process.")
        next_steps.append("Open System Settings > Privacy & Security > Automation and review the controlling app permission.")
        requires_setup = True
    elif not read_only_ok:
        permission_status = "unknown_read_only_probe_failed"
        limitations.append(_compact_error(bundle.stderr) or "AppleScript metadata probe failed.")
        next_steps.append("Run `python smart_agent.py messages probe --explain-permissions` for setup guidance.")
        requires_setup = True
    if explain_permissions:
        next_steps.extend(
            [
                "Do not grant Full Disk Access for this probe.",
                "Do not grant Accessibility for this probe.",
                "Future send work, if ever approved, must still require exact CRITICAL per-action approval.",
            ]
        )

    result = MacOSMessagesProbeResult(
        supported="unknown" if read_only_ok else False,
        platform=current_platform,
        messages_app_found=True,
        messages_app_path=app_path,
        automation_permission_status=permission_status,
        limitations=limitations,
        next_steps=next_steps,
        requires_user_setup=requires_setup,
        applescript_available=True,
        applescript_read_only_probe_ok=read_only_ok,
        applescript_bundle_id=bundle.stdout.strip() if bundle.returncode == 0 else "",
        applescript_version=version.stdout.strip() if version.returncode == 0 else "",
        commands_run=[" ".join(command) for command in (bundle_command, version_command)],
    )
    return result, _save_probe_result(project_root, result)


def last_probe_result(project_root: str | Path = ".") -> dict[str, Any] | None:
    path = Path(project_root).resolve() / PROBE_RESULT_PATH
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"status": "unreadable", "path": str(path)}
    return payload if isinstance(payload, dict) else {"status": "invalid", "path": str(path)}


def make_macos_probe_tools(project_root: str | Path) -> dict[str, Any]:
    root = Path(project_root).resolve()

    def probe(explain_permissions: bool = False) -> dict[str, Any]:
        try:
            result, path = run_macos_messages_probe(project_root=root, explain_permissions=explain_permissions)
        except OSError as exc:
            raise ToolError(f"macOS Messages probe failed: {exc}") from exc
        return {
            "status": "ok",
            "probe": result.to_dict(),
            "connector_status_recorded": True,
            "connector_status_path": path,
            "_audit": {
                "files_written": [path],
                "commands_run": result.commands_run,
                "result_summary": "macOS Messages feasibility probe ran; no private database read and no send executed.",
            },
        }

    return {"messages.probe": probe}


MACOS_PROBE_SCHEMAS: dict[str, dict[str, Any]] = {
    "messages.probe": {
        "type": "function",
        "function": {
            "name": "messages.probe",
            "description": (
                "Safely probe macOS Messages automation feasibility using metadata-only checks. "
                "Does not read message content, require Full Disk Access, or send."
            ),
            "parameters": {
                "type": "object",
                "properties": {"explain_permissions": {"type": "boolean"}},
                "additionalProperties": False,
            },
        },
    }
}


def _first_existing_path(paths: Sequence[str]) -> str:
    for raw in paths:
        if Path(raw).exists():
            return raw
    return ""


def _run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        capture_output=True,
        check=False,
        text=True,
        timeout=5,
    )


def _run_probe_command(command: Sequence[str], runner: ProbeRunner, commands_run: list[str]) -> subprocess.CompletedProcess[str]:
    commands_run.append(" ".join(command))
    return runner(command)


def _is_automation_denied(stderr: str) -> bool:
    lowered = stderr.lower()
    return "not authorized" in lowered or "not authorised" in lowered or "-1743" in lowered or "automation" in lowered and "denied" in lowered


def _compact_error(stderr: str) -> str:
    return " ".join(stderr.strip().split())[:240]


def _save_probe_result(project_root: str | Path, result: MacOSMessagesProbeResult) -> str:
    path = Path(project_root).resolve() / PROBE_RESULT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
