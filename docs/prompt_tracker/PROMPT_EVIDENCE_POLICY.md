# Prompt Completion Evidence Policy

Prompt count is useful context, not proof of maturity. A prompt is complete only when the repo has supporting evidence that the requested work, tests, and tracking updates happened.

## Classifications

- `complete_verified`: prompt is completed and has multiple tracked evidence links.
- `likely_complete`: prompt is completed and has at least one tracked evidence link.
- `partial`: prompt has evidence but is not marked complete.
- `no_evidence`: prompt has no tracked evidence.
- `failed`: prompt is marked failed.
- `blocked`: prompt is marked blocked.
- `superseded`: prompt is marked superseded.
- `stale`: prompt is marked complete but has no supporting evidence.

## Evidence Sources

Evidence may come from docs, tests, dogfood suites, eval cases, reports, command registry entries, completion reports, feature registry/maturity updates, and prompt files.

## Completion Rules

- `mark-complete` requires test and docs status, or explicit `--unknown`.
- `mark-failed` requires a reason.
- Only one prompt may be active at a time.
- Superseded prompts must identify the replacement prompt.
- Recovery commands report plans only; they do not execute prompts.
