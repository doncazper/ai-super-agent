# Command QA Runner

`python smart_agent.py qa commands run` executes only the safe subset of the generated QA plan.

## Defaults

- Supports Tier 0 and Tier 1 by default.
- Supports Tier 3 only when `--sandbox` is present.
- Uses `--safe-only` by default.
- Runs at most 10 commands unless `--limit` is explicitly set.
- Uses `./.venv/bin/python` when present.
- Uses no shell.
- Skips command examples with placeholders.
- Redacts stdout/stderr before writing logs.
- Writes reports under `reports/qa/`.
- Initializes Tier 3 fixture workspaces under `reports/qa/workspaces/current`.

## Examples

```bash
python smart_agent.py qa commands run --tier 0
python smart_agent.py qa commands run --tier 1 --safe-only --limit 5
python smart_agent.py qa commands run --tier 3 --sandbox --limit 5
python smart_agent.py qa commands report --last
```

The runner is not a general shell. It runs only approved command-registry examples from the generated QA plan.
