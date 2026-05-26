# Decision: Command QA Sandbox And Self-Healing Loop

## Status

Accepted for staged implementation.

## Context

The command registry now tracks hundreds of commands across core runtime, safety, web, forums, brain providers, platform scaffolding, native skills, prompt tracking, natural-language UX, and safe autonomy. Manual QA alone is no longer enough to keep command behavior, docs, tests, and maturity evidence aligned.

## Decision

Build a Command QA Sandbox that starts with metadata validation and safe read-only command checks, then deepens through mocks and disposable workspaces. The sandbox may generate bugs, regression stubs, and self-heal plans, but it must remain safe-only by default and must not approve, commit, push, or enable high-risk behavior.

## Consequences

- Command QA becomes an explicit productization feature.
- QA results can inform feature maturity only when evidence exists.
- Automated QA cannot prove live provider or personal-data readiness.
- Self-healing proposals remain subordinate to ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, tests, docs, and human review.

## Non-Negotiables

- No automatic HIGH or CRITICAL execution.
- No real personal-data reads.
- No sends or external writes.
- No real user file mutation outside disposable QA roots.
- No package installs or background jobs.
- No commit/push/merge.
