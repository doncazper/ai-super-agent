# Skill Testing

The native skill test harness validates reviewed native skill metadata and safety fixtures without executing skill code. It is a release-hardening tool, not an installer, runtime, or permission grant.

## Commands

```bash
python smart_agent.py skills test <skill_id>
python smart_agent.py skills test --all-safe
python smart_agent.py eval run --native-skills
```

`skills test` returns JSON with pass/fail/skipped checks. `--all-safe` runs only the safe default set across non-HIGH, non-CRITICAL, non-personal-data native skills.

## Check Categories

- manifest validation
- dependency gating
- provenance and trust validation
- lockfile verification
- conflict detection
- profile allowlist visibility
- compatibility matrix status
- prompt-injection fixture
- secret fixture
- policy denial fixture
- approval-required fixture
- docs presence
- command registry presence

## Safe Defaults

- HIGH, CRITICAL, FORBIDDEN, and personal-data skills are skipped by default.
- Missing dependencies are reported as `skipped`/`requires_setup`, not auto-installed.
- Prompt-injection and secret fixtures are static strings inspected as `UNTRUSTED_DOCUMENT`.
- No external scripts, package managers, plugin runtimes, providers, connectors, or native platform modules are executed.
- Results may inform `FEATURE_MATURITY`, but they do not make a skill user-ready without docs, command registry status, policy/audit evidence, and manual QA.

## Failure Signals

Treat any of these as release blockers:

- a high/critical or personal-data skill runs by default
- a candidate skill script is executed
- a dependency installer is invoked
- provider or connector calls happen during metadata checks
- a prompt-injection fixture is not caught
- a secret fixture is not caught
- a blocking conflict is ignored
- command registry or docs evidence is missing for a user-visible command
