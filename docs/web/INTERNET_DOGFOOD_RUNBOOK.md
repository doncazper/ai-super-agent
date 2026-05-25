# Internet Dogfood And Eval Runbook

Status: local/mock-first release gate added on 2026-05-24.

## Scope

This runbook validates the Internet Access track across provider policy, safe fetch behavior, source-grounded research, blocked/unavailable sources, and fixture-backed eval checks. It is designed to prove that internet features stay brokered, audited, source-aware, and conservative before any live provider expansion.

## Non-Goals

- No paid provider use by default.
- No CAPTCHA, paywall, login-wall, robots, Cloudflare, or anti-bot bypass.
- No browser automation.
- No search history or full article body memory writes by default.
- No personal-data connectors.

## Dogfood Suites

| Suite | Default | Live Network | Purpose |
|---|---:|---:|---|
| `internet_core` | yes | no | Provider registry, provider decision, cache status, and router explain. |
| `web_providers` | yes | no | SearXNG, Brave, SerpAPI doctor/status and fallback policy. |
| `web_fetch` | no | yes | Selected-URL fetch safety, blocked domains, binary blocks, and invalid URLs. |
| `web_research` | no | optional | Research routing, no-fetch source grounding, and provider setup behavior. |
| `web_blocked_sources` | no | optional | CAPTCHA/block fixtures, robots handling, and prompt-injection routing. |

Mock-first commands:

```bash
python smart_agent.py dogfood run internet_core --dry-run
python smart_agent.py dogfood run web_research --dry-run
python smart_agent.py dogfood run web_providers --dry-run
python smart_agent.py dogfood run web_fetch --dry-run
python smart_agent.py dogfood run web_blocked_sources --dry-run
```

Session-backed manual runs:

```bash
python smart_agent.py session start --name internet-release-gate
python smart_agent.py dogfood run internet_core --session
python smart_agent.py dogfood run web_research --session
```

Run `web_fetch` and `web_blocked_sources` only when live public web checks are acceptable for the release pass.

## Eval Gate

The internet eval category is fixture-backed. It does not call live providers.

```bash
python smart_agent.py eval run --internet
python smart_agent.py eval report --internet
```

Checks covered:

- no fabricated citations
- source list present
- `retrieved_at` present
- failed fetches reported separately from citations
- prompt injection ignored
- provider policy respected
- paid provider not used by default
- no query history or web content persisted by default
- network domains present in audit fixtures

## Release Gate

Run:

```bash
./.venv/bin/python -m pytest
./.venv/bin/python smart_agent.py dogfood run internet_core --dry-run
./.venv/bin/python smart_agent.py dogfood run web_research --dry-run
./.venv/bin/python smart_agent.py eval run --internet
./.venv/bin/python smart_agent.py eval report --internet
./.venv/bin/python smart_agent.py commands validate
```

Also validate startup policy, capability manifest, docs, no anti-bot bypass code, paid-provider defaults, ToolBroker routing, and network-domain audit behavior.

## Live Provider Rules

Safe live tests are opt-in and only run when providers are configured. SearXNG must use a configured instance. Brave and SerpAPI require explicit paid/quota policy allowance and must never become the free-first default.

## Known Limitations

- Internet evals are fixture-backed; they do not prove a live provider account is healthy.
- Live fetch dogfood depends on public network availability and should be treated as manual QA evidence.
- Dogfood suites validate command behavior and safety posture; they do not replace unit tests.
