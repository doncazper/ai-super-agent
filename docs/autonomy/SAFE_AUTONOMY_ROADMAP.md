# Safe Autonomy Roadmap

This roadmap defines a safe Hermes-inspired track. It is a planning document; it does not enable new runtime autonomy.

## Principles

- Safety controls are authority: ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, and AuditLogger remain mandatory.
- Autonomy starts as proposal, preview, and metadata, not execution.
- HIGH and CRITICAL actions cannot run unattended.
- Personal-data tools remain disabled by default.
- Channels and subagents cannot grant themselves tools, approvals, persistence, or policy exceptions.
- Background persistence requires a future decision record and release gate.
- Browser automation requires an authorized, narrow, user-visible scope and cannot include anti-bot bypass.

## Track Order

| Order | Track | Safe v1 Output | Explicitly Deferred |
|---:|---|---|---|
| 1 | Gateway/channel process | Channel-neutral request and response metadata, status commands, policy docs | Remote exposure, sends, background listeners |
| 2 | Telegram/mobile access | Disabled-by-default config and setup diagnostics | Real bot polling/webhooks, message sends |
| 3 | Repeated-task skill creation proposals | Local proposal records for repeated safe tasks | Automatic skill creation or enablement |
| 4 | Skill improvement from experience | Evidence-backed improvement proposals | Self-modifying skills or automatic updates |
| 5 | Scheduler UX | Safer previews, dry-run plans, next-action guidance | Hidden background runners and unattended HIGH/CRITICAL actions |
| 6 | Subagent isolation | Read-only/metadata subagent contracts and permission ceilings | Subagent write permissions by default |
| 7 | Sandbox backend abstraction | Metadata-only sandbox backend interface and safe local defaults | Cloud execution with private data |
| 8 | Model switching | Continuity metadata and dry-run routing plans | Silent provider switching or paid/cloud fallback |
| 9 | Long-term memory search | Policy-aware search over approved memory records | Personal memory injection by default |
| 10 | Cross-session continuity | Redacted handoff summaries and recovery hints | Background persistence or secret/session dumps |

## Release Gate Requirements

Before any safe-autonomy surface can be marked tested or hardened, it needs:

- Unit tests for safe and denied paths.
- Command registry rows for any CLI surface.
- Feature registry and maturity updates.
- Audit evidence for metadata writes, denials, and previews.
- Policy tests showing no ToolBroker/PolicyEngine bypass.
- Approval tests for any HIGH or CRITICAL future action.
- Docs explaining setup, limitations, and what remains unavailable.

## Current State

HERMES-01 creates architecture and policy docs only. It does not add runtime channel connections, scheduler execution, subagents, sandbox execution, browser automation, background workers, personal-data access, send/write behavior, or cloud execution.
