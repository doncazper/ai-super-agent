# Manual Dogfood Guide

Manual dogfood suites are curated terminal command lists for exercising real features in a repeatable way. They are QA artifacts, not new agent capabilities.

## Safety Rules

- Suites do not enable personal-data tools.
- Personal-data suites use dry-run or preflight only by default.
- Suites do not send email or messages.
- Suites do not write calendar or contact data.
- Suite commands are constrained to `python smart_agent.py ...`.
- Commands keep their normal ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger behavior.
- `dogfood run --session` requires an active session log and stores redacted output.

## Commands

```bash
python smart_agent.py dogfood list
python smart_agent.py dogfood show all_safe
python smart_agent.py dogfood run all_safe --dry-run
python smart_agent.py dogfood run all_safe
python smart_agent.py session start --name dogfood-all-safe
python smart_agent.py dogfood run all_safe --session
python smart_agent.py feedback good --last
python smart_agent.py feedback bad --last --reason "too vague"
python smart_agent.py session review --last
python smart_agent.py session end
```

## First Recommended Session

Start with the safe subset:

```bash
python smart_agent.py session start --name dogfood-all-safe
python smart_agent.py dogfood run all_safe --session
python smart_agent.py feedback rate --last --score 4
python smart_agent.py session replay --last
python smart_agent.py session review --last
python smart_agent.py session end
```

If LM Studio is not configured, use `dogfood show core` first and skip `core_no_tool_chat`/`core_time_tool` manually until `LMSTUDIO_MODEL` is set.

## Suite Selection

- `all_safe`: default first pass across core diagnostics, weather, web status, workspace files, memory, and native skills.
- `core`: includes no-tool chat and time-tool smoke; requires live LM Studio.
- `weather`: requires web access for live provider calls.
- `web`: requires web/search/fetch provider configuration for full success.
- `workspace_files`: writes only under `./workspace/dogfood`.
- `memory`: uses synthetic `dogfood` memory scope.
- `approvals`: exercises dry-run/queue paths without executing risky operations.
- `native_skills`: vets local synthetic fixtures only.
- `personal_dry_run`: preflight only; no real personal-data connector reads.

## Failure Handling

`dogfood run` continues through failures and prints a structured summary. A failed command means the manual QA reviewer should inspect:

- `exit_code`
- `stdout_preview`
- `stderr_preview`
- `expected_behavior`
- `failure_signals`
- linked session replay if `--session` was used
- feedback records from `python smart_agent.py feedback list --session <session_id>`

Some suites include expected safe failures, such as bad locations or denied path traversal. Those commands declare `expected_exit_codes` in the suite YAML.

## Marking Feedback

Use feedback capture while the session is fresh:

```bash
python smart_agent.py feedback good --last
python smart_agent.py feedback confusing --last --reason "I could not tell whether it ran tools"
python smart_agent.py feedback unsafe --last --reason "It appeared to expose private data"
python smart_agent.py feedback add <command_id> --tag docs_gap --note "README needs this setup hint"
```

Feedback is redacted before storage and appears in `session show`, `session replay`, and `feedback list`. It is review evidence only; it does not grant approvals, weaken policy, or automatically create implementation work.

## Reviewing a Session

Run `python smart_agent.py session review --last` after marking feedback. The review report groups command failures, feedback tags, routing/tool issues, UX confusion, approval friction, docs gaps, suspected bugs, and suggested regression tests.

If the review looks useful, run:

```bash
python smart_agent.py session review --last --create-bugs
python smart_agent.py bugs list
```

Generated bugs are local redacted triage records. They do not automatically change code or weaken policy; review them before using the regression-test generator.
