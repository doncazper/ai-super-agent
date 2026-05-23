# Command QA Runbook

Use this runbook to keep command behavior, docs, and tests aligned.

## Daily Command Smoke Test

1. Run `python smart_agent.py commands validate`.
2. Run `python smart_agent.py commands qa-plan`.
3. Run SAFE/LOW examples from the groups changed in the current run.
4. Run `python smart_agent.py doctor`.
5. Run `python smart_agent.py tools list`.
6. Run focused tests for touched command groups.

## Weekly Full Command Review

1. Run the full test suite.
2. Run startup policy validation.
3. Run capability manifest validation.
4. Run `python smart_agent.py commands validate`.
5. Review `docs/COMMAND_TEST_MATRIX.md` for stale manual QA status.
6. Review `docs/COMMAND_LEGACY.md` for obsolete or confusing command paths.

## Logging Failures

- Add a bug ID to the `Linked bug IDs` column in `docs/COMMAND_TEST_MATRIX.md`.
- Record the failing command, environment, expected behavior, actual behavior, and relevant audit/report path.
- Do not paste secrets or private personal data into bug reports.

## Adding Regression Tests

- Add a focused test under `tests/` for the command group.
- Mock live providers and personal-data connectors by default.
- Use live tests only when explicitly opted in.

## Marking Commands Verified

- Update `Last manual test result` in `docs/COMMAND_TEST_MATRIX.md`.
- Update `Manual QA status` and `Last verified` in `docs/COMMAND_REGISTRY.md`.
- Update `docs/FEATURE_MATURITY.md` if manual QA changes maturity.

## Updating Feature Maturity

Manual QA can raise UX/docs readiness, but it does not replace automated tests, policy checks, approval checks, or audit coverage.
