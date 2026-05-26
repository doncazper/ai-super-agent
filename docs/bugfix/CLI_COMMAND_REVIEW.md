# CLI And Command Bug Review

Prompt ID: `CODEBUG-03`
Date: 2026-05-25

## Scope

Review CLI dispatch, command registry behavior, command validation, and command UX for small, safe release-hardening fixes.

## Non-Goals

- No major CLI redesign.
- No command renames or removals.
- No new user-visible feature commands.
- No policy, approval, audit, or ToolBroker weakening.
- No live provider calls.

## Requirements Checked

- Command registry validation still passes.
- Existing command registry list/show/search/legacy/validate/qa-plan tests still pass.
- Command output should not produce noisy Python tracebacks for ordinary shell usage.
- Unknown command registry IDs should fail clearly without invoking providers or personal data.

## Bugs Found

| Bug ID | Severity | Status | Evidence | Fix |
|---|---:|---|---|---|
| CODEBUG-P2-004 | P2 | fixed | `set -o pipefail; ./.venv/bin/python smart_agent.py commands list \| head -5` raised `BrokenPipeError` traceback. | Added top-level `BrokenPipeError` handling in `smart_agent.py` and regression coverage in `tests/test_command_registry.py`. |

## Bugs Deferred

| Bug ID | Severity | Status | Notes |
|---|---:|---|---|
| CODEBUG-P2-001 | P2 | deferred | `smart_agent.py docs validate` is not a registered command and falls through to chat. This needs a dedicated docs validation design or a safer unknown-command UX change; not fixed in CODEBUG-03 to avoid broad dispatch behavior changes. |
| CODEBUG-P3-001 | P3 | deferred | Empty invocation prints argparse usage and exits 2. Safe but terse; leave for future CLI UX polish. |

## Tests And Validation

- `./.venv/bin/python -m pytest -q tests/test_command_registry.py`: 6 passed.
- `set -o pipefail; ./.venv/bin/python smart_agent.py commands list | head -5`: passed without traceback.
- `./.venv/bin/python smart_agent.py commands validate`: passed with 484 commands and no registry/matrix problems.

## Safety Notes

The fix is limited to top-level process shutdown behavior after a downstream pipe closes. It does not change command routing, command outputs, command registry records, ToolBroker execution, policy gates, approval behavior, audit logging, or provider access.
