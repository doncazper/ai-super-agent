# Hermes-Inspired Safe Autonomy Maturity Review

Date: 2026-05-25

This review classifies the Hermes-inspired safe autonomy track conservatively. Local tests and fixture gates count as `Tested`; they do not count as `Live-Validated` or `User-Ready`.

## Summary

Overall maturity: `4 Tested`.

Overall readiness score: 70/100.

The track is safe to rely on as a bounded groundwork layer for future prompts. It is not safe to rely on as autonomous execution. The implemented surfaces are metadata, preview, proposal, dry-run, mock, fixture, or docs-only by design.

## Maturity Matrix

| Capability Area | Classification | Rationale |
|---|---|---|
| Gateway/channel process | Tested | Brokered metadata commands and gateway guards have tests; no external channel runtime exists. |
| Telegram/mobile access scaffolding | Tested | Disabled-by-default diagnostics and config policy have tests; no bot, webhook, polling, pairing, or approval executor exists. |
| Skill creation from repeated tasks | Tested | Proposal-only flow has tests and redacted report behavior; no skill creation/import/enablement/execution exists. |
| Skill improvement from experience | Tested | Evidence-backed proposal-only flow has tests; no skill edits, lockfile updates, or self-modification exists. |
| Scheduler UX | Tested | Preview/dry-run/review commands have tests; no background runner or unattended high-risk execution exists. |
| Subagent isolation | Tested | Mock profiles and isolation policy have tests; no real subagent runner exists. |
| Sandbox backend abstraction | Tested | Mock backend and planned backend metadata have tests; no executable sandbox exists. |
| Model switching | Tested | Dry-run switch metadata and compatibility checks have tests; no persistent/default provider switch exists. |
| Long-term memory search | Tested | Brokered continuity/context preview helpers have tests; no cloud embeddings or personal memory injection by default exists. |
| Cross-session continuity | Tested | Redacted status/export/summary helpers have tests; no separate persistent continuity profile exists. |
| Authorized web automation boundary | Specified | Docs and planned command tracking exist; no browser automation or deep-scan runtime exists. |
| Safe autonomy dogfood/evals | Tested | Dogfood suites and fixture-backed eval category have tests; live/manual validation remains pending. |
| High-risk autonomy gates | Specified | Gates are documented and enforced as future prerequisites; they do not implement high-risk features. |

## Evidence

- Focused release-gate tests: 74 passed.
- Safe autonomy eval: 4 passed, 0 failed, 5 personal-data skips.
- Safe autonomy dogfood dry-run: status `ok`, 9 previewed/skipped commands, 0 failed.
- Command registry validation: 484 commands, no problems.
- Startup policy and capability manifest validation: passed via `make policy-check`.
- Full suite: 1380 passed, 1 skipped after one command-registry docs-link fix.

## Conservative Limits

- No feature in this track is `Live-Validated`.
- No feature in this track is `User-Ready` for autonomy execution.
- No feature in this track is a `Mature Pattern` for high-risk autonomy.
- `Authorized web automation boundary` and `High-risk autonomy gates` remain `Specified` because they are policy/docs gates, not implementations.

## Forbidden Or Deferred

- Automatic skill creation or automatic skill modification.
- Hidden background persistence, cron, LaunchAgents, daemons, polling loops, or webhooks.
- Unattended HIGH or CRITICAL workflows.
- Cross-platform messaging sends or write actions.
- Subagent write permissions by default.
- Arbitrary sandbox execution, browser sandbox execution, Docker/VM/Firecracker/cloud sandbox execution.
- Browser automation for third-party targets.
- CAPTCHA, Cloudflare, anti-bot, proxy-evasion, login-wall, paywall, cookie/session, or stealth bypass.
- Cloud/server execution over private data.

## Next Work

Recommended next track: return to the standing queue with `news-provider-registry-status-commands`, unless the user wants another release-hardening pass first.
