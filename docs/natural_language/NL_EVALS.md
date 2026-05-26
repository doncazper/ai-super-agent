# Natural-Language Evals

Natural-language command understanding evals are fixture-backed checks for request interpretation, command mapping, clarification, denial, approval requirements, and no-execution behavior.

## Commands

- `python smart_agent.py eval run --natural-language`
- `python smart_agent.py eval report --natural-language`

The report command is an alias for the latest eval report. The run command uses fixtures under `eval_cases/natural_language/` and does not execute mapped commands, call tools, call providers, read personal data, write memory, or consume approvals.

## Fixture Fields

Each fixture records:

- `input_text`
- `expected_intent`
- `expected_safety_outcome`
- `expected_command_group`
- `should_execute`
- `should_clarify`
- `should_require_approval`
- `should_deny`
- `notes`

The eval runner verifies that safe cases can be suggested, risky cases remain not executable, ambiguous cases clarify, unsupported cases report help/missing intent, and audit previews show no tools or commands executed.

## Categories

The v1 fixture set covers weather, web/research, news, Reddit/forums, help/commands, doctor/status, memory, workspace, prompt tracker, bug/session review, ambiguous requests, personal-data requests, send/write requests, unsupported requests, and deprecated/legacy command phrasing.
