# Tracker Maintenance

Last updated: 2026-05-25

Tracker maintenance should preserve history while making the current state easier to find.

## Review Cadence

- Every Codex run: update `docs/PROJECT_STATE.md` and `docs/COMPLETION_REPORT.md`.
- Every user-visible change: update `CHANGELOG.md`.
- Every feature, connector, workflow, command, policy, approval, audit, or memory change: update `docs/FEATURE_REGISTRY.md` and `docs/FEATURE_MATURITY.md`.
- Every command change: update `docs/COMMAND_REGISTRY.md` and `docs/COMMAND_TEST_MATRIX.md`.
- Every release gate: update release docs, `docs/TRACKER_DASHBOARD.md`, and `docs/TRACKER_CONSISTENCY_REPORT.md`.
- Every major prompt batch: update prompt tracking and `docs/PROMPT_AUDIT.md`.

## Anchored Edits

Prefer small anchored edits:

1. Add a new row near the top of a table when it represents the latest work.
2. Add a short status paragraph under the relevant heading.
3. Link to detailed evidence instead of copying long evidence blocks.
4. Preserve old rows unless they are moved to an archive with an evidence link.
5. Avoid broad table reformatting unless explicitly requested.

## Feature Maturity Updates

When updating `docs/FEATURE_MATURITY.md`:

- Keep maturity conservative.
- Do not treat prompt count as proof.
- Do not mark live validation unless an actual live run is recorded.
- Do not mark user-ready without docs, diagnostics, manual QA, and release-gate evidence.
- Keep stubbed/planned features at Scaffolded/Specified unless implementation and tests exist.

## Command Registry Updates

When updating `docs/COMMAND_REGISTRY.md`:

- Every command needs an ID, command string, group, description, example, status, risk level, trust level, approval requirement, side effects, ToolBroker path, audit behavior, memory behavior, test coverage, manual QA status, docs link, and last verified date.
- Deprecated commands need a replacement or reason.
- Removed commands remain listed with removal date and reason.
- Run `./.venv/bin/python smart_agent.py commands validate` after edits.

## Prompt Queue Updates

When updating prompt tracking:

- Keep at most one active prompt.
- Mark failed prompts with a reason.
- Do not run recovered prompts automatically.
- If a prompt is superseded, link the replacement.
- Run `./.venv/bin/python smart_agent.py prompts audit` after prompt status changes.

## Changelog, Completion Report, And Project State

Use this order for most runs:

1. Record the user-visible change in `CHANGELOG.md` if applicable.
2. Record feature status and maturity changes.
3. Append evidence to `docs/COMPLETION_REPORT.md`.
4. Update `docs/PROJECT_STATE.md` last so it reflects final status, tests, blockers, and next action.

## Validation Commands

Use the repo Python interpreter:

```bash
./.venv/bin/python -m pytest -q
./.venv/bin/python -c "from agent.safety.validation import validate_startup_policy; validate_startup_policy()"
./.venv/bin/python -c "import yaml; from agent.config.schema import validate_capabilities_config; validate_capabilities_config(yaml.safe_load(open('config/capabilities.yaml')))"
./.venv/bin/python smart_agent.py commands validate
./.venv/bin/python smart_agent.py prompts audit
```

Run targeted tests first when a focused tracker validation exists, then run the full suite when practical.
