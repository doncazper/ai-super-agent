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
python smart_agent.py dogfood plan
python smart_agent.py dogfood next
python smart_agent.py dogfood checklist
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
- `internet_core`: mock-safe internet provider metadata, provider-decision, cache status, and router explain checks.
- `web_providers`: config-only SearXNG/Brave/SerpAPI doctor and fallback-policy checks; no provider calls.
- `web_research`: default-disabled internet research workflow checks; live provider use is configuration-dependent.
- `web_fetch`: default-disabled selected-URL fetch checks; requires public network access for live runs.
- `web_blocked_sources`: default-disabled blocked/unavailable source checks for CAPTCHA/block/robots/prompt-injection fixtures.
- `workspace_files`: writes only under `./workspace/dogfood`.
- `memory`: uses synthetic `dogfood` memory scope.
- `approvals`: exercises dry-run/queue paths without executing risky operations.
- `native_skills`: vets local synthetic fixtures only.
- `personal_dry_run`: preflight only; no real personal-data connector reads. It includes Messages draft/handoff preflight checks for `messages draft`, `messages handoff`, and `messages draft-from-text`; these checks must not send, read Messages databases, write memory, or copy to clipboard.
- `messaging_core`: default-disabled messaging foundation suite for channel listing, local draft creation, draft validation, send-action proposal creation, and Action Center approval-preview review.
- `messaging_handoff`: default-disabled safe handoff suite using `./workspace/dogfood/message_thread.txt`, fixed local draft ids, save/copy approval-required checks, and handoff instructions.
- `messaging_ios_compose`: default-disabled local iOS compose payload suite that records mock returned results; it does not open an iOS app or silently send.
- `messaging_macos_probe`: default-disabled macOS Messages metadata probe suite; it excludes live-send probes and never accesses `~/Library/Messages`.
- `messaging_send_dry_run`: default-disabled send-gate suite using local drafts and preflight-only send checks; it does not approve or execute sends.
- `lead_response`: default-disabled mock Lead Inbox suite for Apple Business mock inbound, classify, summarize, draft response, follow-up suggestion, and send-action preflight.
- `reddit_core`: default-disabled Reddit diagnostics and setup-gated read-only checks; live API content reads occur only when Reddit is explicitly configured.
- `reddit_research`: default-disabled Reddit source-grounding suite for summaries, consensus, pros/cons, prompt-injection-like comments, and deleted/removed comment handling.
- `forum_multilingual`: default-disabled local multilingual forum suite for Chinese detection, generated translation labels, glossary extraction, source references, and setup-gated cross-language research.
- `v2ex`: default-disabled V2EX read-only connector suite; doctor is config-only and topic/latest/reply reads require explicit V2EX configuration.
- `chinese_forum_discovery`: default-disabled Chinese forum discovery suite for approved site-filter search, selected public fetch, unavailable source reporting, and optional local translation.

Messaging suites are intentionally not part of `all_safe` yet. Run them under a session after reviewing the suite with `dogfood show`, and keep live send probes out of routine dogfood:

```bash
python smart_agent.py dogfood show messaging_core
python smart_agent.py dogfood run messaging_core --dry-run
python smart_agent.py session start --name messaging-dogfood
python smart_agent.py dogfood run messaging_core --session
python smart_agent.py dogfood run messaging_handoff --session
python smart_agent.py dogfood run messaging_ios_compose --session
python smart_agent.py dogfood run messaging_macos_probe --session
python smart_agent.py dogfood run messaging_send_dry_run --session
python smart_agent.py dogfood run lead_response --session
python smart_agent.py session review --last
python smart_agent.py session end
```

Do not run `messages macos live-send-probe` during default dogfood. That command remains a separate CRITICAL approval-gated manual validation path.

Forum suites are also kept out of `all_safe` because several checks are provider/network/setup-gated. Review and dry-run them first:

```bash
python smart_agent.py dogfood show reddit_core
python smart_agent.py dogfood run reddit_core --dry-run
python smart_agent.py dogfood run reddit_research --dry-run
python smart_agent.py dogfood run forum_multilingual --dry-run
python smart_agent.py dogfood run v2ex --dry-run
python smart_agent.py dogfood run chinese_forum_discovery --dry-run
python smart_agent.py eval run --forums
```

See `docs/forums/FORUM_DOGFOOD_RUNBOOK.md` for the full Forum Intelligence runbook.

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

Messaging suites also include expected safe failures, such as denied bulk recipients and expired iOS compose payloads. Treat those as pass conditions only when the output clearly refuses the unsafe path and records no send.

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

## Daily And Weekly Workflow

Use the live runbook commands to choose the next manual validation step:

```bash
python smart_agent.py dogfood plan
python smart_agent.py dogfood next
python smart_agent.py dogfood checklist
```

`dogfood plan` prints the daily safe smoke, weekly deeper check, available suites, and safety rules. `dogfood next` inspects the latest session metadata and dogfood maturity notes to suggest the next safe step. `dogfood checklist` prints checklist entries suitable for copying into a manual QA note.

See:

- `docs/dogfood/LIVE_TEST_RUNBOOK.md`
- `docs/dogfood/DAILY_DOGFOOD_CHECKLIST.md`
- `docs/dogfood/WEEKLY_RELEASE_CHECK.md`
- `docs/templates/dogfood_session_notes.md`
