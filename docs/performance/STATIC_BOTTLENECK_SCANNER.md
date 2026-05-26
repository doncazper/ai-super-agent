# Static Bottleneck Scanner

Status: implemented for PERF-03 local heuristic scanning.

The static scanner inspects Python source text for performance-risk patterns and writes redacted reports under `reports/performance/`. It is intentionally heuristic and review-oriented: findings are not proof of a bug and do not apply fixes automatically.

## Safety Boundary

- The scanner must not execute scanned code.
- It does not import scanned modules.
- It does not call live providers.
- It does not use paid APIs.
- It does not download models.
- It does not access personal data.
- It does not start background services.
- It does not run tests or benchmarks.
- It does not apply patches.

## Default Exclusions

- `.venv`
- `.git`
- `__pycache__`
- `.pytest_cache`
- `logs`
- `reports`
- `media_outputs`
- `.qa_workspace`

## Heuristic Patterns

- Module-level IO/network calls.
- Optional heavy imports in startup paths.
- Repeated config loads in loops.
- Unbounded file reads.
- Broad `os.walk`, `glob`, or `rglob`.
- `subprocess` calls without `timeout=`.
- `requests` or `httpx` calls without `timeout=`.
- Repeated regex compilation candidates.
- Unbounded retry loop candidates.
- Large reads in status/dashboard paths.
- Direct live provider calls in doctor/status paths.
- Full test-suite runs from normal command paths.

## Commands

- `python smart_agent.py perf scan`
- `python smart_agent.py perf scan --static`
- `python smart_agent.py perf scan --static --max-files 200`

Both scan commands route through ToolBroker and write redacted local reports. `perf scan` currently delegates to the static scanner.
