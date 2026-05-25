# Personal iMessage vs Business Messaging

Status: accepted for planning

Date: 2026-05-23

## Context

Personal iMessage and business messaging solve different problems. Personal iMessage is user-owned, socially sensitive, and does not currently expose a safe general inbox/send API for this project. Business messaging is operational, channel-configured, and better suited to lead response workflows when implemented through an approved provider.

This record is planning-only. It does not implement a connector, provider, send path, inbox reader, or lead adapter.

## Decision

Use personal iMessage only for manual, user-confirmed handoff patterns unless a future explicit decision approves a safer path. Use Apple Messages for Business as the preferred long-term direction for business lead response.

## Comparison

| Dimension | Personal iMessage | Apple Messages for Business |
|---|---|---|
| Primary use | Personal/manual communication | Business lead and customer workflows |
| Safe first step | Draft/handoff or iOS user-confirmed compose | Provider strategy and LeadInbox adapter |
| Inbox access | No general safe first-class path in this project | Future provider/webhook-style source |
| Send path | Deferred; user-confirmed compose preferred | Future approved provider send |
| Automation risk | High social/privacy risk | High operational risk, but more auditable |
| Default state | Disabled | Not implemented |
| Approval model | HIGH for reads/handoff, CRITICAL for sends | HIGH for reads, CRITICAL for sends |

## Personal iMessage Boundaries

- Manual selected text and workspace context files are acceptable inputs.
- Draft and handoff are acceptable outputs.
- Native user-confirmed compose is the preferred personal-send exploration path.
- Private database reads, broad history reads, Full Disk Access, and silent sends are rejected first approaches.

## Business Messaging Boundaries

- LeadInbox is the channel-neutral abstraction.
- Apple Messages for Business should be explored through official business/provider setup.
- Provider adapters must not imply permission to auto-send.
- Drafting, follow-up task suggestions, and scheduling suggestions precede send enablement.
- Sends remain CRITICAL until a future explicit auto-response policy is designed, tested, approved, and release-gated.

## Rollout Preference

1. Keep existing messages draft/handoff workflow safe.
2. Add message channel abstraction.
3. Specify message safety policy.
4. Add LeadInbox abstraction.
5. Explore iOS user-confirmed compose for personal handoff.
6. Probe macOS Messages automation only if explicitly approved.
7. Build Apple Messages for Business strategy/provider mock for business leads.
8. Add approved lead response send only after provider and Action Center gates pass.

## Decision Outcome

Consumer iMessage is not the business lead automation foundation. Personal messaging remains manual/user-confirmed first, while business lead response should move toward LeadInbox plus an official business messaging provider path.
