# Safe Command Benchmarks

`PERF-05` adds a bounded benchmark runner for command-registry commands that are already classified as safe enough to run repeatedly.

## Commands

- `python smart_agent.py perf benchmark --safe`
- `python smart_agent.py perf benchmark --group core`
- `python smart_agent.py perf benchmark --command "python smart_agent.py commands validate"`

Optional controls:

- `--iterations N` requests 1 to 10 iterations per command.
- `--timeout N` sets a 1 to 60 second timeout per subprocess run.
- `--max-commands N` caps default/group benchmark scope.

## Safety Rules

The runner denies commands that are not active in `docs/COMMAND_REGISTRY.md` metadata, require approval, contain placeholders, have `HIGH` or `CRITICAL` risk, mention personal-data/live-provider/paid-provider/background behavior, or have mutating/report-writing/model/network side effects.

The benchmark stores timing metadata, return codes, and output byte counts only. It does not store raw stdout/stderr, prompts, provider output, personal data, or secrets.

Reports are redacted local artifacts under `reports/performance/`.

## Limitations

Benchmarks are local and approximate. They are useful for comparing repeated safe command metadata paths, not for proving provider or model latency. Live providers, paid APIs, model downloads, background services, personal-data commands, and mutating commands remain out of scope by default.
