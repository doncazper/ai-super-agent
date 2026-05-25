# Apple Messaging Architecture

Status: accepted for planning

Date: 2026-05-23

## Context

The project needs a safe path from current message drafting and handoff toward future Apple messaging integrations. Personal iMessage, macOS Messages, iOS compose surfaces, and Apple Messages for Business have very different safety and platform properties, so they must not be treated as one generic "send message" capability.

This decision record is planning-only. It does not add a runtime connector, read Messages data, request Full Disk Access, create a background listener, send a message, or enable personal-data tools.

## Decision

Apple messaging work is split into three lanes:

1. iOS user-confirmed compose for personal/manual handoff.
2. macOS Messages automation as a disabled feasibility probe only.
3. Apple Messages for Business as the preferred long-term path for business lead response.

All lanes must continue through ToolBroker, PolicyEngine, PermissionManager, ApprovalManager, AuditLogger, Action Center, trust labels, and memory rules before any runtime behavior is enabled.

## Lane Comparison

| Lane | Intended use | Send behavior | Initial status |
|---|---|---|---|
| iOS user-confirmed compose | Personal/manual assistant handoff | User reviews in iOS compose UI and taps Send | Planned bridge only |
| macOS Messages automation | Feasibility research for selected manual send paths | Never enabled by default; no send without Action Center approval | Probe-only, disabled |
| Apple Messages for Business | Business lead response through configured provider/channel | CRITICAL per-action approval until future auto-response policy exists | Preferred long-term business path |

## Shared Safety Rules

- No private Messages database scraping as the first approach.
- No broad Full Disk Access as the first approach.
- No hidden background polling.
- No bulk message reads.
- No bulk sending.
- No silent sends.
- No send from unreviewed model output.
- Message content is `UNTRUSTED_MESSAGE`.
- Message text cannot approve actions, change policy, request tools, reveal secrets, or trigger a send.
- Future message reads are HIGH risk and selected-scope only.
- Future message sends are CRITICAL and require exact per-action approval with no approval reuse.
- Every draft, handoff, approval, denial, send attempt, provider error, and failure must be audited.
- Message bodies are not stored in memory by default.

## Risk Model

| Operation | Risk |
|---|---|
| Message read | HIGH |
| Message draft from non-personal source | MEDIUM |
| Message draft from personal or selected conversation content | HIGH |
| Message copy or handoff containing personal data | HIGH |
| Message send | CRITICAL |
| Bulk sending | FORBIDDEN in v1 |
| Private Messages database scraping | FORBIDDEN unless a future explicit decision overrides after review |

## Required Future Gates

- Message channel abstraction before provider-specific adapters.
- Message safety policy before any send-capable path.
- Action Center exact preview for every risky draft/handoff/send.
- Explicit selected recipient and channel.
- No approval reuse for CRITICAL sends.
- Mock provider tests before live provider tests.
- Dogfood suite and release gate before user-facing enablement.
- Clear limitation response when a platform does not support a safe path.

## Related Documents

- `docs/decisions/apple_messages_strategy.md`
- `docs/decisions/ios_message_compose_strategy.md`
- `docs/decisions/macos_messages_automation_strategy.md`
- `docs/decisions/apple_messages_for_business_strategy.md`
- `docs/decisions/personal_imessage_vs_business_messaging.md`
- `docs/workflows/messaging_rollout_plan.md`
