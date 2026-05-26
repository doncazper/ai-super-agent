# Codebase Bug Review Baseline

Prompt ID: `CODEBUG-01`
Date: 2026-05-25

## Scope

Baseline review only. No code fixes were made in this prompt except prompt-pack import/queue tracking performed before the run.

## Git State

- Branch: `checkpoint/large-working-tree-20260523`
- Working tree: large dirty tree with many modified tracked files and many untracked feature-pack files from recent Brain, Hermes, productization, and CODEBUG import work.
- Diff stat at baseline: 33 tracked files changed, 2823 insertions, 131 deletions, plus many untracked directories/files.
- Release implication: not release-clean. A clean release-candidate boundary remains a P1 blocker.

## Runtime And Import Checks

- Python: `./.venv/bin/python` 3.12.13.
- `./scripts/agent setup` exits 0 and prints LM Studio setup guidance.
- Targeted imports passed:
  - `smart_agent`
  - `agent.core.orchestrator`
  - `agent.core.router`
  - `agent.core.tool_broker`
  - `agent.safety.policy`
  - `agent.safety.validation`
  - `agent.brain.registry`
  - `agent.tools.registry`
  - `agent.ui.cli_commands`

## Command And Policy Checks

- `./.venv/bin/python smart_agent.py commands validate`: passed with 484 commands and no registry/matrix problems.
- `make policy-check`: passed startup policy and capability manifest validation.
- `./.venv/bin/python smart_agent.py prompts audit`: passed while `CODEBUG-01` was active; active_count 1, completed_count 207, queued_count 10.
- `./.venv/bin/python smart_agent.py doctor`: passed with LM Studio reachable, model available, 205 tools registered, personal tools disabled by default, and no CRITICAL actions enabled by default.

## Tests

- Focused productization/feature-registry docs tests passed: 7 passed.
- Full suite was not rerun in CODEBUG-01 because it was already run immediately before the pack import and is required again after CODEBUG-04 and CODEBUG-08. Baseline keeps the full-suite requirement queued for those prompts.

## Docs Validation

No dedicated docs validation command was found. `./.venv/bin/python smart_agent.py docs validate` is interpreted as a normal chat prompt and returns generic documentation-advice text. This is recorded as a CLI/docs-validation UX bug, not as a validation pass.

## Failing Tests

None in CODEBUG-01 focused checks.

## Import Errors

None found in targeted import checks.

## CLI Startup Errors

- Empty invocation exits 2 with usage text: `usage: smart_agent.py [--interactive] [--no-tools] [--debug] <message>`.
- This is acceptable as current argparse behavior, though a friendlier `setup`/`doctor` hint could be considered later.

## Command Registry Drift

No registry drift found by `commands validate`.

## Safety Validation Issues

None found in startup policy or capability manifest validation.

## Baseline Conclusion

The codebase is locally healthy enough to continue the CODEBUG batch. The highest-risk issue is release process hygiene, not a failing runtime test: the dirty tree is too large for safe release review and prompt tracker/docs validation semantics remain uneven.

