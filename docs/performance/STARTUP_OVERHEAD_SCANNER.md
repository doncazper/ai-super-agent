# Startup Overhead Scanner

Status: implemented for PERF-04 safe local startup/import timing.

The startup scanner measures a bounded set of safe CLI startup/status commands and selected module import timings in subprocesses with explicit timeouts. It stores redacted report artifacts under `reports/performance/`.

## Safety Boundary

- No LM Studio chat/completion calls.
- No live provider calls.
- No personal-data commands.
- No model loading or model downloads.
- No background services.
- No package installation.
- No HIGH or CRITICAL commands.
- Missing commands are skipped, not treated as release failures.
- Every subprocess uses a timeout.

## Default Measurements

- `./scripts/agent --help`
- `python smart_agent.py doctor`
- `python smart_agent.py commands list`
- `python smart_agent.py runtime status`
- `python smart_agent.py brain providers`
- Import timings for `smart_agent`, `agent.ui.cli_commands`, `agent.tools.registry`, `agent.core.tool_broker`, and `agent.performance.static_scanner`

## Commands

- `python smart_agent.py perf scan --startup`
- `python smart_agent.py perf startup`
- `python smart_agent.py perf startup --json`

Optional bounds:

- `--timeout <seconds>`
- `--max-commands <count>`
- `--max-imports <count>`

These commands route through ToolBroker and write local redacted report metadata. They do not run the full test suite or benchmarks.
