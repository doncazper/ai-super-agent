# Test Plan

## Unit Tests

- Policy decisions.
- Tool broker execution and denial.
- LM Studio request payload construction.
- Audit entry redaction and hash chaining.
- Tool argument validation.

## Integration Tests

- No-tool chat sends no tools.
- Tool-call loop appends matching tool results.
- CLI modes construct expected orchestration options.

## Policy Tests

- Unknown capabilities denied.
- SAFE actions allowed.
- HIGH actions ask approval.
- CRITICAL actions require per-action approval.
- FORBIDDEN actions denied.

## Approval Tests

- Approval required when policy returns `ASK`.
- Denial prevents execution.
- Critical actions do not reuse approvals.

## Audit-Log Tests

- Executions are logged.
- Denials are logged.
- Approval results are logged.
- Hash chain links entries.
- Secrets are redacted.

## Prompt-Injection Tests

- Webpage instructions are ignored.
- Email/message instructions are ignored.
- Document instructions are ignored.

## Personal-Data Tests

- Personal modules disabled by default.
- Selected-scope reads require approval.
- Body text is not stored in long-term memory by default.

## Self-Improvement Tests

- Proposal mode does not edit files.
- Implementation creates a branch.
- Policy weakening and audit disabling are blocked.
- Tests and diffs are produced before commit.

## Release-Gate Tests

- All selected milestone tests pass or failures are documented.
- Forbidden capabilities are absent.
- Audit and policy checks pass.
