# M9 Controlled Self-Improvement

## Scope

Allow the agent to propose and implement approved improvements without granting itself more power.

## Non-Goals

No policy weakening, audit disabling, personal-data permission grants, persistence creation, sending, or package installation without approval.

## Requirements

- `improve --propose`
- `improve --implement "<approved feature>"`
- `improve --run-tests`
- `improve --show-diff`
- `improve --commit` with approval.
- Branch-based changes.
- Feature proposal JSON format.

## Risks

- Safety regression.
- Hidden persistence.
- Dependency supply-chain risk.
- Undetected policy modifications.

## Tests

- Proposal does not edit files.
- Implementation creates branch.
- Policy reduction blocked.
- Audit disabling blocked.
- Tests run.
- Diff shown.
- Commit requires approval.

## Approval Gate

Requires M1-M5 complete and explicit user approval.
