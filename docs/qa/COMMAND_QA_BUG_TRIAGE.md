# Command QA Bug Triage

Command QA bug triage turns redacted QA run records into local bug reports and regression scaffolds.

Commands:

```bash
python smart_agent.py qa results rank --last
python smart_agent.py qa bugs create --from-run <run_id>
python smart_agent.py qa bugs create --from-report <report_id>
python smart_agent.py qa regressions create --from-bug <bug_id>
python smart_agent.py qa regressions create --from-run <run_id>
```

Safety rules:

- Bug reports use redacted stdout/stderr excerpts only.
- Personal-looking data and common secret tokens are redacted again before writing.
- Generated regressions are skipped scaffolds until a human converts them into concrete fixture-backed assertions.
- The triage layer never marks bugs fixed automatically.
- The triage layer does not run commands, apply patches, install packages, or call providers.

Severity ranking:

- `P0`: policy, approval, audit, redaction, security, or data-leak signals.
- `P1`: core/runtime command not found, import, or exception failures.
- `P2`: feature command failures, timeout, provider setup failures, or unknown failures.
- `P3`: UX/docs/help/command registry mismatch.
- `P4`: polish, flaky, or noise.

