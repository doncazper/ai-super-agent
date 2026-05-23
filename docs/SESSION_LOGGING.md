# Live Session Logging and Replay

Session logging records manual dogfooding runs: which commands were tried, what happened, where failures appeared, and which audit identifiers were visible. It is separate from the security audit log.

- Audit log: policy decisions, denials, approvals, executions, and failures.
- Session log: user-facing command attempts, redacted output previews, feedback/bug counters, and replay material for debugging.

## Commands

```bash
python smart_agent.py session start --name "core-smoke"
python smart_agent.py session status
python smart_agent.py session run -- --no-tools "Explain RCS vs iMessage"
python smart_agent.py session run -- weather current "Phoenix, AZ"
python smart_agent.py session replay --last
python smart_agent.py session review --last
python smart_agent.py session review --last --create-bugs
python smart_agent.py session show <session_id>
python smart_agent.py session export <session_id>
python smart_agent.py session end
python smart_agent.py session list
python smart_agent.py session last
```

`session run -- ...` executes a `smart_agent.py` command and appends redacted stdout/stderr previews to the active session. It does not create a new tool execution path; delegated commands keep their existing ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger behavior.

## Feedback Capture

During or after a dogfood session, attach redacted feedback to the last command or to a specific command id:

```bash
python smart_agent.py feedback good --last
python smart_agent.py feedback bad --last --reason "too vague"
python smart_agent.py feedback bug --last --title "weather command crashed"
python smart_agent.py feedback confusing --last --reason "approval wording was unclear"
python smart_agent.py feedback slow --last --reason "took too long"
python smart_agent.py feedback unsafe --last --reason "looked like private data leaked"
python smart_agent.py feedback rate --last --score 4
python smart_agent.py feedback add <command_id> --tag poor_response --note "missed citation"
python smart_agent.py feedback list --session <session_id>
python smart_agent.py feedback export --session <session_id>
```

Feedback is stored in `feedback.jsonl` inside the session directory. Feedback text is redacted for secrets, email addresses, and phone numbers before storage. Unsafe feedback is automatically marked higher severity. Feedback is review data only; it is not treated as an instruction to weaken policy, grant permissions, send messages, or change tool behavior.

Supported tags:

`poor_response`, `wrong_tool`, `missing_tool`, `bad_routing`, `hallucination`, `no_citation`, `bad_error_message`, `command_failed`, `command_hung`, `approval_confusing`, `unsafe_behavior`, `too_slow`, `UX_confusing`, `docs_gap`, `test_gap`.

## Session Review and Bugs

After a session has command records and feedback, create a structured review:

```bash
python smart_agent.py session review --last
python smart_agent.py session review <session_id>
python smart_agent.py session review --last --create-bugs
python smart_agent.py bugs list
python smart_agent.py bugs show BUG-0001
python smart_agent.py bugs export
```

Session review summarizes pass/fail counts, feedback tags, repeated failure patterns, tool/routing failures, poor response flags, confusing UX, approval friction, missing docs, suspected bugs, and suggested regression tests. It reads redacted session previews and feedback records only. `--create-bugs` writes redacted local bug records under `bugs/`; it does not fix bugs, open network calls, access personal connectors, or write memory. See `docs/BUG_TRIAGE.md`.

## Storage

Default path: `reports/sessions/`.

Each session stores:

- `session.json` for session metadata.
- `commands.jsonl` for command records.
- `feedback.jsonl` for redacted command feedback.
- `outputs/<command_id>.txt` for redacted combined output.

Raw session outputs are ignored by git through `.gitignore`; only `reports/sessions/.gitkeep` is intended to be committed.

Session review reports under `reports/session_reviews/` and generated bug JSON under `bugs/` are local QA artifacts and are also ignored by git except for `.gitkeep` placeholders.

## Redaction

By default, session logs redact:

- API keys, bearer tokens, passwords, and secret-looking tokens.
- Email addresses.
- Obvious U.S. phone numbers.

The recorder does not capture environment variables. Raw logging is off by default and requires the explicit `--unsafe-raw` flag on `session run`; do not use that mode for personal-data, credential, or approval-gated sessions.

## Privacy Boundaries

Session logs must not store raw email, message, calendar, or contact contents. Personal-data connector commands remain disabled by default and approval-gated. If a personal-data command is wrapped by `session run`, the session recorder stores only redacted output previews and any separate connector/tool policy still applies.

## Replay

Replay is designed for bug reports and morning reviews:

```bash
python smart_agent.py session replay --last
python smart_agent.py session export <session_id>
```

Use replay output to identify failing commands, regression candidates, and missing docs/tests. Do not paste unredacted personal data into bug reports.
