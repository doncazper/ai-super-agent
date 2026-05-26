# Hermes-Inspired Safe Autonomy Decision

Status: Accepted for planning and policy scaffolding only.

Date: 2026-05-25

## Context

The project already has a safety control plane: ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, command registry tracking, prompt tracking, scheduler guardrails, native skill vetting, Brain Runtime provider scaffolds, and platform/app bridge boundaries. The Hermes-inspired track may borrow useful product ideas such as channels, mobile access, repeated-task learning, isolated helpers, model continuity, memory search, and better scheduler UX.

The project must not copy unsafe autonomy patterns. In particular, this decision forbids risky unattended operation, uncontrolled browser automation, background persistence, personal-data access, send/write actions, cloud/private data execution, and anti-bot bypass work unless a later explicit prompt, policy review, tests, and release gate approve a narrow safe design.

## Decision

The Hermes-inspired track is approved as a safe groundwork track. It may add documentation, metadata-only registries, disabled-by-default scaffolds, local proposal workflows, and mock/dogfood/eval coverage.

It must not enable high-risk autonomy by default. Runtime execution remains governed by ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger. Channels, subagents, schedulers, skill proposals, memory continuity, model switching, and sandbox backends are not authority surfaces; they are request or metadata surfaces until brokered execution approves a specific action.

## Safe Groundwork

The approved groundwork tracks are:

1. Gateway/channel process.
2. Telegram/mobile access scaffolding.
3. Repeated-task skill creation proposals.
4. Skill improvement from experience.
5. Scheduler UX for safe automations.
6. Subagent isolation groundwork.
7. Sandbox backend abstraction.
8. Model switching and session continuity.
9. Long-term memory search.
10. Cross-session continuity.

## Hard Boundary

Unauthorized CAPTCHA, Cloudflare, anti-bot, proxy-evasion, login-wall, paywall bypass, and human impersonation against third-party sites are forbidden.

Allowed future work is limited to documented, authorized, disabled-by-default flows such as:

- Official APIs.
- OAuth.
- User-in-the-loop manual login steps.
- Official test keys or staging environments.
- Approved first-party or contracted test environments.
- Approved partner access.

Even authorized flows require explicit scope, audit, tests, setup gates, provider limits, and disabled-by-default behavior.

## Consequences

- This track can improve ergonomics and planning without creating dangerous autonomy.
- High-risk features remain deferred until specific release gates exist.
- User-facing maturity must stay conservative: documentation-only work is `Specified`, not user-ready.
- Any future executable capability must be declared in the capability manifest before execution and must map through ToolBroker.

## Non-Goals

- No unattended high-risk workflows.
- No arbitrary browser automation.
- No background persistence.
- No personal-data tools.
- No message/email/calendar/contact send or write behavior.
- No anti-bot or CAPTCHA bypass.
- No cloud/server private-data access.
- No subagent write permissions by default.
