from __future__ import annotations

from agent.safety.approvals import ApprovalRequest, ApprovalStore
from agent.safety.policy import RiskLevel
from agent.tools.registry import default_registry
from agent.ui.cli_commands import dispatch_cli
from agent.ui.interactive import InteractiveState, run_interactive
from smart_agent import parse_args


def input_script(lines: list[str]):
    pending = iter(lines)

    def read(prompt: str) -> str:
        return next(pending)

    return read


def test_parse_args_allows_interactive_without_message() -> None:
    args = parse_args(["--interactive"])

    assert args.interactive is True
    assert args.message == []


def test_dispatch_cli_leaves_interactive_for_main_entrypoint() -> None:
    assert dispatch_cli(["--interactive"]) is None


def test_interactive_help_and_exit_do_not_call_model() -> None:
    calls: list[str] = []
    output: list[str] = []

    def respond(message: str, state: InteractiveState) -> str:
        calls.append(message)
        return "model answer"

    result = run_interactive(
        respond,
        registry=default_registry(),
        input_fn=input_script([":help", ":exit"]),
        output_fn=output.append,
        error_fn=output.append,
    )

    assert result == 0
    assert calls == []
    assert any(":doctor" in line for line in output)
    assert output[-1] == "Goodbye."


def test_interactive_no_tools_toggle_affects_responder_state() -> None:
    states: list[bool] = []
    output: list[str] = []

    def respond(message: str, state: InteractiveState) -> str:
        states.append(state.no_tools)
        return f"echo: {message}"

    result = run_interactive(
        respond,
        registry=default_registry(),
        input_fn=input_script([":no-tools on", "hello", ":no-tools off", "again", ":exit"]),
        output_fn=output.append,
        error_fn=output.append,
    )

    assert result == 0
    assert states == [True, False]
    assert "No-tools mode is on." in output
    assert "No-tools mode is off." in output


def test_interactive_doctor_command_does_not_call_model(monkeypatch) -> None:
    from agent.ui import interactive
    from agent.ui.doctor import DoctorCheck

    calls: list[str] = []
    output: list[str] = []
    monkeypatch.setattr(interactive, "run_doctor", lambda: [DoctorCheck("config_loaded", "ok", "loaded")])

    def respond(message: str, state: InteractiveState) -> str:
        calls.append(message)
        return "model answer"

    result = run_interactive(
        respond,
        registry=default_registry(),
        input_fn=input_script([":doctor", ":exit"]),
        output_fn=output.append,
        error_fn=output.append,
    )

    assert result == 0
    assert calls == []
    assert any("[ok] config_loaded" in line for line in output)


def test_interactive_unknown_command_reports_help_hint() -> None:
    output: list[str] = []

    result = run_interactive(
        lambda message, state: "unused",
        registry=default_registry(),
        input_fn=input_script([":missing", ":exit"]),
        output_fn=output.append,
        error_fn=output.append,
    )

    assert result == 0
    assert "Unknown command. Type :help for interactive commands." in output


def test_interactive_approvals_list_and_show_use_session_store(tmp_path) -> None:
    output: list[str] = []
    store = ApprovalStore(tmp_path / "approvals.json")
    request = ApprovalRequest(
        capability="git.commit",
        tool_name="git.commit",
        risk_level=RiskLevel.HIGH,
        summary="Commit changes",
        args_preview={"message": "safe"},
    )
    store.add(request)

    result = run_interactive(
        lambda message, state: "unused",
        registry=default_registry(),
        approval_store=store,
        input_fn=input_script([":approvals", f":approvals {request.request_id}", ":exit"]),
        output_fn=output.append,
        error_fn=output.append,
    )

    assert result == 0
    assert any('"approvals"' in line for line in output)
    assert any(request.request_id in line for line in output)
    assert any("Approval required" in line for line in output)
