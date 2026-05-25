# Apple Messages For Business Strategy

Status: accepted for planning

Date: 2026-05-23

## Context

Lead response is a business workflow, not just a personal messaging workflow. Consumer iMessage does not currently provide a safe general first-class inbox/send path for this project. Apple Messages for Business is the preferred long-term direction for business lead response because it is designed around explicit business channels, Apple/business/provider setup, provider configuration, and auditable operational workflows.

This strategy record is paired with the local stub decision in `docs/decisions/apple_messages_for_business_provider.md`. The current implementation creates only a mock/local provider surface; it does not poll a live channel, send a message, load real credentials, or store lead data outside the approved workspace.

## Decision

Business lead response should prefer a future Apple Messages for Business provider strategy over consumer iMessage automation. The provider should integrate through LeadInbox, Action Center, ToolBroker, PolicyEngine, ApprovalManager, and AuditLogger.

Apple Messages for Business is the better fit for API/webhook-style lead workflows. It must still remain approval-gated unless a future auto-response policy is explicitly designed, reviewed, tested, approved, and release-gated.

## Provider Strategy

- Use a future official, configured business messaging provider path.
- Require Apple/business/provider setup before any live provider is enabled.
- Prefer provider/API/webhook-style lead intake over consumer Messages automation.
- Ingest only scoped lead metadata and selected message content.
- Normalize inbound leads into LeadInbox records.
- Keep body content behind selected reads where feasible.
- Draft responses before any send.
- Use Action Center for pending response actions.
- Keep sends CRITICAL and per-action approved in initial phases.
- Keep approval reuse disabled for all CRITICAL sends.
- Rate-limit, audit, and redact all provider interactions.

## Current Stub Status

The v1 provider stub adds:

- `python smart_agent.py apple-business doctor`
- `python smart_agent.py apple-business status`
- `python smart_agent.py apple-business mock-inbound`
- `python smart_agent.py apple-business draft-response <lead_id>`

`mock-inbound` writes a local Lead Inbox record under `./workspace/leads/apple_business/` with `UNTRUSTED_MESSAGE` trust. `draft-response` creates a local `MessageDraft` with `channel=apple_messages_for_business`. No live provider API call, send action creation, send execution, personal iMessage automation, private Messages database read, Full Disk Access request, or memory write is added.

## Rollout Fit

| Rollout level | Apple Messages for Business behavior |
|---|---|
| Level 0 | Summarize selected business lead records only. |
| Level 1 | Draft response for selected lead. |
| Level 2 | Create pending Action Center items for response, follow-up task, or meeting suggestion. |
| Level 3 | Send only after explicit per-action approval. |
| Level 4 | Narrow template-based auto-send only after a future policy decision. |
| Level 5 | Autonomous lead handling remains deferred. |

## Risks

- Incorrect or premature lead response.
- Sending to the wrong customer or channel.
- Prompt injection in inbound lead text.
- Storing lead content in memory or reports.
- Provider misconfiguration or broad channel scope.
- Treating business messaging provider availability as permission to auto-send.
- Assuming provider configuration alone grants permission to read every lead or send every response.

## Required Future Work

- Provider setup decision record.
- Credential and secret doctor.
- LeadInbox adapter tests.
- Mock provider before live provider.
- Action Center send approval tests.
- Redacted audit, bug, and session-log handling.
- Live provider validation only with explicit user approval.
- Separate auto-response policy design before any template-based automatic send behavior.
