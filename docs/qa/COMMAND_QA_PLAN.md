# Command QA Plan

`python smart_agent.py qa commands plan` generates a deterministic QA plan from `docs/COMMAND_REGISTRY.md` and the structured command registry.

## Behavior

- Reads command registry metadata as the source of truth.
- Cross-checks top-level CLI command groups through static discovery where practical.
- Classifies commands into QA Tier 0 through Tier 7.
- Skips planned, stubbed, deprecated, blocked, removed, and legacy commands by default.
- Marks provider/API setup requirements.
- Marks disposable-workspace requirements.
- Marks approval requirements.
- Reports missing examples, risk levels, docs, or tests.
- Does not execute commands.

## Examples

```bash
python smart_agent.py qa commands plan
python smart_agent.py qa commands plan --tier 1
python smart_agent.py qa commands plan --group weather
python smart_agent.py qa commands plan --safe-only
```

The plan is advisory. The later runner must still enforce the plan, tier policy, redaction, timeout, and report boundaries.
