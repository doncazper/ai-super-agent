# Canonical State Boundaries

Status: CANON-01 implemented as read-only metadata.

## Allowed

- Read local repo tracker files.
- Read local git branch, last commit, and dirty-worktree counts.
- Report active prompt, next prompt, and validation summaries.
- Preview tracker conflicts.
- Redact secret-like fields before output.

## Forbidden

- Execute tools or workflows.
- Call model, web, personal-data, provider, or live services.
- Start background processes.
- Mutate prompt trackers during preview.
- Infer completion without evidence.
- Treat summary dashboards as primary truth.

## Reconciliation Rule

`runtime reconcile-preview` reports conflicts and recommendations only. Actual tracker fixes still require explicit small anchored edits or prompt tracking commands.
