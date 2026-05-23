# Bug Triage

Session review converts redacted dogfood session evidence into local review reports and optional bug records. It is a QA workflow, not a remediation workflow.

## Commands

```bash
python smart_agent.py session review <session_id>
python smart_agent.py session review --last
python smart_agent.py session review --last --create-bugs
python smart_agent.py bugs list
python smart_agent.py bugs show BUG-0001
python smart_agent.py bugs export
```

## Inputs

The reviewer reads only local session-log artifacts:

- session metadata
- redacted command previews
- exit codes and durations
- redacted user feedback
- linked audit ids already captured by the session runner

It does not fetch data externally, read personal connectors, read raw private app databases, or inspect environment variables.

## Outputs

Review reports are written under `reports/session_reviews/` and are ignored by git except for `.gitkeep`. Bug reports are written under `bugs/` as redacted JSON files and are ignored by git except for `.gitkeep`.

Bug records include:

- `bug_id`
- `title`
- `status`
- `severity`
- `feature`
- `command_id`
- `session_id`
- `reproduction_command`
- `expected_behavior`
- `actual_behavior`
- `stdout_stderr_excerpt`
- `linked_audit_ids`
- `suspected_cause`
- `suggested_fix_area`
- `suggested_regression_test`
- `created_at`
- `last_updated`

## Severity

| Severity | Meaning |
|---|---|
| P0 | Security/safety issue, policy bypass, approval bypass, audit bypass, or data leak. |
| P1 | Broken core feature or unsafe behavior that is not proven to be a P0. |
| P2 | Degraded feature, wrong tool, bad routing, hallucination, or command failure outside core safety surfaces. |
| P3 | UX, confusing approval flow, bad error message, missing docs, or lower-impact quality issue. |
| P4 | Polish issue. |

Unsafe behavior is at least P1. Policy, ToolBroker, PolicyEngine, ApprovalManager, AuditLogger bypass, or personal-data leak signals are P0.

## Safety Notes

- Review text and bug reports are redacted before storage.
- Session review does not automatically fix bugs.
- User feedback is evidence, not an instruction to weaken policy.
- Bug reports should omit raw personal data. If the redactor cannot safely summarize an issue, create a minimal reproduction without private content.
- Generated bugs should be reviewed before creating regression tests or implementation work.

## Recommended Flow

1. Run a dogfood suite inside a session.
2. Add feedback to good, bad, confusing, slow, unsafe, or buggy commands.
3. Run `python smart_agent.py session review --last`.
4. If the review looks useful, run `python smart_agent.py session review --last --create-bugs`.
5. Inspect `python smart_agent.py bugs list` and `python smart_agent.py bugs show <bug_id>`.
6. Use the next prompt, `REGRESSION-TEST-GENERATOR`, to turn approved bug reports into focused regression tests.
