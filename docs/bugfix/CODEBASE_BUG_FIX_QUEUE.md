# Codebase Bug Fix Queue

Prompt ID: `CODEBUG-01`
Date: 2026-05-25

## P0

No P0 bug verified in baseline.

## P1

| Bug ID | Title | Status | Owner prompt | Notes |
|---|---|---|---|---|
| CODEBUG-P1-001 | Clean release-candidate boundary needed | deferred | future release-hardening prompt | Do not fix inside CODEBUG unless explicitly scoped; requires human-reviewable staging/cleanup. |
| CODEBUG-P1-002 | Prompt tracker stale rows/files need reconciliation | in_review | CODEBUG-06 | Do not delete prompt files without archive/evidence rules. |

## P2

| Bug ID | Title | Status | Owner prompt | Notes |
|---|---|---|---|---|
| CODEBUG-P2-001 | `smart_agent.py docs validate` is not a real docs validator | open | CODEBUG-03 or CODEBUG-06 | Command falls through to chat. Either add a real docs command later or document as not available. |
| CODEBUG-P2-002 | Static bypass scan needed for subprocess/network/file anti-patterns | completed | CODEBUG-07 | Static scan report created; no scoped code fix confirmed. Future allowlist review recommended. |
| CODEBUG-P2-003 | Provider/setup errors need targeted UX review | open | CODEBUG-05 | Review missing-provider and disabled-connector behavior without live calls. |
| CODEBUG-P2-004 | `commands list` traceback on closed stdout pipe | fixed | CODEBUG-03 | Fixed top-level `BrokenPipeError` handling and added regression test. |

## P3

| Bug ID | Title | Status | Owner prompt | Notes |
|---|---|---|---|---|
| CODEBUG-P3-001 | Empty invocation could provide friendlier next steps | deferred | future UX polish | Current usage exit is acceptable and safe. |
