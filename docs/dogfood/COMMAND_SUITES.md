# Dogfood Command Suites

Suite files live in `dogfood_suites/` and are loaded as data.

## Suite Schema

```yaml
suite_id: all_safe
name: All Safe Dogfood Subset
description: Safe subset of routine manual QA checks.
risk_level: LOW
requires_live_lmstudio: false
requires_web: true
requires_personal_data: false
default_enabled: true
commands:
  - id: safe_doctor
    description: Run doctor diagnostics.
    command: python smart_agent.py doctor
    expected_behavior: Runtime readiness is shown without personal-data reads.
    failure_signals: Startup validation failure or secret leakage.
    tags: [core, doctor]
    expected_exit_codes: [0]
```

Required command fields:

- `id`
- `description`
- `command`
- `expected_behavior`
- `failure_signals`
- `tags`

Optional command fields:

- `expected_exit_codes`: defaults to `[0]`.

## Current Suites

| Suite | Risk | Live LM Studio | Web | Personal data | Default | Purpose |
|---|---|---:|---:|---:|---:|---|
| `core` | LOW | yes | no | no | yes | Core runtime, no-tool chat, time tool, doctor, status, tools, config, preflight. |
| `weather` | LOW | no | yes | no | yes | Weather doctor, current, forecast, bad location, cache, alerts. |
| `web` | LOW | no | yes | no | yes | Research, safe URL fetch, blocked URL behavior, source-grounding, provider status. |
| `workspace_files` | MEDIUM | no | no | no | yes | Workspace list/read/summarize/write/patch and traversal denial. |
| `memory` | LOW | no | no | no | yes | Synthetic project-fact memory add/search/export/clear and secret refusal. |
| `approvals` | MEDIUM | no | no | no | yes | Preflight approval checks and safe queue/denial paths. |
| `native_skills` | LOW | no | no | no | yes | Skill registry, validation, finder, and safe/risky vetter fixtures. |
| `personal_dry_run` | LOW | no | no | no | no | Preflight-only personal connector dry-runs. |
| `all_safe` | LOW | no | yes | no | yes | Routine safe subset for first dogfood session. |

## Updating Suites

When adding or changing a suite:

1. Keep commands as `python smart_agent.py ...`.
2. Add expected behavior and failure signals.
3. Avoid personal-data reads by default.
4. Add or update tests in `tests/test_dogfood_suites.py`.
5. Update `docs/COMMAND_REGISTRY.md`, `docs/FEATURE_MATURITY.md`, `docs/PROJECT_STATE.md`, and `docs/COMPLETION_REPORT.md`.
