# Frontend and Channel State Boundary

Status: CANON-03 contract.

Frontends may display status, submit request envelopes, and display redacted results. They may not execute shell commands, tools, providers, approvals, or policy mutations directly.

## Current Frontend

- CLI: current first frontend and compatibility baseline.

## Future Frontends

- local app
- iOS companion
- Windows app
- web dashboard
- external channels

Future frontends must call gateway/kernel service methods and receive redacted summaries. They cannot self-approve generated actions.
