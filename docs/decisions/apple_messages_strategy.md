# Apple Messages Strategy

Status: accepted for planning

Date: 2026-05-23

## Context

The project has a safe Messages draft and handoff workflow, but it does not have a safe general-purpose consumer iMessage inbox or send API. Personal Messages data is sensitive, local, and easily over-scoped. Sending a text or iMessage can be irreversible and socially consequential.

This record is planning-only and does not implement a connector, read Messages data, copy message history, or send messages.

## Decision

Consumer Messages/iMessage support starts with manual selected text, workspace-bounded context files, draft generation, save-draft, and copy-draft handoff. Automatic sending remains deferred.

## Rejected First Approaches

- Reading `~/Library/Messages/chat.db`.
- Requiring broad Full Disk Access.
- Scraping private Messages app databases.
- Silent or background message reads.
- AppleScript or Accessibility automation for automatic sends.
- Broad chat-history search.
- Contact harvesting from message history.
- Treating incoming message text as trusted instructions.

## Approved V1 Pattern

1. User intentionally provides selected text or a workspace context file.
2. The content is labeled `UNTRUSTED_MESSAGE`.
3. The agent summarizes or drafts a response without sending.
4. Save/copy handoff actions go through Action Center when personal data is present.
5. The user manually reviews and sends outside the agent.

## Future Exploration

Any future personal iMessage bridge must be separately approved and should prefer user-confirmed compose or handoff flows over automation. A future feasibility probe may investigate whether a permissioned compose surface exists, but it must not scrape databases, require Full Disk Access, or send automatically.

The iOS user-confirmed compose path means the user reviews the message in the iOS compose UI and taps Send. It is not silent background sending. macOS Messages automation remains a separate disabled feasibility probe because it requires explicit macOS Automation permission, can be brittle across macOS versions, and must never send without Action Center approval.

## Safety Requirements For Any Future Send

- Capability is CRITICAL.
- Disabled by default.
- Exact message preview required.
- Per-action approval only, with no reuse.
- No background sends.
- No bulk sends.
- No send from unreviewed model output.
- No content-supplied approval from `UNTRUSTED_MESSAGE`.
- Full audit lifecycle.

## Current Limitation

There is no approved general consumer iMessage send path in this project. The safe current path is draft and handoff only.

## Related Documents

- `docs/decisions/apple_messaging_architecture.md`
- `docs/decisions/ios_message_compose_strategy.md`
- `docs/decisions/macos_messages_automation_strategy.md`
- `docs/decisions/personal_imessage_vs_business_messaging.md`
- `docs/workflows/messaging_rollout_plan.md`
