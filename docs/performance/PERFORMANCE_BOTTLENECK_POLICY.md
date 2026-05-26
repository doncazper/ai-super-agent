# Performance Bottleneck Policy

Performance findings are advisory unless a release gate declares them blockers. The scanner must not execute scanned code during static scans and must not run live providers, personal-data commands, paid APIs, model downloads, or background services.

## Scan Categories

- Startup/import overhead.
- CLI dispatch overhead.
- Command registry loading.
- Prompt tracker loading.
- Capability manifest parsing.
- ToolBroker overhead.
- Audit and redaction overhead.
- File IO hotspots.
- Full-file scans.
- JSON/YAML load hotspots.
- Regex in loops.
- Unbounded loops or retries.
- Missing timeouts.
- Network risks.
- Cache gaps.
- Subprocess inefficiencies.
- Slow tests.
- Provider health overhead.
- Model startup overhead.
- Memory search overhead.
- Report generation overhead.
- Excessive tracker/doc rewrites.

## Severity

- P0: Safety, release, or data-protection issue caused by performance behavior, such as an unbounded scan over sensitive paths.
- P1: Broken core flow or startup/command latency likely to make normal use unreliable.
- P2: Slow implemented feature or repeated IO with clear user impact.
- P3: Local inefficiency, missing cache, or test slowness with limited impact.
- P4: Polish, documentation, or future optimization idea.

## Safety Rules

- Static scans read source text only and exclude generated, private, cache, report, and environment directories by default.
- Startup scans run only safe commands with timeouts.
- Command benchmarks use command registry metadata and reject HIGH, CRITICAL, mutating, provider-live, personal-data, commit, push, package-install, and background-service commands by default.
- Test profiling must never delete, skip, or weaken tests to make timing look better.
- Recommendations and patch plans must be evidence-based and must not apply patches by default.
