# Artifact Tracking Decision

Prompt ID: CLEAN-RELEASE-BOUNDARY-POST-CANON-01
Date: 2026-05-26 UTC / 2026-05-25 PDT

## Decision

Generated reports are local evidence by default, not source artifacts.

Track source code, tests, docs, prompt records, prompt packs selected by the user, dogfood/eval fixtures, and `.gitkeep` placeholders for report directories. Do not track timestamped generated report payloads by default.

## Track By Default

- Source code under `agent/` and `smart_agent.py`.
- Tests under `tests/`.
- Dogfood suite definitions under `dogfood_suites/`.
- Eval fixtures under `eval_cases/`.
- Documentation under `docs/`.
- Prompt records under `prompts/completed/` when completion evidence exists.
- Prompt packs under `prompts/packs/` only when intentionally imported/preserved.
- `.gitkeep` placeholders for report directories.

## Ignore By Default

- `reports/qa/*` run logs, JSONL, and Markdown run outputs.
- `reports/brain/*.json` benchmark/eval outputs.
- `reports/autonomy/*.json` proposal outputs.
- `reports/performance/*` generated static/startup/benchmark/profile/recommendation/regression/baseline/patch-plan reports.
- `reports/evals/*.json` timestamped eval outputs.
- Raw session/audit logs, local caches, pyc files, local databases, OAuth/token/private-key/credential files.

## Promote Only By Exception

A generated report may be promoted to tracked docs only when:

1. It is redacted.
2. It contains no raw prompts, raw provider data, raw command output, secrets, or personal data.
3. It is renamed or summarized as a stable documentation artifact.
4. It is linked from a completion report or release gate.
5. The user explicitly wants that artifact retained.

## Change Made In This Pass

Top-level `.gitignore` now ignores `reports/performance/*` while allowing `reports/performance/.gitkeep`.

