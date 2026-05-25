# Messaging Rollout Plan

Status: specified

Date: 2026-05-23

## Goal

Define the ordered Apple Ecosystem + Messaging track from safe drafting to possible approved sends without enabling runtime message sending, private database access, or broad personal-data access.

## Track Order

| Order | Task | Status | Gate |
|---:|---|---|---|
| 1 | Message channel abstraction | planned | Metadata/interfaces only; no sends |
| 2 | Message safety policy | specified | Risk model, approval gates, and forbidden behaviors documented |
| 3 | Lead Inbox abstraction | specified | Existing LeadInbox decision record; no runtime store yet |
| 4 | iOS user-confirmed compose bridge | planned | User taps Send; no silent background send |
| 5 | macOS Messages automation probe | planned | Feasibility only; explicit permission; no real send |
| 6 | Draft/handoff workflow | complete for v1, hardening planned | Manual selected text/workspace fallback; Action Center for risky handoff |
| 7 | Incoming message strategy | planned | No hidden polling or broad inbox reads |
| 8 | macOS approved iMessage send adapter | blocked | Requires future explicit decision, probe, and approval gate |
| 9 | Apple Messages for Business connector | planned | Preferred business path; provider/mock first |
| 10 | Lead response drafting | specified | Draft-only |
| 11 | Approved lead response send | blocked | CRITICAL per-action approval; no reuse |
| 12 | Messaging dogfood suite | planned | No live sends by default |
| 13 | Messaging release gate | planned | Full tests, policy, manifest, approval, audit, and redaction checks |

## Safety Invariants

- No runtime message sending in this planning track.
- No private Messages database access.
- No broad Full Disk Access dependency.
- No background listener.
- No bulk sending.
- No sends to non-allowlisted recipients in tests.
- Message reads are HIGH risk and selected-scope.
- Message sends are CRITICAL and exact per-action only.
- Bulk sending is FORBIDDEN in v1.
- Private database scraping is FORBIDDEN unless a future explicit decision overrides after review.

## Stop Conditions

Stop implementation work and return a limitation if:

- The platform cannot provide selected-scope access.
- A send path requires silent automation.
- Automation requires broad Full Disk Access.
- A provider would require unreviewed scripts or opaque binaries.
- A workflow needs bulk sending or broad inbox ingestion.
- Approval, audit, or exact preview cannot be preserved.

## Next Recommended Prompt

`MESSAGE-CHANNEL-ABSTRACTION`: build the channel abstraction as metadata/interfaces only, with no runtime sends, no private data reads, no provider credentials, and no hidden polling.
