# Manual Validation Plan

Prompt ID: `MATURITY-AUDIT-01`
Date: 2026-05-25

Use `./.venv/bin/python` for Python commands. Do not use live providers, personal-data connectors, paid APIs, sends/writes, or background services unless a command is explicitly a safe doctor and the relevant provider is intentionally configured.

## Safe Daily Smoke Commands

```bash
./.venv/bin/python --version
./.venv/bin/python smart_agent.py doctor
./.venv/bin/python smart_agent.py commands validate
make policy-check
./.venv/bin/python -m pytest -q tests/test_productization_audit_docs.py
```

## Weekly Full Dogfood Commands

```bash
./.venv/bin/python -m pytest -q
./.venv/bin/python smart_agent.py commands validate
make policy-check
./.venv/bin/python smart_agent.py dogfood list
./.venv/bin/python smart_agent.py eval list
```

If the repo exposes safe all-session dogfood commands, run them only with local/mock providers and record the resulting report path in `docs/COMPLETION_REPORT.md`.

## Provider-Specific Live Validation

- Weather: run current/forecast commands only against free configured providers and record retrieved provider, timestamp, and failures.
- Web: run provider doctors first; run safe public URL fetch only through the brokered web commands; do not bypass robots, paywalls, login walls, CAPTCHA, or anti-bot systems.
- News: runtime news providers are not implemented yet; validate docs/manifest/status only until `news-provider-registry-status-commands` completes.
- Reddit: run `reddit doctor` or `connectors status reddit` only if configured; do not fetch posts/comments unless an explicit safe live validation prompt authorizes it.
- V2EX/Chinese forums: use public API/fixtures first; report blocked/login/CAPTCHA pages as unavailable.
- Brain/runtime: run provider health checks only for local configured runtimes; do not call paid/cloud APIs by default.

## Prompt Tracker Tests

```bash
./.venv/bin/python smart_agent.py prompts audit
./.venv/bin/python smart_agent.py work status
```

If a prompt tracker command is unavailable, record `Not available` and use file evidence from `docs/PROMPT_LEDGER.md`, `docs/PROMPT_QUEUE.md`, `docs/PROMPT_AUDIT.md`, and `prompts/`.

## Native Skill Tests

```bash
./.venv/bin/python smart_agent.py skills list
./.venv/bin/python smart_agent.py skills conflicts
./.venv/bin/python smart_agent.py skills docs-check
```

Do not install, execute, or enable external skills during manual validation.

## Apple / Platform Tests

```bash
./.venv/bin/python smart_agent.py platform doctor
./.venv/bin/python smart_agent.py platform status
./.venv/bin/python smart_agent.py platform capabilities
./.venv/bin/python smart_agent.py platform matrix
```

These commands must remain read-only and must not access personal data or import heavy native frameworks.

## Failure Signals

- Any secret appears unredacted in logs, reports, docs, or command output.
- A personal-data connector is enabled by default.
- A HIGH or CRITICAL action proceeds without ApprovalManager evidence.
- A send/write command bypasses Action Center or exact preview matching.
- A provider uses paid APIs in free-first mode.
- A web/fetch/news/forum command bypasses robots, paywalls, login walls, CAPTCHA, or anti-bot protections.
- A prompt tracker marks a prompt complete without code/test/docs/completion evidence.

## Feedback And Bug Logging

1. Capture the command, timestamp, expected behavior, actual behavior, and redacted output.
2. Add a bug under `bugs/` or use the existing bug generator if safe.
3. Link the bug in `docs/COMPLETION_REPORT.md` and `docs/PROJECT_STATE.md`.
4. Add or request a regression test before marking the issue closed.

