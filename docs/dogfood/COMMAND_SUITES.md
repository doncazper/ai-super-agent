# Dogfood Command Suites

Suite files live in `dogfood_suites/` and are loaded as data.

## Suite Schema

```yaml
suite_id: all_safe
name: All Safe Dogfood Subset
description: Safe subset of routine manual QA checks.
risk_level: LOW
requires_live_lmstudio: false
requires_web: true
requires_personal_data: false
default_enabled: true
commands:
  - id: safe_doctor
    description: Run doctor diagnostics.
    command: python smart_agent.py doctor
    expected_behavior: Runtime readiness is shown without personal-data reads.
    failure_signals: Startup validation failure or secret leakage.
    tags: [core, doctor]
    expected_exit_codes: [0]
```

Required command fields:

- `id`
- `description`
- `command`
- `expected_behavior`
- `failure_signals`
- `tags`

Optional command fields:

- `expected_exit_codes`: defaults to `[0]`.

## Current Suites

| Suite | Risk | Live LM Studio | Web | Personal data | Default | Purpose |
|---|---|---:|---:|---:|---:|---|
| `core` | LOW | yes | no | no | yes | Core runtime, no-tool chat, time tool, doctor, status, tools, config, preflight. |
| `weather` | LOW | no | yes | no | yes | Weather doctor, current, forecast, bad location, cache, alerts. |
| `web` | LOW | no | yes | no | yes | Research, safe URL fetch, blocked URL behavior, source-grounding, provider status. |
| `internet_core` | LOW | no | no | no | yes | Mock-safe web provider registry, provider-decision, cache status, and router explain checks. |
| `web_providers` | LOW | no | no | no | yes | Config-only SearXNG, Brave, SerpAPI doctor/status and free-first fallback checks. |
| `web_research` | MEDIUM | no | yes | no | no | Current/stable routing and source-grounded research behavior with provider setup outcomes. |
| `web_fetch` | MEDIUM | no | yes | no | no | Selected-URL fetch safety, blocked/private URL denial, binary block, and invalid URL handling. |
| `web_blocked_sources` | MEDIUM | no | yes | no | no | CAPTCHA/block-page, robots, private source, and prompt-injection routing fixtures. |
| `workspace_files` | MEDIUM | no | no | no | yes | Workspace list/read/summarize/write/patch and traversal denial. |
| `memory` | LOW | no | no | no | yes | Synthetic project-fact memory add/search/export/clear and secret refusal. |
| `approvals` | MEDIUM | no | no | no | yes | Preflight approval checks and safe queue/denial paths. |
| `native_skills` | LOW | no | no | no | yes | Skill registry, validation, finder, and safe/risky vetter fixtures. |
| `personal_dry_run` | LOW | no | no | no | no | Preflight-only personal connector dry-runs. |
| `all_safe` | LOW | no | yes | no | yes | Routine safe subset for first dogfood session. |
| `messaging_core` | MEDIUM | no | no | no | no | Channel-neutral messaging metadata, local draft, draft validation, send-action proposal, and Action Center preview checks. |
| `messaging_handoff` | MEDIUM | no | no | no | no | Workspace fixture draft-from-text, fixed local draft handoff, save/copy approval-required checks, and handoff instructions. |
| `messaging_ios_compose` | MEDIUM | no | no | no | no | Local iOS compose handoff payloads, status, mock returned results, and expiry rejection; no iOS app or silent send. |
| `messaging_macos_probe` | LOW | no | no | no | no | Metadata-only macOS Messages feasibility probe and disabled send-adapter status; live-send probe excluded. |
| `messaging_send_dry_run` | MEDIUM | no | no | no | no | Local send-action and preflight-only send-gate checks, denied bulk recipient, and approval-reuse expectations. |
| `lead_response` | MEDIUM | no | no | no | no | Mock Lead Inbox and Apple Business local lead response drafting, follow-up suggestion, and send-action preflight. |
| `reddit_core` | MEDIUM | no | yes | no | no | Reddit doctor/status, setup-gated search/post checks, cache status, and retention status. Live API reads occur only when explicitly configured. |
| `reddit_research` | MEDIUM | no | yes | no | no | Reddit summary/consensus/pros-cons fixtures for source grounding, deleted/removed handling, and prompt-injection resistance. |
| `forum_multilingual` | MEDIUM | no | no | no | no | Chinese detection, local-model translation labeling, glossary extraction, source-reference preservation, and setup-gated multilingual forum research. |
| `v2ex` | MEDIUM | no | yes | no | no | V2EX doctor plus setup-gated read-only latest/topic/reply checks through the documented API only. |
| `chinese_forum_discovery` | MEDIUM | no | yes | no | no | Chinese forum provider/site-filter discovery, blocked/unavailable source reporting, selected public fetch, and optional local translation checks. |

## Updating Suites

When adding or changing a suite:

1. Keep commands as `python smart_agent.py ...`.
2. Add expected behavior and failure signals.
3. Avoid personal-data reads by default.
4. Add or update tests in `tests/test_dogfood_suites.py`.
5. Update `docs/COMMAND_REGISTRY.md`, `docs/FEATURE_MATURITY.md`, `docs/PROJECT_STATE.md`, and `docs/COMPLETION_REPORT.md`.

Messaging-specific suites must remain default-disabled until the messaging release gate passes. They may create local drafts, local mock leads, pending Action Center items, or redacted session evidence, but they must not approve actions, execute sends, run `messages macos live-send-probe`, read private Messages databases, request Full Disk Access, or rely on real personal data.

Forum-specific suites are default-disabled and remain mock/setup-gated by default. They must not scrape Reddit or Chinese platforms, use login cookies or browser sessions, bypass CAPTCHA/anti-bot systems or robots, use paid providers by default, post/comment/vote/DM, write forum content to memory, train on forum content, or expose raw cached author/query/body data. Run `eval run --forums` for fixture-backed checks before any live provider validation.
