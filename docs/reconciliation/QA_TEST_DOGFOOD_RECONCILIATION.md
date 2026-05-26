# QA Test Dogfood Reconciliation

Last reconciled: 2026-05-25

## Safe Validation Evidence

- `./.venv/bin/python smart_agent.py commands validate`: passed with 522 commands.
- `make policy-check`: passed startup policy and capability manifest validation.
- `./scripts/agent doctor`: passed with Python 3.12.13, valid startup policy, valid capability manifest, personal tools disabled, and critical actions disabled.
- `./.venv/bin/python smart_agent.py dogfood run all_safe --dry-run`: passed as dry-run with skipped preview commands.

## Findings

- Dogfood suites are mostly mock/fixture-safe by default.
- Live provider checks remain opt-in and should not be assumed complete.
- Personal-data dogfood and HIGH/CRITICAL commands must stay skipped by default.
- Command QA sandbox has safe-tier enforcement and no automatic HIGH/CRITICAL execution.
- Regression tests exist for several recent bugfixes, but coverage remains uneven across older feature tracks.

## Deferred

- Dedicated docs validation, feature maturity validation, and prompt tracker validation commands beyond `prompts audit` were not confirmed as separate commands.
- Manual QA remains the largest evidence gap for user-ready claims.
